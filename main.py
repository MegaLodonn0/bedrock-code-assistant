"""CLI - Command Line Interface"""

import argparse
import sys
import os
from pathlib import Path

from config import get_config, ConfigError
from core import BedrockClient
from utils import (
    print_header, print_section, print_success, print_error,
    print_warning, print_info, print_models, print_response,
    execute_command, ask_confirmation, validate_command,
    ProviderScreen, UsageTracker, TableFormatter, Colors
)
from commands.parser import SlashCommandParser, CommandRegistry


class CodeAssistantCLI:
    """Interactive Code Assistant CLI"""
    
    def __init__(self):
        """Initialize CLI and Bedrock client"""
        try:
            self.config = get_config()
            self.bedrock = BedrockClient(self.config)
            self.usage_tracker = UsageTracker(self.bedrock)  # Pass bedrock_client
            self.command_registry = CommandRegistry()
            self._register_commands()
            print_success("Connected to AWS Bedrock")
        except ConfigError as e:
            print_error(str(e))
            sys.exit(1)
        except Exception as e:
            print_error(f"Failed to initialize: {str(e)}")
            sys.exit(1)
    
    def _register_commands(self):
        """Register slash commands"""
        self.command_registry.register('ask', self._cmd_ask)
        self.command_registry.register('analyze', self._cmd_analyze)
        self.command_registry.register('exec', self._cmd_exec)
        self.command_registry.register('models', self._cmd_list_models)
        self.command_registry.register('select', self._cmd_select_model)
        self.command_registry.register('help', self._cmd_help)
        self.command_registry.register('usage', self._cmd_usage)
        self.command_registry.register('exit', self._cmd_exit)
    
    def _cmd_ask(self, args: str):
        """Handle /ask command"""
        if not args:
            print_error("Please provide a question: /ask <question>")
            return
        
        try:
            model_id = self.config.bedrock.get('default_model', 
                                              'anthropic.claude-opus-4-5-20251101-v1:0')
            print_info(f"Asking {model_id}...")
            
            response = self.bedrock.invoke_model(model_id, args)
            print_response("Response:", response, model_id)
            self.usage_tracker.increment_request()
        
        except Exception as e:
            print_error(f"Failed to get response: {str(e)}")
    
    def _cmd_analyze(self, args: str):
        """Handle /analyze command"""
        print_info("Analyze feature coming soon!")
    
    def _cmd_exec(self, args: str):
        """Handle /exec command"""
        if not args:
            print_error("Please provide a command: /exec <command>")
            return
        
        if not validate_command(args):
            return
        
        success, output = execute_command(args, ask_before_execute=True)
        
        if success and output:
            print_section("Command Output:")
            print(output)
    
    def _cmd_list_models(self, args: str):
        """Handle /models command"""
        try:
            models = self.bedrock.list_models()
            
            # Format as table
            table = TableFormatter.format_models_table(models)
            print_section("Available Models:")
            print(table)
        except Exception as e:
            print_error(f"Failed to list models: {str(e)}")
    
    def _cmd_select_model(self, args: str):
        """Handle /select command - full-screen provider selection"""
        try:
            models = self.bedrock.list_models()
            screen = ProviderScreen(models)
            
            # Step 1: Provider selection
            provider, provider_models = screen.show_provider_selection()
            
            # Step 2: Model selection for selected provider
            selected = screen.show_models_for_provider(provider, provider_models)
            
            # Display confirmation
            os.system('cls' if os.name == 'nt' else 'clear')
            print()
            print_success(f"Selected Model:")
            print(f"  {Colors.GREEN}Name: {selected['modelName']}{Colors.END}")
            print(f"  {Colors.GREEN}ID: {selected['modelId']}{Colors.END}")
            print(f"  {Colors.GREEN}Provider: {selected['providerName']}{Colors.END}")
            print()
            input("Press Enter to continue...")
        
        except Exception as e:
            print_error(f"Model selection failed: {str(e)}")
            input("Press Enter to continue...")
    
    def _cmd_help(self, args: str):
        """Handle /help command"""
        help_text = SlashCommandParser.get_help_text()
        print_section("Available Slash Commands:", help_text)
    
    def _cmd_usage(self, args: str):
        """Handle /usage command"""
        self.usage_tracker.display_usage_right_panel()
    
    def _cmd_exit(self, args: str):
        """Handle /exit command"""
        print_success("Goodbye!")
        sys.exit(0)
    
    
    def interactive(self):
        """Start interactive mode"""
        print_header("AWS Bedrock Code Assistant")
        print_info("Type '/help' for commands, '/exit' to quit\n")
        
        while True:
            try:
                user_input = input(f"{Colors.BOLD}{Colors.GREEN}>> {Colors.END}").strip()
                
                if not user_input:
                    continue
                
                # Check for slash command
                if SlashCommandParser.is_slash_command(user_input):
                    command, arguments = SlashCommandParser.parse_command(user_input)
                    
                    if not SlashCommandParser.validate_command(command):
                        print_error(f"Unknown command: /{command}")
                        continue
                    
                    self.command_registry.handle(command, arguments)
                else:
                    # Default: treat as question for AI
                    self._cmd_ask(user_input)
            
            except KeyboardInterrupt:
                print("\n")
                if ask_confirmation("Exit?"):
                    print_success("Goodbye!")
                    break
            except Exception as e:
                print_error(f"Error: {str(e)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AWS Bedrock-powered Code Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Start interactive mode
  %(prog)s ask "What is Python?"     # Ask a question
  %(prog)s select                    # Interactive model selection
  %(prog)s models                    # List all models
  %(prog)s exec "ls -la"             # Execute a command

Slash Commands (in interactive mode):
  /ask <question>    - Ask the AI a question
  /select            - Interactive model selection
  /models            - List available models
  /exec <command>    - Execute a shell command
  /usage             - Show API usage limits
  /help              - Show help information
  /exit              - Exit the assistant
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # ask command
    ask_parser = subparsers.add_parser('ask', help='Ask the AI')
    ask_parser.add_argument('question', help='Question to ask')
    
    # select command
    subparsers.add_parser('select', help='Interactive model selection')
    
    # models command
    subparsers.add_parser('models', help='List available models')
    
    # exec command
    exec_parser = subparsers.add_parser('exec', help='Execute a command')
    exec_parser.add_argument('command', help='Command to execute')
    
    args = parser.parse_args()
    
    cli = CodeAssistantCLI()
    
    if args.command == 'ask':
        class AskArgs:
            question = args.question
        cli._cmd_ask(args.question)
    elif args.command == 'select':
        cli._cmd_select_model('')
    elif args.command == 'models':
        cli._cmd_list_models('')
    elif args.command == 'exec':
        cli._cmd_exec(args.command)
    else:
        # Start interactive mode if no command
        cli.interactive()


if __name__ == '__main__':
    main()
