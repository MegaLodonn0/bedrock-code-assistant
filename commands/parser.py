"""Command parser for slash-prefixed commands"""

from typing import Tuple, Optional


class SlashCommandParser:
    """Parse and handle slash-prefixed commands"""
    
    SLASH_COMMANDS = {
        'ask': 'Ask AI a question',
        'analyze': 'Analyze code or files',
        'exec': 'Execute shell command',
        'models': 'Select and list models',
        'select': 'Interactive model selection',
        'help': 'Show help information',
        'usage': 'Show API usage limits',
        'history': 'Show conversation history',
        'exit': 'Exit the assistant',
    }
    
    @staticmethod
    def is_slash_command(text: str) -> bool:
        """Check if text starts with slash command"""
        return text.strip().startswith('/')
    
    @staticmethod
    def parse_command(text: str) -> Tuple[str, str]:
        """
        Parse slash command and arguments.
        
        Args:
            text: Input text (e.g., "/ask What is Python?")
        
        Returns:
            Tuple of (command, arguments)
        """
        text = text.strip()
        
        if not text.startswith('/'):
            return 'default', text
        
        # Remove leading slash
        text = text[1:]
        
        # Split command and arguments
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        arguments = parts[1] if len(parts) > 1 else ''
        
        return command, arguments
    
    @staticmethod
    def validate_command(command: str) -> bool:
        """Check if command is valid"""
        return command in SlashCommandParser.SLASH_COMMANDS or command == 'default'
    
    @staticmethod
    def get_help_text() -> str:
        """Get help text for all commands"""
        help_text = "Available Commands:\n"
        
        for cmd, desc in SlashCommandParser.SLASH_COMMANDS.items():
            help_text += f"  /{cmd:<15} - {desc}\n"
        
        return help_text


class CommandRegistry:
    """Registry for slash commands"""
    
    def __init__(self):
        """Initialize command registry"""
        self.handlers = {}
    
    def register(self, command: str, handler):
        """Register a command handler"""
        self.handlers[command] = handler
    
    def handle(self, command: str, arguments: str):
        """Handle a command"""
        if command in self.handlers:
            return self.handlers[command](arguments)
        else:
            from utils.output import print_error
            print_error(f"Unknown command: /{command}")
            return None
    
    def list_commands(self):
        """List all registered commands"""
        return list(self.handlers.keys())
