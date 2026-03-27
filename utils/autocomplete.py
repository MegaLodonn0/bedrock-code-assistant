"""Autocomplete functionality for CLI"""

import os
from pathlib import Path
from typing import List

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


class AutoCompleter:
    """Provide autocomplete suggestions for commands and file paths"""
    
    def __init__(self, commands: List[str]):
        """
        Initialize autocompleter
        
        Args:
            commands: List of available commands (e.g., ['ask', 'read', 'analyze'])
        """
        self.commands = commands
        self.current_path = "."
        self._setup_readline()
    
    def _setup_readline(self):
        """Setup readline for tab completion"""
        if not READLINE_AVAILABLE:
            return
        
        try:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete)
        except Exception:
            pass
    
    def complete(self, text: str, state: int) -> str:
        """
        Readline completer function
        
        Args:
            text: Current text being completed
            state: State of completion (0 for first match, 1+ for next matches)
            
        Returns:
            Completion suggestion or None
        """
        options = self.get_completions(text)
        
        if state < len(options):
            return options[state]
        
        return None
    
    def get_completions(self, text: str) -> List[str]:
        """
        Get completion suggestions for text
        
        Args:
            text: Partial text to complete
            
        Returns:
            List of completion suggestions
        """
        if text.startswith('/'):
            # Complete slash commands
            return self._complete_command(text[1:])
        else:
            # Complete file paths
            return self._complete_filepath(text)
    
    def _complete_command(self, partial: str) -> List[str]:
        """
        Complete slash commands
        
        Args:
            partial: Partial command (without leading /)
            
        Returns:
            List of matching commands with / prefix
        """
        matches = []
        partial_lower = partial.lower()
        
        for cmd in self.commands:
            if cmd.startswith(partial_lower):
                matches.append('/' + cmd)
        
        return sorted(matches)
    
    def _complete_filepath(self, partial: str) -> List[str]:
        """
        Complete file paths
        
        Args:
            partial: Partial file path
            
        Returns:
            List of matching file paths
        """
        try:
            # If path contains directory separator, parse it
            if os.sep in partial or '/' in partial:
                # Normalize separators
                partial = partial.replace('/', os.sep)
                dir_path = os.path.dirname(partial)
                prefix = os.path.basename(partial)
            else:
                dir_path = "."
                prefix = partial
            
            # Ensure directory exists
            if not os.path.isdir(dir_path):
                return []
            
            matches = []
            prefix_lower = prefix.lower()
            
            # List files/directories in the directory
            try:
                items = os.listdir(dir_path)
            except PermissionError:
                return []
            
            for item in items:
                # Skip hidden files and __pycache__
                if item.startswith('.') or item == '__pycache__':
                    continue
                
                if item.lower().startswith(prefix_lower):
                    full_path = os.path.join(dir_path, item)
                    
                    # Add separator for directories
                    if os.path.isdir(full_path):
                        matches.append(full_path + os.sep)
                    else:
                        matches.append(full_path)
            
            return sorted(matches)
        
        except Exception:
            return []
    
    @staticmethod
    def enable_autocomplete(commands: List[str]):
        """
        Enable autocomplete globally
        
        Args:
            commands: List of available commands
        """
        if not READLINE_AVAILABLE:
            return
        
        completer = AutoCompleter(commands)
        readline.set_completer(completer.complete)
