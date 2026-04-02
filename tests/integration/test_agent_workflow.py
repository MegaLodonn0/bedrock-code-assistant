"""Integration tests for the full Agent workflow."""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.agent.orchestrator import AgentOrchestrator
from src.core.agent.tools import ToolRegistry
from src.core.agent.prompts import build_system_prompt, build_tool_result_message
from src.core.agent.tools import ToolResult


class TestPromptBuilding:
    """Test system prompt generation."""

    def test_system_prompt_contains_tool_descriptions(self):
        reg = ToolRegistry()
        prompt = build_system_prompt(reg.get_tool_descriptions())
        assert "read_file" in prompt
        assert "list_dir" in prompt
        assert "search_code" in prompt
        assert "Available Tools" in prompt

    def test_tool_result_message_formatting(self):
        results = [
            ToolResult("read_file", True, "file content here", None, 12.5),
            ToolResult("list_dir", False, "", "directory not found", 3.0),
        ]
        msg = build_tool_result_message(results)
        assert "read_file" in msg
        assert "✅" in msg
        assert "list_dir" in msg
        assert "❌" in msg
        assert "directory not found" in msg


class TestFullAgentWorkflow:
    """Test the agent end-to-end with mocked AI backend."""

    def _make_executor_mock(self):
        """Create a fully mocked executor."""
        mock = MagicMock()
        mock.use_mock = True
        mock.bedrock = None
        mock.current_model = "nova-lite"
        mock.cost_monitor = MagicMock()
        mock.rate_limiter = MagicMock()
        mock.rate_limiter.wait_and_acquire = AsyncMock()
        mock.last_response = None
        mock.last_request = None
        return mock

    async def test_mock_mode_returns_immediately(self):
        """In mock mode, the agent should return a mock message without trying tool calls."""
        mock_executor = self._make_executor_mock()
        orch = AgentOrchestrator(mock_executor)
        result = await orch.run("test query")
        assert "MOCK MODE" in result

    async def test_tool_registry_has_terminal_tools(self):
        """The orchestrator should register run_terminal and terminal_interact."""
        mock_executor = self._make_executor_mock()
        orch = AgentOrchestrator(mock_executor)
        names = [t.name for t in orch.tool_registry.list_tools()]
        assert "run_terminal" in names
        assert "terminal_interact" in names

    async def test_terminal_tools_require_approval(self):
        """Terminal tools must be marked as requiring approval."""
        mock_executor = self._make_executor_mock()
        orch = AgentOrchestrator(mock_executor)
        run_term = orch.tool_registry.get("run_terminal")
        interact = orch.tool_registry.get("terminal_interact")
        assert run_term.requires_approval is True
        assert interact.requires_approval is True

    async def test_read_tools_do_not_require_approval(self):
        """Read-only tools must NOT require approval."""
        mock_executor = self._make_executor_mock()
        orch = AgentOrchestrator(mock_executor)
        for name in ["read_file", "list_dir", "glob_files", "search_code", "tree_view"]:
            tool = orch.tool_registry.get(name)
            assert tool.requires_approval is False, f"{name} should not require approval"


class TestToolSchemaIntegrity:
    """Ensure tool schemas are valid for Bedrock ToolConfiguration."""

    def test_schemas_have_required_fields(self):
        reg = ToolRegistry()
        schemas = reg.get_tool_schemas()
        for schema in schemas:
            assert "toolSpec" in schema
            spec = schema["toolSpec"]
            assert "name" in spec
            assert "description" in spec
            assert "inputSchema" in spec
            assert "json" in spec["inputSchema"]
            json_schema = spec["inputSchema"]["json"]
            assert json_schema["type"] == "object"
            assert "properties" in json_schema


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
