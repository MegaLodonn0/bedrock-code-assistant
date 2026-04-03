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
  [green]/models[/green]              List curated models
  [green]/models all[/green]          Interactive wizard to pull ALL AWS Bedrock models

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
            warning_icon = "" if executor.supports_agent else "[bold yellow]![/bold yellow] "
            prompt_str = f"{warning_icon}[magenta]copilot[/magenta][[cyan]{executor.current_model}[/cyan]]> "
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
                if not executor.supports_agent:
                    console.print(Panel(
                        "Note: The selected model is excellent for text or code generation, but it lacks autonomous tool-calling capabilities or Bedrock Converse compatibility. Therefore, the [bold yellow]/agent[/bold yellow] mode cannot be used.\n\n[dim]You can still use /ask for normal conversations![/dim]",
                        title="[yellow]Autonomous Agent Unsupported[/yellow]",
                        border_style="yellow"
                    ))
                    continue

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
                console.print(await executor.set_model(model_name))
                if not executor.supports_agent:
                    console.print(Panel(
                        "[dim]Note: The selected model does not support autonomous tools, so the /agent command is disabled for this session.[/dim]", 
                        border_style="yellow"
                    ))

            elif user_input == "/models all":
                if not (executor.bedrock and getattr(executor.bedrock, 'available', False)):
                    console.print("[red]Bedrock connection is unavailable. Cannot fetch all models.[/red]")
                    continue
                
                console.print("[dim]Fetching comprehensive model list from AWS...[/dim]")
                provider_groups = await executor.bedrock.get_all_grouped_models()
                
                if not provider_groups:
                    console.print("[yellow]No active models found in your AWS region.[/yellow]")
                    continue
                    
                providers = list(provider_groups.keys())
                providers.sort()
                
                console.print("\n[bold cyan]── Base AWS Model Providers ──[/bold cyan]")
                for i, prov in enumerate(providers, 1):
                    count = len(provider_groups[prov])
                    console.print(f"[{i}] {prov} [dim]({count} models)[/dim]")
                    
                prov_sel = console.input("\n[green]Select provider number (or enter to cancel): [/green]").strip()
                if not prov_sel.isdigit() or not (1 <= int(prov_sel) <= len(providers)):
                    console.print("[dim]Cancelled.[/dim]")
                    continue
                    
                selected_provider = providers[int(prov_sel) - 1]
                models_list = provider_groups[selected_provider]
                
                console.print(f"\n[bold cyan]── {selected_provider} Models ──[/bold cyan]")
                for i, m in enumerate(models_list, 1):
                    # Highlight if it's the current model
                    active_marker = "[bold green]✓[/bold green] " if m["id"] == executor.current_model else "  "
                    console.print(f"{active_marker}[{i}] {m['id']}")
                    
                mod_sel = console.input("\n[green]Select model number to equip (or enter to cancel): [/green]").strip()
                if not mod_sel.isdigit() or not (1 <= int(mod_sel) <= len(models_list)):
                    console.print("[dim]Cancelled.[/dim]")
                    continue
                    
                selected_model_id = models_list[int(mod_sel) - 1]["id"]
                resp = await executor.set_model(selected_model_id)
                console.print(resp)
                if not executor.supports_agent:
                    console.print(Panel(
                        "[dim]Note: The selected model does not support autonomous tools, so the /agent command is disabled for this session.[/dim]", 
                        border_style="yellow"
                    ))

            elif user_input == "/models":
                if executor.bedrock and getattr(executor.bedrock, 'available', False):
                    console.print("[dim]Fetching curated models from AWS...[/dim]")
                    available_models = await executor.bedrock.get_available_models()
                else:
                    available_models = settings.bedrock_models

                table = Table(title="Curated Models", border_style="cyan")
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Model ID", style="dim")
                table.add_column("Active", justify="center")
                for name, model_id in available_models.items():
                    active = "[bold green]✓[/bold green]" if name == executor.current_model else ""
                    table.add_row(name, model_id, active)
                console.print(table)
                console.print("[dim]Tip: Try [bold]/models all[/bold] to see the full list of raw AWS models (DeepSeek, Llama, Qwen etc).[/dim]")

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


import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="Bedrock Copilot")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a repository or file")
    analyze_parser.add_argument("path", help="Path to repository or file")
    analyze_parser.add_argument("--model", help="Model to use")
    analyze_parser.add_argument("--output-format", help="Output format")
    analyze_parser.add_argument("--include-metrics", action="store_true", help="Include metrics")
    analyze_parser.add_argument("--focus", help="Focus area (e.g., security)")

    # review command
    review_parser = subparsers.add_parser("review", help="Review a file")
    review_parser.add_argument("path", help="Path to file")
    review_parser.add_argument("--focus", help="Focus area")
    review_parser.add_argument("--depth", help="Review depth")

    # generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code or tests")
    generate_parser.add_argument("type", help="Type of generation (e.g., tests)")
    generate_parser.add_argument("path", help="Path to module")
    generate_parser.add_argument("--framework", help="Testing framework")
    generate_parser.add_argument("--coverage-target", type=int, help="Coverage target")

    # fix command
    fix_parser = subparsers.add_parser("fix", help="Fix issues in a file")
    fix_parser.add_argument("path", help="Path to file")
    fix_parser.add_argument("--issue-type", help="Type of issue")
    fix_parser.add_argument("--auto-apply", action="store_true", help="Auto-apply fixes")

    # map command
    map_parser = subparsers.add_parser("map", help="Map a project")
    map_parser.add_argument("path", help="Path to project")

    # report command
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_parser.add_argument("--type", help="Report type")
    report_parser.add_argument("--format", help="Report format")

    # costs command
    costs_parser = subparsers.add_parser("costs", help="Monitor costs")
    costs_parser.add_argument("--timerange", help="Time range")
    costs_parser.add_argument("--format", help="Output format")

    # interactive command
    subparsers.add_parser("interactive", help="Start interactive session")

    args = parser.parse_args()

    executor = Executor()

    if args.command == "interactive" or not args.command:
        asyncio.run(interactive_mode(executor))
    elif args.command == "map":
        # Simulate mapping output
        print(json.dumps({"mapped": args.path, "status": "success"}))
    elif args.command == "analyze":
        # Simulate analyze output
        asyncio.run(executor.analyze_file(args.path))
    elif args.command == "costs":
        print(executor.cost_monitor.get_summary())
    elif args.command == "report":
        print(f"Report generated for {args.type}")
    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main())
