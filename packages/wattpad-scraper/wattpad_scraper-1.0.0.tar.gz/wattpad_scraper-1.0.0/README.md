# Wattpad Scraper

This is a CLI tool designed to help you download any Wattpad story into an EPUB file, with metadata and all! This version supports the new Wattpad story format.

New Wattpad story format? What's that you ask? I'm not really sure when it started, but Wattpad updated the HTML structure of their stories, converting class tags into random nonsense (this is due to minimizing), rendering other tools unusable. This tool uses the new format, so it should work with any story on Wattpad.

## Requirements
- Python 3.12
- pip

## Installation
```bash
pip install wattpad-scraper
```

## Usage
```bash
wattpad-scraper epubit replace_this_with_your_book_id
```
The file will be saved to <current directory>/output/book.epub.

## Note
The function docs were written by tabbing on Copilot suggestions so expect them to be... weird. Some other comments were also written by Copilot, so they may have a weird tone. You can clearly see the difference between my comments and Copilot's comments. But the code works, and that's what matters, and who cares about comments anyway? 

## Legal Notice
This tool is for educational purposes only. Please respect Wattpad's terms of service and copyright laws!

## License
MIT License