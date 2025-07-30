from ebooklib import epub
import requests
import re
from bs4 import BeautifulSoup
import hashlib
from wattpad_scraper.print_utils import print_step, print_success, print_fail, print_info, print_book, print_write, print_done

def clean_html_content(html_content: str) -> str:
    """Cleans HTML content by removing extra newlines and whitespace"""
    content = re.sub(r'\n\s*\n', '\n', html_content)
    content = re.sub(r'\s+', ' ', content)

    soup = BeautifulSoup(content, 'html.parser')

    for p in soup.find_all('p'):
        has_text = p.get_text(strip=True)
        has_img = p.find('img') is not None
        if not has_text and not has_img:
            p.decompose()

    return str(soup)

def download_and_process_image(img_url: str, book: epub.EpubBook) -> tuple[str, bytes]:
    print_step(f"Downloading image: {img_url}")
    try:
        response = requests.get(img_url)
        if response.status_code != 200:
            print_fail(f"Failed to download image from {img_url}. Status code: {response.status_code}")
            return '', b''
        
        # Generate unique filename based on URL
        file_id = hashlib.md5(img_url.encode()).hexdigest()
        
        content_type = response.headers.get('content-type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            filename = f'Images/image_{file_id}.jpg'  
            media_type = 'image/jpeg'
        elif 'png' in content_type:
            filename = f'Images/image_{file_id}.png' 
            media_type = 'image/png'
        else:
            print_fail(f"Unsupported image type for {img_url}. Content type: {content_type}")
            return '', b''
        
        img = epub.EpubImage(
            uid=f'img_{file_id}',
            file_name=filename,
            media_type=media_type,
            content=response.content
        )
        book.add_item(img)
        
        print_success(f"Image added: {filename}")
        return filename, response.content
    except requests.exceptions.RequestException as e:
        print_fail(f"Exception occurred while downloading image from {img_url}. Error: {e}")
        return '', b''

def export_to_epub(book_data: dict, output_path: str):
    print_book(f"Starting EPUB export for: {book_data.get('title', 'Unknown Title')}")
    book = epub.EpubBook()
    
    # Set metadata using the first chapter's ID as the book ID
    chapter_id = book_data['chapters'][0]['id'] if book_data.get('chapters') else 'unknown'
    book.set_identifier(f'wattpad_{chapter_id}')
    book.set_title(book_data['title'])
    book.set_language('en')
    book.add_author(book_data['author'])
    
    print_info("Setting book metadata...")
    if book_data.get('cover'):
        print_step("Adding cover image...")
        cover_path, cover_content = download_and_process_image(book_data['cover'], book)
        if cover_path:
            book.set_cover("Images/cover.jpg", cover_content)
            print_success("Cover image added!")
        else:
            print_fail("Failed to add cover image.")
    
    # Define CSS first so we can link it to chapters
    print_step("Adding CSS styles...")
    style = '''
        body { margin: 5%; text-align: justify; font-size: 1em; }
        p { text-indent: 1em; margin-top: 0.7em; margin-bottom: 0.7em; }
        h1 { text-align: center; margin-bottom: 1em; }
        img { display: block; margin: 1em auto; max-width: 100%; }
    '''
    css = epub.EpubItem(
        uid="style_default",
        file_name="style/default.css",
        media_type="text/css",
        content=style
    )
    book.add_item(css)
    
    print_step("Adding chapters...")
    chapters = []
    for idx, chapter_data in enumerate(book_data['chapters'], 1):
        print_write(f"Processing chapter {idx}: {chapter_data['title']}")
        chapter = epub.EpubHtml(
            title=chapter_data['title'],
            file_name=f'chapter_{idx:03d}.xhtml',
            lang='en'
        )
        
        chapter.add_item(css)
        
        # Clean content and process images
        content = clean_html_content(chapter_data['content'])
        soup = BeautifulSoup(content, 'html.parser')
        for img in soup.find_all('img'):
            if img.get('src'):
                new_path, _ = download_and_process_image(img['src'], book)
                if new_path:
                    img['src'] = f'{new_path}' 
                    print_success(f"Processed image in chapter {idx}: {img['src']}")
                else:
                    print_fail(f"Failed to process image in chapter {idx}. Removing image.")
                    img.decompose()
        
        chapter.content = str(soup)
        book.add_item(chapter)
        chapters.append(chapter)
    
    print_step("Adding navigation and table of contents...")
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    book.toc = [(epub.Section(book_data['title']), chapters)]
    
    book.spine = ['nav'] + chapters
    
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print_step(f"Writing EPUB file to: {output_path}")
    try:
        epub.write_epub(output_path, book, {'epub3_pages': True})
        print_done(f"EPUB export complete! File saved at: {output_path}")
    except Exception as e:
        print_fail(f"Failed to create epub file at {output_path}. Error: {e}")
        raise OSError(f"Failed to create epub file: {str(e)}") from e
