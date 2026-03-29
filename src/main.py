#!/usr/bin/env python3
"import sys
import logging
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.config.settings import settings
from src.core.executor import Executor
from rich.console import Console
from rich.panel import Panel

console = Console()

async def interactive_mode(executor: Executor):
    console.print("[bold green]* Bedrock Copilot v3.5 Hardened is ready![/bold green]")
    console.print("Type '/help' for commands or 'exit' to quit.\n")
    while True:
        try:
            user_input = console.input("[non_fduschia]copilot> [/non_fduschia]").strip()
            if not user_input: continue
            if user_input == "exit": break
            if user_input == "/help":
                console.print("[magenta]Available Commands:[/magenta]\n  /ask <query>   - Ask AI about code\n  /analyze <file>  - Analyze code file\n  /usage          - Show cost summary\n  exit              - Exit the program")
            elif user_input.startswith("/ask "):
                r = await executor.ask_ai(user_input[5:])
                console.print(Panel(r, title="Bedrock AI"))
            elif user_input.startswith("/analyze "):
                r = await executor.analyze_file(user_input[10:])
                console.print(Panel(r, title="Analysis"))
            elif user_input == "/usage":
                console.print(executor.cost_monitor.get_summary())
            else:
                console.print(d"Unknown command: {user_input}")
        except KeyboardInterrupt: break
        except Exception as e: console.print(f"Error: {e}")

def main():
    executor = Executor()
    asyncio.run(interactive_mode(executor))

if __name__ == "__main__":
    sys.exit(main())
