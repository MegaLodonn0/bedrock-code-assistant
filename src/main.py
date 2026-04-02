#!/usr/bin/env python3
import sys
import logging
import asyncio
from pathlib import Path

# Resolve project root (parent of the src/ directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import settings
from src.core.executor import Executor
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

HELP_TEXT = """
[bold magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold magenta]
[bold white]  Bedrock Copilot — Command Reference[/bold white]
[bold magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold magenta]

[bold cyan]AI Commands:[/bold cyan]
  [green]/ask <query>[/green]         Ask the AI a question about your code
  [green]/analyze <file>[/green]      Analyze a source file with AI insights
  [green]/execute <code>[/green]      Run code in Docker sandbox (HITL approval required)

[bold yellow]🤖 Agent Mode (NEW):[/bold yellow]
  [green]/agent <query>[/green]       Ask the AI agent — it can read files, browse
                        your project, run terminal commands (with approval),
                        and analyze outputs autonomously.

[bold cyan]Model Management:[/bold cyan]
  [green]/model <name>[/green]        Switch the active model  (e.g. /model nova-lite)
  [green]/models[/green]              List all available Bedrock models

[bold cyan]Quality & Feedback:[/bold cyan]
  [green]/qa [lang][/green]           Run QA checks on the last AI response (default: python)
  [green]/feedback[/green]            Start interactive feedback loop on the last response

[bold cyan]Memory & Sessions:[/bold cyan]
  [green]/memory[/green]              Show vector DB status
  [green]/recall <query>[/green]      Semantic search over conversation history
  [green]/save <name>[/green]         Save current session to disk
  [green]/load <name>[/green]         Load a saved session from disk
  [green]/sessions[/green]            List all saved sessions

[bold cyan]Stats & Info:[/bold cyan]
  [green]/usage[/green]               Show cost summary
  [green]/rate[/green]                Show rate limiter status
  [green]/help[/green]                Show this help message
  [green]exit[/green]                 Exit the program

[bold magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold magenta]
"""


async def interactive_mode(executor: Executor):
    console.print(
        f"\n[bold green]★ Bedrock Copilot v3.5 Hardened[/bold green] — "
        f"model: [cyan]{executor.current_model}[/cyan]\n"
        "Type [bold]/help[/bold] for commands or [bold]exit[/bold] to quit.\n"
    )

    while True:
        try:
            prompt_str = f"[magenta]copilot[/magenta][[cyan]{executor.current_model}[/cyan]]> "
            user_input = console.input(prompt_str).strip()

            if not user_input:
                continue

            # ── Exit ───────────────────────────────────────────────
            if user_input == "exit":
                console.print("[dim]Goodbye![/dim]")
                break

            # ── Help ───────────────────────────────────────────────
            elif user_input == "/help":
                console.print(HELP_TEXT)

            # ── AI Commands ─────────────────────────────────────────
            elif user_input.startswith("/ask "):
                query = user_input[5:].strip()
                if not query:
                    console.print("[yellow]Usage:[/yellow] /ask <your question>")
                    continue
                r = await executor.ask_ai(query)
                console.print(Panel(r, title=f"[bold]Bedrock AI[/bold] [{executor.current_model}]", border_style="green"))

            elif user_input.startswith("/analyze "):
                filepath = user_input[9:].strip()
                if not filepath:
                    console.print("[yellow]Usage:[/yellow] /analyze <file_path>")
                    continue
                r = await executor.analyze_file(filepath)
                console.print(Panel(r, title="[bold]Code Analysis[/bold]", border_style="blue"))

            elif user_input.startswith("/execute "):
                code = user_input[9:].strip()
                if not code:
                    console.print("[yellow]Usage:[/yellow] /execute <python_code>")
                    continue
                success, result = await executor.execute_code(code)
                title = "Output" if success else "Error"
                style = "green" if success else "red"
                console.print(Panel(result, title=title, border_style=style))

            # ── Agent Mode ──────────────────────────────────────────
            elif user_input.startswith("/agent "):
                query = user_input[7:].strip()
                if not query:
                    console.print("[yellow]Usage:[/yellow] /agent <your request>")
                    continue
                console.print("[bold yellow]🤖 Agent mode activated[/bold yellow]")
                r = await executor.ask_agent(query, console=console)
                console.print(Panel(
                    r,
                    title=f"[bold]🤖 Agent Response[/bold] [{executor.current_model}]",
                    border_style="yellow",
                ))

            # ── Model Management ────────────────────────────────────
            elif user_input.startswith("/model "):
                model_name = user_input[7:].strip()
                if not model_name:
                    console.print("[yellow]Usage:[/yellow] /model <model_name>")
                    continue
                console.print(executor.set_model(model_name))

            elif user_input == "/models":
                table = Table(title="Available Models", border_style="cyan")
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Model ID", style="dim")
                table.add_column("Active", justify="center")
                for name, model_id in settings.bedrock_models.items():
                    active = "[bold green]✓[/bold green]" if name == executor.current_model else ""
                    table.add_row(name, model_id, active)
                console.print(table)

            # ── Quality & Feedback ──────────────────────────────────
            elif user_input.startswith("/qa"):
                parts = user_input.split(maxsplit=1)
                lang = parts[1].strip() if len(parts) > 1 else "python"
                console.print(Panel(
                    executor.run_qa(lang),
                    title=f"[bold]QA Report[/bold] [{lang}]",
                    border_style="yellow"
                ))

            elif user_input == "/feedback":
                if not executor.last_response:
                    console.print("[yellow]No response yet. Run /ask first.[/yellow]")
                else:
                    console.print("[dim]Starting interactive feedback loop...[/dim]")
                    _, approved = await executor.feedback_loop.start_refinement(
                        executor.last_request or "query",
                        executor.last_response,
                        revision_callback=executor.ask_ai
                    )
                    status = "[green]Approved[/green]" if approved else "[yellow]Pending[/yellow]"
                    console.print(f"\nStatus: {status}")

            # ── Memory & Sessions ───────────────────────────────────
            elif user_input == "/memory":
                console.print(executor.get_memory_stats())

            elif user_input.startswith("/recall "):
                query = user_input[8:].strip()
                if not query:
                    console.print("[yellow]Usage:[/yellow] /recall <search_term>")
                    continue
                console.print(executor.search_memory(query))

            elif user_input.startswith("/save "):
                name = user_input[6:].strip()
                if not name:
                    console.print("[yellow]Usage:[/yellow] /save <session_name>")
                    continue
                console.print(executor.save_session(name))

            elif user_input.startswith("/load "):
                name = user_input[6:].strip()
                if not name:
                    console.print("[yellow]Usage:[/yellow] /load <session_name>")
                    continue
                console.print(executor.load_session(name))

            elif user_input == "/sessions":
                console.print(executor.list_sessions())

            # ── Stats ───────────────────────────────────────────────
            elif user_input == "/usage":
                console.print(executor.cost_monitor.get_summary())

            elif user_input == "/rate":
                console.print(executor.get_rate_stats())

            # ── Unknown Command ─────────────────────────────────────
            else:
                console.print(
                    f"[yellow]Unknown command:[/yellow] {user_input}\n"
                    "Type [bold]/help[/bold] for available commands."
                )

        except KeyboardInterrupt:
            console.print("\n[dim]Exiting...[/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def main():
    executor = Executor()
    asyncio.run(interactive_mode(executor))


if __name__ == "__main__":
    sys.exit(main())
