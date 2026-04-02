"""
Managed Terminal
================
Safe subprocess execution for the agent. Handles command running, output capture,
process interaction (stdin), and timeout management.
"""

import asyncio
import logging
import re
import time
from dataclasses import dataclass
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Commands that are safe enough to skip explicit user approval
SAFE_COMMANDS = {
    "dir", "ls", "tree", "type", "cat", "head", "tail",
    "python --version", "python3 --version", "pip list", "pip show",
    "pip --version", "git status", "git log", "git diff", "git branch",
    "echo", "hostname", "whoami", "date", "pwd", "cd",
}

# Patterns that are ALWAYS blocked, even if user approves
BLOCKED_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bdel\s+/[sS]\b",
    r"\bformat\s+[A-Z]:",
    r"\bDROP\s+TABLE\b",
    r"\bDROP\s+DATABASE\b",
    r"\bDELETE\s+FROM\b.*\bWHERE\s+1\s*=\s*1",
    r"\brm\s+-r\s+/\b",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r">\s*/dev/sd",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bkill\s+-9\s+1\b",
    r"\bchmod\s+-R\s+777\s+/\b",
]


@dataclass
class TerminalResult:
    """Result of a terminal command execution."""
    command: str
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float
    timed_out: bool = False


class ManagedTerminal:
    """Spawn, interact with, and analyze terminal processes."""

    def __init__(self, default_timeout: int = 30, max_output_chars: int = 50_000):
        self.default_timeout = default_timeout
        self.max_output_chars = max_output_chars
        self._active_processes: Dict[str, asyncio.subprocess.Process] = {}

    @staticmethod
    def is_safe_command(command: str) -> bool:
        """Check if a command is in the safe (auto-approve) list."""
        cmd_lower = command.strip().lower()
        # Check exact matches
        if cmd_lower in SAFE_COMMANDS:
            return True
        # Check prefix matches (e.g., "dir src" starts with "dir")
        for safe in SAFE_COMMANDS:
            if cmd_lower.startswith(safe + " ") or cmd_lower == safe:
                return True
        # pytest and python test commands are safe reads
        if cmd_lower.startswith("python -m pytest") or cmd_lower.startswith("pytest"):
            return True
        return False

    @staticmethod
    def is_blocked_command(command: str) -> Optional[str]:
        """Check if a command matches a destructive pattern. Returns reason or None."""
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return f"Command blocked by safety rule: matches pattern '{pattern}'"
        return None

    async def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> TerminalResult:
        """Execute a shell command and capture output."""
        start = time.time()
        effective_timeout = timeout or self.default_timeout

        # Safety: check for blocked commands
        blocked_reason = self.is_blocked_command(command)
        if blocked_reason:
            return TerminalResult(
                command=command,
                success=False,
                stdout="",
                stderr=blocked_reason,
                return_code=-1,
                execution_time_ms=(time.time() - start) * 1000,
            )

        try:
            # Use shell=True on Windows for cmd compatibility
            import sys
            if sys.platform == "win32":
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=env,
                )
            else:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                    env=env,
                )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(), timeout=effective_timeout
                )
                timed_out = False
            except asyncio.TimeoutError:
                import sys, subprocess
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
                else:
                    import os, signal
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except Exception:
                        pass
                
                try:
                    process.kill()
                except Exception:
                    pass
                
                try:
                    stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=3.0)
                except asyncio.TimeoutError:
                    stdout_bytes, stderr_bytes = b"", b"Pipeline blocked. Process forcefully killed."
                timed_out = True

            stdout = stdout_bytes.decode("utf-8", errors="replace")[:self.max_output_chars]
            stderr = stderr_bytes.decode("utf-8", errors="replace")[:self.max_output_chars]

            if timed_out:
                stderr += f"\n\n⚠️ Command timed out after {effective_timeout}s and was killed."

            return TerminalResult(
                command=command,
                success=process.returncode == 0 and not timed_out,
                stdout=stdout,
                stderr=stderr,
                return_code=process.returncode or -1,
                execution_time_ms=(time.time() - start) * 1000,
                timed_out=timed_out,
            )

        except Exception as e:
            return TerminalResult(
                command=command,
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time_ms=(time.time() - start) * 1000,
            )

    async def run_interactive(
        self,
        command: str,
        inputs: list[str],
        cwd: Optional[str] = None,
        timeout: int = 30,
    ) -> TerminalResult:
        """Run a command that requires interactive input (y/n/a answers)."""
        start = time.time()

        blocked_reason = self.is_blocked_command(command)
        if blocked_reason:
            return TerminalResult(
                command=command, success=False, stdout="",
                stderr=blocked_reason, return_code=-1,
                execution_time_ms=(time.time() - start) * 1000,
            )

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            # Feed all inputs separated by newlines
            combined_input = "\n".join(inputs) + "\n"
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(combined_input.encode("utf-8")),
                    timeout=timeout,
                )
                timed_out = False
            except asyncio.TimeoutError:
                import sys, subprocess
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
                else:
                    import os, signal
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except Exception:
                        pass
                
                try:
                    process.kill()
                except Exception:
                    pass
                
                try:
                    stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=3.0)
                except asyncio.TimeoutError:
                    stdout_bytes, stderr_bytes = b"", b"Pipeline blocked. Process forcefully killed."
                timed_out = True

            stdout = stdout_bytes.decode("utf-8", errors="replace")[:self.max_output_chars]
            stderr = stderr_bytes.decode("utf-8", errors="replace")[:self.max_output_chars]

            return TerminalResult(
                command=command,
                success=process.returncode == 0 and not timed_out,
                stdout=stdout,
                stderr=stderr,
                return_code=process.returncode or -1,
                execution_time_ms=(time.time() - start) * 1000,
                timed_out=timed_out,
            )
        except Exception as e:
            return TerminalResult(
                command=command, success=False, stdout="",
                stderr=str(e), return_code=-1,
                execution_time_ms=(time.time() - start) * 1000,
            )


# Global instance
_terminal: Optional[ManagedTerminal] = None


def get_managed_terminal() -> ManagedTerminal:
    """Get or create the global ManagedTerminal instance."""
    global _terminal
    if _terminal is None:
        _terminal = ManagedTerminal()
    return _terminal
