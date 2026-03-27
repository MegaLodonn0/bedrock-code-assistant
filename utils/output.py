"""Output formatting and display utilities"""

import sys
from typing import Optional


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a header with formatting"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_section(title: str, content: str = None):
    """Print a formatted section"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * len(title)}{Colors.END}")
    if content:
        print(content)


def print_success(text: str, checkmark: bool = False):
    """Print success message"""
    marker = "✅" if checkmark else "[OK]"
    print(f"{Colors.GREEN}{marker} {text}{Colors.END}")


def print_checkmark(text: str):
    """Print message with checkmark"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_check(text: str):
    """Print message with simple checkmark"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}", file=sys.stderr)


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")


def print_code_block(code: str, language: str = ""):
    """Print a code block with formatting"""
    print(f"\n{Colors.BOLD}Code:{Colors.END}")
    print(f"{Colors.YELLOW}```{language}{Colors.END}")
    print(code)
    print(f"{Colors.YELLOW}```{Colors.END}\n")


def print_response(title: str, content: str, model: str = ""):
    """Print a formatted response"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}{title}{Colors.END}")
    if model:
        print(f"{Colors.CYAN}Model: {model}{Colors.END}")
    print(f"{Colors.GREEN}{'-' * 70}{Colors.END}")
    print(content)
    print(f"{Colors.GREEN}{'-' * 70}{Colors.END}\n")


def print_models(models: list):
    """Print available models in a formatted way"""
    print_header("Available Bedrock Models")
    print(f"Total models: {len(models)}\n")
    
    for i, model in enumerate(models, 1):
        model_id = model.get('modelId', 'N/A')
        model_name = model.get('modelName', 'N/A')
        provider = model.get('providerName', 'N/A')
        
        print(f"{Colors.BOLD}{i}. {model_id}{Colors.END}")
        print(f"   {Colors.CYAN}Name: {model_name}{Colors.END}")
        print(f"   {Colors.CYAN}Provider: {provider}{Colors.END}\n")


def print_table(headers: list, rows: list):
    """Print a simple table"""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(f"\n{Colors.BOLD}{Colors.CYAN}{header_line}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * len(header_line)}{Colors.END}")
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(row_line)
    print()
