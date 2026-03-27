"""CLI - Command Line Interface"""

import argparse
import sys
from pathlib import Path

from config import get_config, ConfigError
from core import BedrockClient
from utils import (
    print_header, print_section, print_success, print_error,
    print_warning, print_info, print_models, print_response,
    execute_command, ask_confirmation, validate_command
)


class CodeAssistantCLI:
    """Interactive Code Assistant CLI"""
    
    def __init__(self):
        """Initialize CLI and Bedrock client"""
        try:
            self.config = get_config()
            self.bedrock = BedrockClient(self.config)
            print_success("Connected to AWS Bedrock")
        except ConfigError as e:
            print_error(str(e))
            sys.exit(1)
        except Exception as e:
            print_error(f"Failed to initialize: {str(e)}")
            sys.exit(1)
    
    def cmd_ask(self, args):
        """Ask the AI a question"""
        if not args.question:
            print_error("Question required")
            return
        
        try:
            model = self.config.bedrock.get('default_model', 
                                          'anthropic.claude-opus-4-5-20251101-v1:0')
            print_info(f"Asking {model}...")
            
            response = self.bedrock.invoke_model(model, args.question)
            print_response("Response:", response, model)
        
        except Exception as e:
            print_error(f"Failed to get response: {str(e)}")
    
    def cmd_list_models(self, args):
        """List available models"""
        try:
            models = self.bedrock.list_models()
            print_models(models)
        except Exception as e:
            print_error(f"Failed to list models: {str(e)}")
    
    def cmd_exec(self, args):
        """Execute a shell command"""
        if not args.command:
            print_error("Command required")
            return
        
        if not validate_command(args.command):
            return
        
        success, output = execute_command(
            args.command,
            ask_before_execute=True
        )
        
        if success and output:
            print_section("Command Output:")
            print(output)
    
    def interactive(self):
        """Start interactive mode"""
        print_header("AWS Bedrock Code Assistant")
        print_info("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                elif user_input.lower() == 'exit':
                    print_success("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self._print_help()
                elif user_input.lower().startswith('ask '):
                    question = user_input[4:].strip()
                    if question:
                        class Args:
                            pass
                        args = Args()
                        args.question = question
                        self.cmd_ask(args)
                elif user_input.lower() == 'models':
                    class Args:
                        pass
                    args = Args()
                    self.cmd_list_models(args)
                elif user_input.lower().startswith('exec '):
                    command = user_input[5:].strip()
                    if command:
                        class Args:
                            pass
                        args = Args()
                        args.command = command
                        self.cmd_exec(args)
                else:
                    # Default: ask AI
                    class Args:
                        pass
                    args = Args()
                    args.question = user_input
                    self.cmd_ask(args)
            
            except KeyboardInterrupt:
                print("\n")
                if ask_confirmation("Exit?"):
                    print_success("Goodbye!")
                    break
            except Exception as e:
                print_error(f"Error: {str(e)}")
    
    def _print_help(self):
        """Print help information"""
        help_text = """
Available Commands:
  ask <question>    - Ask the AI a question
  models           - List available Bedrock models
  exec <command>   - Execute a shell command (with confirmation)
  help             - Show this help
  exit             - Exit the assistant
        """
        print_section("Help", help_text.strip())


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AWS Bedrock-powered Code Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         # Start interactive mode
  %(prog)s ask "What is Python?"   # Ask a question
  %(prog)s list-models             # List available models
  %(prog)s exec "ls -la"           # Execute a command
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # ask command
    ask_parser = subparsers.add_parser('ask', help='Ask the AI')
    ask_parser.add_argument('question', help='Question to ask')
    
    # list-models command
    subparsers.add_parser('list-models', help='List available models')
    
    # exec command
    exec_parser = subparsers.add_parser('exec', help='Execute a command')
    exec_parser.add_argument('command', help='Command to execute')
    
    args = parser.parse_args()
    
    cli = CodeAssistantCLI()
    
    if args.command == 'ask':
        cli.cmd_ask(args)
    elif args.command == 'list-models':
        cli.cmd_list_models(args)
    elif args.command == 'exec':
        cli.cmd_exec(args)
    else:
        # Start interactive mode if no command
        cli.interactive()


if __name__ == '__main__':
    main()
