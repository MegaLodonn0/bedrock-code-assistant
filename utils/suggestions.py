"""Smart autocomplete suggestions for interactive input"""

import sys
from typing import List, Optional
from utils.output import Colors


class SmartSuggestions:
    """Provide real-time suggestions as user types"""
    
    def __init__(self, options: List[str]):
        """
        Initialize suggestions engine
        
        Args:
            options: List of available options (e.g., commands without /)
        """
        self.options = sorted(options)
    
    @staticmethod
    def get_best_match(typed: str, options: List[str]) -> Optional[str]:
        """
        Get best matching option for typed text
        
        Args:
            typed: Text user typed (without /)
            options: List of available options
            
        Returns:
            Best matching option or None
        """
        typed_lower = typed.lower()
        
        # Exact match
        for opt in options:
            if opt.lower() == typed_lower:
                return opt
        
        # Prefix match (prioritize by position)
        matches = []
        for opt in options:
            if opt.lower().startswith(typed_lower):
                matches.append(opt)
        
        if matches:
            # Return the shortest match (most specific)
            return min(matches, key=len)
        
        return None
    
    @staticmethod
    def get_all_matches(typed: str, options: List[str]) -> List[str]:
        """
        Get all matching options for typed text
        
        Args:
            typed: Text user typed (without /)
            options: List of available options
            
        Returns:
            List of matching options
        """
        typed_lower = typed.lower()
        matches = []
        
        for opt in options:
            if opt.lower().startswith(typed_lower):
                matches.append(opt)
        
        return sorted(matches)
    
    @staticmethod
    def display_suggestions(typed: str, options: List[str]):
        """
        Display suggestions inline while typing
        
        Args:
            typed: Text user typed
            options: List of available options
        """
        if not typed:
            return
        
        matches = SmartSuggestions.get_all_matches(typed, options)
        
        if not matches:
            return
        
        # Show best match as suggestion
        best = SmartSuggestions.get_best_match(typed, options)
        if best:
            # Show remaining part of best match in dim color
            remaining = best[len(typed):]
            sys.stdout.write(f"{Colors.CYAN}{remaining}{Colors.END}")
            sys.stdout.flush()
            
            # Move cursor back
            for _ in range(len(remaining)):
                sys.stdout.write('\b')
            sys.stdout.flush()


class InteractiveCommandInput:
    """Handle interactive command input with real-time suggestions"""
    
    def __init__(self, commands: List[str]):
        """
        Initialize command input handler
        
        Args:
            commands: List of available commands (without /)
        """
        self.commands = commands
        self.suggestions = SmartSuggestions(commands)
    
    def prompt_with_suggestions(self) -> str:
        """
        Prompt user with real-time command suggestions
        
        Returns:
            Full command typed by user (e.g., "/ask what is python")
        """
        from utils.output import Colors
        from utils.keyboard import InteractiveInput
        
        def on_char(typed: str, tab_pressed: bool = False) -> Optional[str]:
            """Callback for each character typed"""
            if not typed.startswith('/'):
                return None
            
            # Remove the / for matching
            cmd_part = typed[1:]
            
            if tab_pressed:
                # Tab pressed - return the best match
                best = self.suggestions.get_best_match(cmd_part, self.commands)
                if best:
                    return '/' + best
                return typed
            
            # Just typed a character - show suggestions
            best = self.suggestions.get_best_match(cmd_part, self.commands)
            all_matches = self.suggestions.get_all_matches(cmd_part, self.commands)
            
            if best:
                # Show the best match as a dim suggestion inline
                sys.stdout.write(f"{Colors.CYAN}{best[len(cmd_part):]}{Colors.END}")
                sys.stdout.flush()
                # Move cursor back to typed position
                for _ in range(len(best) - len(cmd_part)):
                    sys.stdout.write('\b')
                sys.stdout.flush()
            
            return None
        
        print(f"{Colors.BOLD}{Colors.GREEN}>> {Colors.END}", end="", flush=True)
        try:
            full_input = InteractiveInput.get_line_with_callback(
                prompt="",
                on_char_callback=on_char
            )
            return full_input
        except Exception as e:
            print(f"{Colors.END}", flush=True)
            return ""
    
    @staticmethod
    def show_suggestion_help():
        """Show help text for suggestions"""
        print()
        print(f"{Colors.CYAN}💡 Tip: Start with / for commands, use Tab for autocomplete{Colors.END}")
        print(f"{Colors.CYAN}   Examples: /ask, /read, /analyze, /grep, /save, /load, /compress{Colors.END}")
        print()
