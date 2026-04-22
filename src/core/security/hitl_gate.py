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


# ──────────────────────────────────────────────────────────────────────────────
# Web HITL Gate — replaces CLI blocking with asyncio queue for web UI
# ──────────────────────────────────────────────────────────────────────────────

class WebHITLGate:
    """
    Async HITL gate for the Web UI.

    Instead of blocking on CLI input(), this gate:
    1. Puts a pending request dict onto `event_queue` (an asyncio.Queue the SSE
       stream is draining — so frontend receives the approval request instantly).
    2. Waits on an asyncio.Event.
    3. When the user clicks Approve/Reject in the browser, `resolve()` is called
       by the POST /api/agent/respond endpoint, which sets the event.
    4. The gate returns True (approved) or False (rejected) to the orchestrator.
    """

    def __init__(self, event_queue: asyncio.Queue):
        """
        Args:
            event_queue: The asyncio.Queue that the SSE stream is draining.
                         All events emitted here will reach the browser in real-time.
        """
        self._queue = event_queue
        self._event = asyncio.Event()
        self._decision: str = "reject"   # "approve" | "reject"
        self._lock = asyncio.Lock()       # Only one pending approval at a time

    async def request_file_approval(
        self,
        filepath: str,
        old_content: str,
        new_content: str,
    ) -> bool:
        """
        Emit a `hitl_file` SSE event and wait for user decision.

        Returns True if approved, False if rejected.
        """
        import difflib
        diff = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=f"original/{filepath}",
            tofile=f"modified/{filepath}",
            lineterm="",
        ))

        async with self._lock:
            self._event.clear()
            self._decision = "reject"

            await self._queue.put({
                "type": "hitl_file",
                "filepath": filepath,
                "diff": "\n".join(diff),
                "old": old_content,
                "new": new_content,
                "is_new_file": old_content == "",
            })

            await self._event.wait()
            return self._decision == "approve"

    async def request_command_approval(
        self,
        command: str,
        context: str = "",
    ) -> bool:
        """
        Emit a `hitl_cmd` SSE event and wait for user decision.

        Returns True if approved, False if rejected.
        """
        async with self._lock:
            self._event.clear()
            self._decision = "reject"

            await self._queue.put({
                "type": "hitl_cmd",
                "command": command,
                "context": context,
            })

            await self._event.wait()
            return self._decision == "approve"

    def resolve(self, decision: str) -> None:
        """
        Called by POST /api/agent/respond to unblock a pending approval.

        Args:
            decision: "approve" or "reject"
        """
        self._decision = decision
        self._event.set()

