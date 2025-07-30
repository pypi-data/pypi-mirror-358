import requests
from .core.epub_exporter import export_to_epub
from .core.extractor import extract_book_info, recursively_extract_chapter_content
from wattpad_scraper.print_utils import print_step, print_success, print_fail, print_info, print_book, print_done

def get_book(id: int) -> dict:
    print_step(f"Fetching Wattpad book with ID: {id}")
    url: str = f"https://www.wattpad.com/story/{id}?language=5" # Language 5 is English
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    })

    if response.status_code != 200:
        print_fail(f"Failed to fetch book with ID {id}: {response.status_code}")
        raise Exception(f"Failed to fetch book with ID {id}: {response.status_code}")
    
    print_success(f"Fetched book page for ID {id}")
    return response.content

def run(book_id: int):
    print_book(f"Let's scrape and export book ID: {book_id}!")
    book_data = extract_book_info(get_book(book_id))
    print_info(f"Extracted book info: '{book_data.get('title', 'Unknown')}' by {book_data.get('author', 'Unknown')}")
    print_step("Extracting chapters...")
    chapters = recursively_extract_chapter_content(book_data)
    print_success(f"Extracted {len(chapters)} chapters!")
    book_data['chapters'] = chapters
    export_to_epub(book_data, "output/book.epub")
    print_done(f"Book '{book_data['title']}' by {book_data['author']} has been exported to 'output/book.epub'.")
