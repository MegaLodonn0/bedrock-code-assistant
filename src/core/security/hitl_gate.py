"""Human-in-the-loop gate for approving sensitive operations.

All public methods have both a synchronous and an async variant so they
can be safely called from both sync code and inside an asyncio event loop.
"""

import asyncio
import difflib

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


class HITLGate:
    # ──────────────────────────────────────────────────────────────
    # File-diff approval (used by /execute and code patching flows)
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _show_diff_panel(filepath: str, old_content: str, new_content: str) -> str:
        """Render the diff panel and return user choice (blocking, run in thread)."""
        diff = difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=f"OLD: {filepath}",
            tofile=f"NEW: {filepath}",
            lineterm="",
        )
        diff_text = "\n".join(diff)
        if not diff_text:
            return "y"  # No changes — auto-approve

        console.print(Panel(
            Syntax(diff_text, "diff", theme="monokai"),
            title=f"🚨 APPROVAL REQUIRED: {filepath}",
            subtitle="Accept changes? (y/n)",
        ))
        return input(">> ").strip().lower()

    @staticmethod
    def request_approval(filepath: str, old_content: str, new_content: str) -> bool:
        """Synchronous approval request (safe for use outside asyncio loops)."""
        choice = HITLGate._show_diff_panel(filepath, old_content, new_content)
        return choice == "y"

    @staticmethod
    async def async_request_approval(filepath: str, old_content: str, new_content: str) -> bool:
        """Async-safe approval request — does not block the event loop."""
        choice = await asyncio.to_thread(
            HITLGate._show_diff_panel, filepath, old_content, new_content
        )
        return choice == "y"

    # ──────────────────────────────────────────────────────────────
    # Terminal command approval (used by the agent's run_terminal tool)
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _show_command_panel(command: str, context: str = "") -> str:
        """Render the command approval panel and return user choice (blocking)."""
        console.print(Panel(
            Syntax(command, "bash", theme="monokai", word_wrap=True),
            title="🚨 TERMINAL COMMAND — APPROVE?",
            subtitle="Run this command? (y/n)",
            border_style="red",
        ))
        if context:
            console.print(f"  [dim]Reason: {context}[/dim]")
        return input(">> ").strip().lower()

    @staticmethod
    def request_command_approval(command: str, context: str = "") -> bool:
        """Synchronous command approval (safe for use outside asyncio loops)."""
        choice = HITLGate._show_command_panel(command, context)
        return choice == "y"

    @staticmethod
    async def async_request_command_approval(command: str, context: str = "") -> bool:
        """Async-safe command approval — does not block the event loop."""
        choice = await asyncio.to_thread(
            HITLGate._show_command_panel, command, context
        )
        return choice == "y"
