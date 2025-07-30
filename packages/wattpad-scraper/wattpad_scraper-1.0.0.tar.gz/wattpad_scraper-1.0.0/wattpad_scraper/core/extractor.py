import bs4
from datetime import datetime, timedelta
import requests
from wattpad_scraper.print_utils import print_step, print_success, print_fail, print_info

def extract_pre_from_html(html_content: str) -> list:
    print_step("Extracting <pre> elements from chapter HTML content...")
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    return soup.select("#sticky-end>.row.part-content>div>div pre") or []

def extract_chapter_content(html_content: str) -> str:
    print_step("Extracting chapter content from HTML...")
    pre_elements = extract_pre_from_html(html_content)
    if not pre_elements:
        print_info("No <pre> elements found in chapter HTML.")
        return ""
    
    content = []
    for pre in pre_elements:
        for p in pre.find_all('p'):
            [x.decompose() for x in p.find_all(class_=True)]  
            [x.decompose() for x in p.select('span:not(:has(img))')]  # Remove spans except those with images
            
            for tag in p.find_all(recursive=True):
                if tag.name == 'img':
                    allowed_attrs = ['src', 'alt']
                    for attr in list(tag.attrs):
                        if attr not in allowed_attrs:
                            del tag[attr]
                else:
                    tag.attrs = {}
            
            p.attrs = {}
            
            if p.find('img') or p.get_text(strip=True):  
                content.append(str(p).strip())
    
    print_success(f"Extracted {len(content)} paragraphs from chapter.")
    return "\n".join(content)

def recursively_extract_chapter_content(object: dict) -> str:
    print_step("Recursively extracting all chapter contents...")
    content = []
    for idx, part in enumerate(object["parts"], 1):
        print_info(f"Fetching chapter {idx}: part ID {part['id']}")
        result = requests.get(f"https://www.wattpad.com/{part['id']}?language=5", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        })
        if result.status_code != 200:
            print_fail(f"Failed to fetch part with ID {part['id']}: {result.status_code}")
            raise Exception(f"Failed to fetch part with ID {part['id']}: {result.status_code}")

        chapter_content = extract_chapter_content(result.text)
        if chapter_content:
            print_success(f"Chapter {idx} content extracted!")
        else:
            print_info(f"No content found for chapter {idx}.")
        content.append({
            'id': part['id'],
            'title': part['title'],
            'content': chapter_content
        })
    print_success(f"All {len(content)} chapters extracted!")
    return content

def extract_parts_from_toc(html_content: str) -> list[dict]:
    soup = bs4.BeautifulSoup(html_content, 'html.parser')

    parts_el: list = soup.find("div", class_="Y26Ib").find_all("li")
    if not parts_el:
        return []

    parts = []
    for part in parts_el:
        parts.append({
            "id": part.find("a")["href"].split("/")[3].split("-")[0],
            "title": part.find("div", class_="wpYp-").get_text(strip=True),
            "date": parse_date(part.find("div", class_="bSGSB").get_text(strip=True))
        })
    
    return parts

def extract_book_info(html_content: str) -> dict:
    """
    Extracts book information from the HTML content.

    Args:
        html_content (str): The HTML content to extract the book info from.

    Returns:
        dict: A dictionary containing the book title and author.
    """
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    title: str = soup.find("div", class_="gF-N5").get_text(strip=True)
    author: str = soup.find("a", class_="SjGa2").get_text(strip=True)
    description: str = soup.find("pre", class_="mpshL").get_text(strip=True).replace("All Rights Reserved", "").strip()
    try:
        cover: str = soup.find("img", class_="cover__BlyZa")["src"]
    except TypeError:
        cover = ""

    stats = soup.select("div.stats-value>div>div>span.sr-only")
    reads: int = int((stats[0].get_text(strip=True) if len(stats) > 0 else "0").replace(",", ""))
    votes: int = int((stats[1].get_text(strip=True) if len(stats) > 1 else "0").replace(",", ""))
    partsint: int = int((stats[2].get_text(strip=True) if len(stats) > 2 else "0").replace(",", ""))
    
    parts = extract_parts_from_toc(html_content)

    return {
        "title": title,
        "cover": cover,
        "author": author,
        "reads": reads,
        "votes": votes,
        "amount_of_parts": partsint,
        "description": description,
        "parts": parts
    }

def parse_date(date_str: str) -> datetime:
    """
    Parse both absolute and relative dates from Wattpad.
    
    Args:
        date_str (str): Date string from Wattpad (e.g. 'Thu, Jun 13, 2024' or 'about 1 hour ago')
        
    Returns:
        datetime: Parsed datetime object
    """
    try:
        # Try parsing absolute date first
        return datetime.strptime(date_str, '%a, %b %d, %Y').replace(tzinfo=None)
    except ValueError:
        # Handle relative dates
        now = datetime.now()
        
        if 'just now' in date_str.lower():
            return now
        
        parts = date_str.lower().split()
        if len(parts) >= 4 and 'ago' in parts:
            amount = int(parts[1])
            unit = parts[2]
            
            if 'second' in unit:
                return now - timedelta(seconds=amount)
            elif 'minute' in unit:
                return now - timedelta(minutes=amount)
            elif 'hour' in unit:
                return now - timedelta(hours=amount)
            elif 'day' in unit:
                return now - timedelta(days=amount)
            elif 'week' in unit:
                return now - timedelta(weeks=amount)
            elif 'month' in unit:
                return now - timedelta(days=amount*30)  # Approximate
            elif 'year' in unit:
                return now - timedelta(days=amount*365)  # Approximate
                
        # If we can't parse it, return current time
        return now