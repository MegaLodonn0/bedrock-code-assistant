"""Cross-platform keyboard input handler with arrow key support"""

import sys
import os
from typing import Optional

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False
    import termios
    import tty


class KeyboardInput:
    """Handle keyboard input with arrow key support (cross-platform)"""
    
    # Key codes
    UP_ARROW = 'up'
    DOWN_ARROW = 'down'
    ENTER = 'enter'
    TAB = 'tab'
    ESC = 'esc'
    
    @staticmethod
    def get_key() -> Optional[str]:
        """
        Get single key press (cross-platform)
        
        Returns:
            Key type: 'up', 'down', 'enter', 'tab', 'esc', or character
        """
        if WINDOWS:
            return KeyboardInput._get_key_windows()
        else:
            return KeyboardInput._get_key_unix()
    
    @staticmethod
    def _get_key_windows() -> Optional[str]:
        """Get key on Windows using msvcrt - blocking call"""
        try:
            ch = msvcrt.getch()
            
            # Handle escape sequences (arrow keys)
            if ch == b'\xe0':  # Extended key
                ch2 = msvcrt.getch()
                if ch2 == b'H':  # Up arrow
                    return KeyboardInput.UP_ARROW
                elif ch2 == b'P':  # Down arrow
                    return KeyboardInput.DOWN_ARROW
                elif ch2 == b'K':  # Left arrow
                    return 'left'
                elif ch2 == b'M':  # Right arrow
                    return 'right'
                elif ch2 == b'G':  # Home
                    return 'home'
                elif ch2 == b'O':  # End
                    return 'end'
            
            # Handle regular keys
            elif ch == b'\r':  # Enter
                return KeyboardInput.ENTER
            elif ch == b'\t':  # Tab
                return KeyboardInput.TAB
            elif ch == b'\x1b':  # Escape
                return KeyboardInput.ESC
            elif ch == b'\x03':  # Ctrl+C
                return 'ctrl_c'
            else:
                try:
                    return ch.decode('utf-8')
                except:
                    return ch.decode('latin-1')
        except Exception as e:
            return None
    
    @staticmethod
    def _get_key_unix() -> Optional[str]:
        """Get key on Unix (Linux/Mac) using termios"""
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                
                # Handle escape sequences (arrow keys)
                if ch == '\x1b':
                    # Read next characters
                    seq = sys.stdin.read(2)
                    if seq == '[A':
                        return KeyboardInput.UP_ARROW
                    elif seq == '[B':
                        return KeyboardInput.DOWN_ARROW
                    elif seq == '[C':
                        return 'right'
                    elif seq == '[D':
                        return 'left'
                    else:
                        return KeyboardInput.ESC
                
                # Handle regular keys
                if ch == '\r' or ch == '\n':
                    return KeyboardInput.ENTER
                elif ch == '\t':
                    return KeyboardInput.TAB
                else:
                    return ch
            
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        except Exception:
            pass
        
        return None


class NavigationMenu:
    """Interactive menu with arrow key navigation"""
    
    def __init__(self, items: list, title: str = ""):
        """
        Initialize navigation menu
        
        Args:
            items: List of items to display
            title: Optional title
        """
        self.items = items
        self.title = title
        self.selected_index = 0
    
    def display(self) -> int:
        """
        Display menu and handle navigation with arrow keys
        
        Returns:
            Index of selected item (-1 if cancelled)
        """
        from utils.output import Colors
        
        while True:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Show title
            if self.title:
                print(f"\n{Colors.BOLD}{Colors.CYAN}{self.title}{Colors.END}\n")
            
            # Show items with selection indicator
            for i, item in enumerate(self.items):
                if i == self.selected_index:
                    # Highlight selected item
                    print(f"{Colors.GREEN}→ {item}{Colors.END}")
                else:
                    print(f"  {item}")
            
            print(f"\n{Colors.YELLOW}Use ↑/↓ arrows to navigate, Enter to select, ESC to cancel{Colors.END}")
            
            try:
                # Get key input (blocking)
                key = KeyboardInput.get_key()
                
                if key == KeyboardInput.UP_ARROW:
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                
                elif key == KeyboardInput.DOWN_ARROW:
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                
                elif key == KeyboardInput.ENTER:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return self.selected_index
                
                elif key == KeyboardInput.ESC or key == 'ctrl_c':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return -1  # Cancel
            
            except KeyboardInterrupt:
                os.system('cls' if os.name == 'nt' else 'clear')
                return -1


class InteractiveInput:
    """Handle character-by-character input for real-time features"""
    
    @staticmethod
    def get_line_with_callback(prompt: str = "", on_char_callback=None) -> str:
        """
        Get input line with character callbacks for real-time features (e.g., suggestions)
        
        Args:
            prompt: Prompt to display
            on_char_callback: Callback function(typed_so_far, tab_pressed) called after each character
            
        Returns:
            Full input line or empty string if cancelled
        """
        if prompt:
            sys.stdout.write(prompt)
            sys.stdout.flush()
        
        typed = ""
        
        while True:
            key = KeyboardInput.get_key()
            
            if key == KeyboardInput.ENTER:
                print()  # New line
                return typed
            
            elif key == KeyboardInput.TAB:
                # Tab - call callback with tab flag
                if on_char_callback:
                    result = on_char_callback(typed, tab_pressed=True)
                    if result and result != typed:
                        # Auto-complete with result
                        typed = result
                        # Redraw line
                        sys.stdout.write(f"\r{prompt}{typed}")
                        sys.stdout.flush()
            
            elif key == 'backspace' or key == '\x08' or key == '\x7f':
                # Backspace
                if typed:
                    typed = typed[:-1]
                    sys.stdout.write('\b \b')  # Erase character
                    sys.stdout.flush()
            
            elif key and len(key) == 1 and key.isprintable():
                # Regular character
                typed += key
                sys.stdout.write(key)
                sys.stdout.flush()
                
                # Call callback for real-time suggestions
                if on_char_callback:
                    on_char_callback(typed, tab_pressed=False)
            
            elif key == KeyboardInput.ESC or key == 'ctrl_c':
                print()
                return ""
