"""CLI - Command Line Interface"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from config import get_config, ConfigError
from core import BedrockClient
from core.conversation import ConversationManager
from utils import (
    print_header, print_section, print_success, print_error,
    print_warning, print_info, print_models, print_response,
    print_checkmark, print_check,
    execute_command, ask_confirmation, validate_command,
    ProviderScreen, UsageTracker, TableFormatter, Colors, FileReader, AutoCompleter
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
            self.selected_model = None  # Track user-selected model
            self.conversation = ConversationManager()  # Track conversation history
            self._register_commands()
            
            # Setup autocomplete for commands
            AutoCompleter.enable_autocomplete(list(SlashCommandParser.SLASH_COMMANDS.keys()))
            
            print_success("Connected to AWS Bedrock", checkmark=True)
        except ConfigError as e:
            print_error(str(e))
            sys.exit(1)
        except Exception as e:
            print_error(f"Failed to initialize: {str(e)}")
            sys.exit(1)
    
    def _register_commands(self):
        """Register slash commands"""
        self.command_registry.register('ask', self._cmd_ask)
        self.command_registry.register('read', self._cmd_read)
        self.command_registry.register('analyze', self._cmd_analyze)
        self.command_registry.register('grep', self._cmd_grep)
        self.command_registry.register('save', self._cmd_save)
        self.command_registry.register('load', self._cmd_load)
        self.command_registry.register('compress', self._cmd_compress)
        self.command_registry.register('exec', self._cmd_exec)
        self.command_registry.register('map', self._cmd_map)
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
            # Use selected model if available, otherwise use default
            if self.selected_model:
                model_id = self.selected_model['modelId']
                model_name = self.selected_model['modelName']
            else:
                model_id = self.config.bedrock.get('default_model', 
                                                   'anthropic.claude-opus-4-5-20251101-v1:0')
                model_name = "Default"
            
            print_info(f"Asking {model_name} ({model_id})...")
            
            response = self.bedrock.invoke_model(model_id, args)
            print_response("Response:", response, model_id)
            self.usage_tracker.increment_request()
        
        except Exception as e:
            error_msg = str(e)
            
            # Handle on-demand throughput not supported
            if "on-demand throughput" in error_msg.lower() and "supported" in error_msg.lower():
                print_warning("This model requires Provisioned Throughput.")
                print()
                print_info("Solutions:")
                print("  1. Use /select to try another model")
                print("  2. Set up Provisioned Throughput in AWS Console")
                print("     → Bedrock → Provisioned Throughput → Create")
            else:
                print_error(f"Failed to get response: {error_msg}")
    
    def _cmd_read(self, args: str):
        """Handle /read command - read and display file content"""
        if not args:
            print_error("Usage: /read <filepath>")
            return
        
        try:
            success, content = FileReader.read_file(args)
            
            if success:
                print_section(f"File: {args}")
                print(content)
                self.conversation.add_message('user', f"Read file: {args}", "file_reader")
            else:
                print_error(content)
        
        except Exception as e:
            print_error(f"Failed to read file: {str(e)}")
    
    def _cmd_analyze(self, args: str):
        """Handle /analyze command - analyze file with AI"""
        if not args:
            print_error("Usage: /analyze <filepath>")
            return
        
        try:
            success, content = FileReader.read_file(args)
            
            if not success:
                print_error(content)
                return
            
            # Create analysis prompt
            prompt = f"""Analyze the following code/text file and provide insights:

File: {args}

Content:
{content}

Please provide:
1. Summary of what this file does
2. Key findings or observations
3. Potential issues or improvements
4. Overall assessment"""
            
            # Use selected model or default
            if self.selected_model:
                model_id = self.selected_model['modelId']
                model_name = self.selected_model['modelName']
            else:
                model_id = self.config.bedrock.get('default_model', 
                                                   'amazon.nova-micro-v1:0')
                model_name = "Default"
            
            print_info(f"Analyzing with {model_name}...")
            
            response = self.bedrock.invoke_model(model_id, prompt)
            print_response("Analysis:", response, model_id)
            
            self.conversation.add_message('user', f"Analyze file: {args}", "analyze")
            self.conversation.add_message('assistant', response, model_id)
            self.usage_tracker.increment_request()
        
        except Exception as e:
            error_msg = str(e)
            
            if "on-demand throughput" in error_msg.lower() and "supported" in error_msg.lower():
                print_warning("This model requires Provisioned Throughput.")
                print("  Use /select to try another model")
            else:
                print_error(f"Failed to analyze: {error_msg}")
    
    def _cmd_grep(self, args: str):
        """Handle /grep command - search for pattern in files"""
        if not args:
            print_error("Usage: /grep <pattern> [directory]")
            return
        
        try:
            parts = args.split(maxsplit=1)
            pattern = parts[0]
            directory = parts[1] if len(parts) > 1 else "."
            
            success, results = FileReader.grep_pattern(pattern, directory)
            
            if success:
                print_section(f"Search Results for: {pattern}")
                print(results)
                self.conversation.add_message('user', f"Grep pattern: {pattern}", "grep")
            else:
                print_error(results)
        
        except Exception as e:
            print_error(f"Failed to search: {str(e)}")
    
    def _cmd_save(self, args: str):
        """Handle /save command - save conversation to file"""
        if not args:
            print_error("Usage: /save <filename>")
            return
        
        try:
            success, message = self.conversation.save_conversation(args)
            
            if success:
                print_checkmark(message)
            else:
                print_error(message)
        
        except Exception as e:
            print_error(f"Failed to save conversation: {str(e)}")
    
    def _cmd_load(self, args: str):
        """Handle /load command - load conversation from file"""
        if not args:
            print_error("Usage: /load <filename>")
            return
        
        try:
            success, message = self.conversation.load_conversation(args)
            
            if success:
                print_checkmark(message)
                # Display context from loaded conversation
                print_section("Recent Messages:")
                print(self.conversation.get_context(last_n=3))
            else:
                print_error(message)
        
        except Exception as e:
            print_error(f"Failed to load conversation: {str(e)}")
    
    def _cmd_compress(self, args: str):
        """Handle /compress command - compress conversation history"""
        try:
            result = self.conversation.compress_history()
            print_info(result)
        
        except Exception as e:
            print_error(f"Failed to compress: {str(e)}")
    
    def _cmd_map(self, args: str):
        """Handle /map command - create task map and delegate to agents"""
        if not args:
            print_error("Usage: /map <task_description>")
            print_info("Example: /map analyze bedrock integration")
            return
        
        try:
            from core import MapCoordinator
            import json
            
            print_info(f"Creating map for task: {args}")
            
            # Initialize coordinator
            coordinator = MapCoordinator(
                repo_path='.',
                bedrock_client=self.bedrock
            )
            
            # Analyze repo if not already done
            if not coordinator.repo_analyzer.files_analysis:
                print_section("Step 1: Analyzing Repository")
                repo_map = coordinator.analyze_repository()
                print_success(f"✓ Analyzed {repo_map['total_files']} files", checkmark=True)
            
            # Create task map
            print_section("Step 2: Creating Task Map")
            task_map = coordinator.create_task_map(args, max_subtasks=5)
            print_success(f"✓ Created {len(task_map.subtasks)} subtasks", checkmark=True)
            print_info(f"Token compression: {task_map.compression_ratio:.1f}%")
            
            # Show subtasks
            print_section("Subtasks to Execute:")
            for i, subtask in enumerate(task_map.subtasks, 1):
                print(f"  {i}. {subtask['name']}")
                if subtask.get('filepath'):
                    print(f"     File: {subtask['filepath']}")
                print(f"     Type: {subtask['type']}")
            
            # Execute task map
            print_section("Step 3: Executing with Agents")
            results = coordinator.execute_task_map(task_map)
            
            # Display results
            print_section("Execution Results:")
            print_success(f"✓ Status: {results['status']}", checkmark=True)
            print(f"  Agents executed: {results['agents_executed']}")
            print(f"  Successful: {results['agents_successful']}")
            print(f"  Failed: {results['agents_failed']}")
            print()
            print_info("Metrics:")
            print(f"  • Total tokens: {results['metrics']['total_tokens_used']:.0f}")
            print(f"  • Execution time: {results['metrics']['total_execution_time']:.2f}s")
            print(f"  • Token savings: {results['metrics']['token_savings']}")
            
            # Cleanup
            coordinator.cleanup()
        
        except ImportError:
            print_error("Map system not available (MapCoordinator not found)")
        except Exception as e:
            print_error(f"Failed to create map: {str(e)}")
    
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
        """Handle /models command - full-screen provider selection with usage limits"""
        try:
            models = self.bedrock.list_models()
            screen = ProviderScreen(models)
            
            # Step 1: Provider selection
            provider, provider_models = screen.show_provider_selection()
            
            # Check if user cancelled
            if provider is None or provider_models is None:
                print_info("Model selection cancelled")
                return
            
            # Step 2: Model selection for selected provider
            selected = screen.show_models_for_provider(provider, provider_models)
            
            # Check if user cancelled
            if selected is None:
                print_info("Model selection cancelled")
                return
            
            # Display confirmation with usage limits and checkmark
            os.system('cls' if os.name == 'nt' else 'clear')
            print()
            print_checkmark("Model Information:")
            print(f"  {Colors.GREEN}Name: {selected['modelName']}{Colors.END}")
            print(f"  {Colors.GREEN}ID: {selected['modelId']}{Colors.END}")
            print(f"  {Colors.GREEN}Provider: {selected['providerName']}{Colors.END}")
            print()
            
            # Display usage limits
            self.usage_tracker.display_usage_right_panel(os.get_terminal_size().columns)
            print()
            
            input("Press Enter to continue...")
        
        except Exception as e:
            print_error(f"Failed to list models: {str(e)}")
    
    def _cmd_select_model(self, args: str):
        """Handle /select command - full-screen provider selection"""
        try:
            models = self.bedrock.list_models()
            screen = ProviderScreen(models)
            
            # Step 1: Provider selection
            provider, provider_models = screen.show_provider_selection()
            
            # Check if user cancelled
            if provider is None or provider_models is None:
                print_info("Model selection cancelled")
                return
            
            # Step 2: Model selection for selected provider
            selected = screen.show_models_for_provider(provider, provider_models)
            
            # Check if user cancelled
            if selected is None:
                print_info("Model selection cancelled")
                return
            
            # Save selected model
            self.selected_model = selected
            
            # Display confirmation with checkmark
            os.system('cls' if os.name == 'nt' else 'clear')
            print()
            print_checkmark("Model Selected:")
            print(f"  {Colors.GREEN}Name: {selected['modelName']}{Colors.END}")
            print(f"  {Colors.GREEN}ID: {selected['modelId']}{Colors.END}")
            print(f"  {Colors.GREEN}Provider: {selected['providerName']}{Colors.END}")
            print()
            print_check("This model is now active for /ask commands")
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
        """Start interactive mode with smart suggestions"""
        from utils.suggestions import SmartSuggestions
        from utils.keyboard import KeyboardInput
        
        print_header("AWS Bedrock Code Assistant")
        print_info("Type '/help' for commands, '/exit' to quit")
        print_check("Smart suggestions enabled - type / for command hints\n")
        
        commands = list(SlashCommandParser.SLASH_COMMANDS.keys())
        
        while True:
            try:
                # Show prompt and get input
                sys.stdout.write(f"{Colors.BOLD}{Colors.GREEN}>> {Colors.END}")
                sys.stdout.flush()
                
                # Use interactive input with real-time suggestions
                from utils import InteractiveInput, SmartSuggestions
                
                def suggestion_callback(typed: str, tab_pressed: bool = False) -> Optional[str]:
                    """Show suggestions as user types"""
                    if typed.startswith('/'):
                        cmd_part = typed[1:]
                        suggestions = SmartSuggestions(
                            list(SlashCommandParser.SLASH_COMMANDS.keys())
                        )
                        best = suggestions.get_best_match(cmd_part, 
                                                         list(SlashCommandParser.SLASH_COMMANDS.keys()))
                        if tab_pressed and best:
                            # Return auto-completed command
                            return '/' + best
                        elif best:
                            # Show inline suggestion
                            remaining = best[len(cmd_part):]
                            sys.stdout.write(f"{Colors.CYAN}{remaining}{Colors.END}")
                            sys.stdout.flush()
                            for _ in range(len(remaining)):
                                sys.stdout.write('\b')
                            sys.stdout.flush()
                    return None
                
                user_input = InteractiveInput.get_line_with_callback(
                    prompt="",
                    on_char_callback=suggestion_callback
                ).strip()
                
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
