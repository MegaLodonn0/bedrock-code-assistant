"""Command execution utilities"""

import subprocess
import sys
from typing import Tuple, Optional
from utils.output import print_warning, print_error, print_success, Colors


def ask_confirmation(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        prompt: The prompt to display
        default: Default answer if user just presses Enter
    
    Returns:
        True if user confirms, False otherwise
    """
    yes_no = "(Y/n)" if default else "(y/N)"
    
    while True:
        try:
            sys.stdout.write(f"{Colors.YELLOW}{prompt} {yes_no}: {Colors.END}")
            choice = input().lower().strip()
            
            if choice == '':
                return default
            elif choice in ('y', 'yes'):
                return True
            elif choice in ('n', 'no'):
                return False
            else:
                print_warning("Please enter 'y' or 'n'")
        except KeyboardInterrupt:
            print_error("\nOperation cancelled")
            return False


def execute_command(
    command: str,
    ask_before_execute: bool = True,
    shell: bool = True,
    capture_output: bool = True
) -> Tuple[int, str, str]:
    """
    Execute a shell command.
    
    Args:
        command: The command to execute
        ask_before_execute: Ask for confirmation before executing
        shell: Whether to use shell
        capture_output: Capture stdout and stderr
    
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if ask_before_execute:
        print_warning(f"About to execute: {Colors.BOLD}{command}{Colors.END}")
        if not ask_confirmation("Do you want to continue?"):
            print_error("Command execution cancelled")
            return 1, "", ""
    
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=capture_output,
            text=True,
            timeout=60
        )
        
        return result.returncode, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print_error("Command execution timed out")
        return 124, "", "Timeout"
    except Exception as e:
        print_error(f"Command execution failed: {str(e)}")
        return 1, "", str(e)


def execute_command_safe(
    command: str,
    ask_before_execute: bool = True
) -> Tuple[bool, str]:
    """
    Execute a command safely with error handling.
    
    Args:
        command: The command to execute
        ask_before_execute: Ask for confirmation before executing
    
    Returns:
        Tuple of (success, output)
    """
    return_code, stdout, stderr = execute_command(
        command,
        ask_before_execute=ask_before_execute
    )
    
    if return_code == 0:
        print_success(f"Command executed successfully")
        return True, stdout
    else:
        print_error(f"Command failed with code {return_code}")
        if stderr:
            print_error(f"Error: {stderr}")
        return False, stdout or stderr


def validate_command(command: str) -> bool:
    """
    Validate if a command is safe to execute.
    
    Args:
        command: The command to validate
    
    Returns:
        True if command is safe, False otherwise
    """
    # Basic safety checks
    dangerous_patterns = [
        'rm -rf /',
        'dd if=/dev/',
        'mkfs',
        'fdisk',
        ':(){:|:&'  # Fork bomb
    ]
    
    for pattern in dangerous_patterns:
        if pattern in command:
            print_error(f"Dangerous command pattern detected: {pattern}")
            return False
    
    return True
