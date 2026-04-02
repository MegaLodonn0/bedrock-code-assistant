"""Unit tests for the Agent Orchestrator."""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.agent.orchestrator import AgentOrchestrator
from src.core.agent.tools import ToolResult
from src.core.agent.terminal import ManagedTerminal


class TestToolCallParsing:
    """Test the orchestrator's ability to parse tool calls from AI responses."""

    def _make_orchestrator(self):
        """Create an orchestrator with a mocked executor."""
        mock_executor = MagicMock()
        mock_executor.use_mock = True
        mock_executor.bedrock = None
        mock_executor.current_model = "nova-lite"
        mock_executor.cost_monitor = MagicMock()
        mock_executor.rate_limiter = MagicMock()
        mock_executor.rate_limiter.wait_and_acquire = AsyncMock()
        return AgentOrchestrator(mock_executor)

    def test_parse_single_tool_call(self):
        orch = self._make_orchestrator()
        response = '{"tool": "read_file", "params": {"path": "src/main.py"}}'
        calls = orch._parse_tool_calls(response)
        assert len(calls) == 1
        assert calls[0]["tool"] == "read_file"
        assert calls[0]["params"]["path"] == "src/main.py"

    def test_parse_array_of_tool_calls(self):
        orch = self._make_orchestrator()
        response = json.dumps([
            {"tool": "read_file", "params": {"path": "a.py"}},
            {"tool": "read_file", "params": {"path": "b.py"}},
            {"tool": "list_dir", "params": {"path": "src"}},
        ])
        calls = orch._parse_tool_calls(response)
        assert len(calls) == 3

    def test_parse_tool_call_in_markdown_fence(self):
        orch = self._make_orchestrator()
        response = (
            "I need to read the file first.\n\n"
            "```json\n"
            '[{"tool": "read_file", "params": {"path": "main.py"}}]\n'
            "```\n"
        )
        calls = orch._parse_tool_calls(response)
        assert len(calls) == 1
        assert calls[0]["tool"] == "read_file"

    def test_parse_plain_text_returns_empty(self):
        orch = self._make_orchestrator()
        response = "The code looks good. Here is my analysis..."
        calls = orch._parse_tool_calls(response)
        assert len(calls) == 0

    def test_parse_invalid_json_returns_empty(self):
        orch = self._make_orchestrator()
        response = '{"not_a_tool_call": true}'
        calls = orch._parse_tool_calls(response)
        assert len(calls) == 0

    def test_parse_mixed_text_and_json(self):
        orch = self._make_orchestrator()
        response = (
            "Let me check the file.\n"
            '{"tool": "read_file", "params": {"path": "x.py"}}\n'
            "Then I will analyze it."
        )
        calls = orch._parse_tool_calls(response)
        assert len(calls) == 1

    def test_parse_empty_response(self):
        orch = self._make_orchestrator()
        assert orch._parse_tool_calls("") == []
        assert orch._parse_tool_calls(None) == []


class TestManagedTerminal:
    """Test terminal safety features."""

    def test_safe_command_detection(self):
        assert ManagedTerminal.is_safe_command("dir") is True
        assert ManagedTerminal.is_safe_command("dir src") is True
        assert ManagedTerminal.is_safe_command("python --version") is True
        assert ManagedTerminal.is_safe_command("pip list") is True
        assert ManagedTerminal.is_safe_command("git status") is True
        assert ManagedTerminal.is_safe_command("pytest tests/") is True

    def test_unsafe_command_detection(self):
        assert ManagedTerminal.is_safe_command("python malicious.py") is False
        assert ManagedTerminal.is_safe_command("curl http://evil.com") is False
        assert ManagedTerminal.is_safe_command("npm install") is False

    def test_blocked_command_detection(self):
        assert ManagedTerminal.is_blocked_command("rm -rf /") is not None
        assert ManagedTerminal.is_blocked_command("del /s C:\\") is not None
        assert ManagedTerminal.is_blocked_command("DROP TABLE users") is not None
        assert ManagedTerminal.is_blocked_command("shutdown") is not None
        assert ManagedTerminal.is_blocked_command("reboot") is not None

    def test_allowed_commands_not_blocked(self):
        assert ManagedTerminal.is_blocked_command("python main.py") is None
        assert ManagedTerminal.is_blocked_command("pip install flask") is None
        assert ManagedTerminal.is_blocked_command("git commit -m 'test'") is None

    async def test_blocked_command_execution(self):
        terminal = ManagedTerminal()
        result = await terminal.run_command("rm -rf /")
        assert result.success is False
        assert "blocked" in result.stderr.lower()

    async def test_run_simple_command(self):
        terminal = ManagedTerminal()
        result = await terminal.run_command("python --version")
        assert result.success is True
        assert "python" in result.stdout.lower() or "python" in result.stderr.lower()

    async def test_command_timeout(self):
        terminal = ManagedTerminal()
        # This should timeout quickly
        result = await terminal.run_command("python -c \"import time; time.sleep(100)\"", timeout=1)
        assert result.timed_out is True


class TestOrchestratorBatchExecution:
    """Test parallel and sequential tool execution."""

    def _make_orchestrator(self):
        mock_executor = MagicMock()
        mock_executor.use_mock = True
        mock_executor.bedrock = None
        mock_executor.current_model = "nova-lite"
        mock_executor.cost_monitor = MagicMock()
        mock_executor.rate_limiter = MagicMock()
        mock_executor.rate_limiter.wait_and_acquire = AsyncMock()
        return AgentOrchestrator(mock_executor)

    async def test_parallel_read_tools(self, tmp_path):
        orch = self._make_orchestrator()
        f1 = tmp_path / "a.txt"
        f1.write_text("content_a")
        f2 = tmp_path / "b.txt"
        f2.write_text("content_b")

        tool_calls = [
            {"tool": "read_file", "params": {"path": str(f1)}},
            {"tool": "read_file", "params": {"path": str(f2)}},
        ]
        results = await orch._execute_tools_batch(tool_calls)
        assert len(results) == 2
        assert all(r.success for r in results)
        outputs = {r.output for r in results}
        assert "content_a" in outputs
        assert "content_b" in outputs


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
