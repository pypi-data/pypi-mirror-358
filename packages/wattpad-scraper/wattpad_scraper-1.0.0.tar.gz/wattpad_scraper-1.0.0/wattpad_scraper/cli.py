import argparse
from .main import run
from wattpad_scraper.print_utils import print_step, print_book, print_done

def main():
    print_book("Welcome to Wattpad Scraper CLI! ✨")
    parser = argparse.ArgumentParser(prog="wattpad-scraper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    epubit_parser = subparsers.add_parser("epubit", help="Export a Wattpad book to EPUB.")
    epubit_parser.add_argument("book_id", type=int, help="The Wattpad book ID.")

    args = parser.parse_args()

    if args.command == "epubit":
        print_step(f"You chose to export book ID: {args.book_id}")
        run(args.book_id)
        print_done("All done! Enjoy your EPUB! 🎉")

if __name__ == "__main__":
    main()
