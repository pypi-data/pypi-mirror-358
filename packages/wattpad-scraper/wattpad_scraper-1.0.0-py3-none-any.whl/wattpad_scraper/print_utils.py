# print_utils.py
from colorama import Fore, Style, init
init(autoreset=True)

EMOJIS = {
    'start': '🚀',
    'success': '✅',
    'fail': '❌',
    'info': 'ℹ️',
    'step': '🔹',
    'book': '📚',
    'write': '✍️',
    'done': '🏁',
    'file': '📄',
    'folder': '📁',
    'sparkle': '✨',
}

def print_step(message):
    print(f"{Fore.CYAN}{EMOJIS['step']} {message}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}{EMOJIS['success']} {message}{Style.RESET_ALL}")

def print_fail(message):
    print(f"{Fore.RED}{EMOJIS['fail']} {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.YELLOW}{EMOJIS['info']} {message}{Style.RESET_ALL}")

def print_book(message):
    print(f"{Fore.MAGENTA}{EMOJIS['book']} {message}{Style.RESET_ALL}")

def print_write(message):
    print(f"{Fore.BLUE}{EMOJIS['write']} {message}{Style.RESET_ALL}")

def print_done(message):
    print(f"{Fore.GREEN}{EMOJIS['done']} {message}{Style.RESET_ALL}")
