"""Unit tests for the Agent Tool System."""

import pytest
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.agent.tools import (
    ToolRegistry, ToolResult, ToolDefinition,
    tool_read_file, tool_list_dir, tool_glob_files,
    tool_search_code, tool_tree_view,
)


class TestToolResult:
    """Test ToolResult dataclass."""

    def test_successful_result(self):
        r = ToolResult("test", True, "output", None, 10.5)
        assert r.success is True
        assert r.output == "output"
        assert r.error is None

    def test_failed_result(self):
        r = ToolResult("test", False, "", "something broke", 5.0)
        assert r.success is False
        assert r.error == "something broke"


class TestToolReadFile:
    """Test read_file tool."""

    @pytest.fixture
    def temp_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("print('hello world')\n")
        return str(f)

    async def test_read_existing_file(self, temp_file):
        result = await tool_read_file(temp_file)
        assert result.success is True
        assert "print('hello world')" in result.output

    async def test_read_nonexistent_file(self):
        result = await tool_read_file("/nonexistent/file.py")
        assert result.success is False
        assert "not found" in result.error.lower()

    async def test_read_directory_fails(self, tmp_path):
        result = await tool_read_file(str(tmp_path))
        assert result.success is False
        assert "not a file" in result.error.lower()


class TestToolListDir:
    """Test list_dir tool."""

    async def test_list_existing_dir(self, tmp_path):
        (tmp_path / "file1.py").write_text("a")
        (tmp_path / "file2.py").write_text("b")
        (tmp_path / "subdir").mkdir()
        result = await tool_list_dir(str(tmp_path))
        assert result.success is True
        assert "file1.py" in result.output
        assert "file2.py" in result.output
        assert "subdir" in result.output

    async def test_list_nonexistent_dir(self):
        result = await tool_list_dir("/nonexistent/dir")
        assert result.success is False

    async def test_skips_pycache(self, tmp_path):
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "real_file.py").write_text("x")
        result = await tool_list_dir(str(tmp_path))
        assert result.success is True
        assert "__pycache__" not in result.output
        assert "real_file.py" in result.output


class TestToolGlobFiles:
    """Test glob_files tool."""

    async def test_find_python_files(self, tmp_path):
        (tmp_path / "a.py").write_text("x")
        (tmp_path / "b.txt").write_text("y")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.py").write_text("z")
        result = await tool_glob_files("**/*.py", str(tmp_path))
        assert result.success is True
        assert "a.py" in result.output
        assert "c.py" in result.output
        assert "b.txt" not in result.output

    async def test_no_matches(self, tmp_path):
        result = await tool_glob_files("*.xyz", str(tmp_path))
        assert result.success is True
        assert "no matches" in result.output.lower()


class TestToolSearchCode:
    """Test search_code tool."""

    async def test_find_text_in_files(self, tmp_path):
        (tmp_path / "main.py").write_text("def hello():\n    return 'world'\n")
        (tmp_path / "util.py").write_text("import os\ndef helper(): pass\n")
        result = await tool_search_code("hello", str(tmp_path))
        assert result.success is True
        assert "main.py" in result.output
        assert "hello" in result.output

    async def test_no_matches(self, tmp_path):
        (tmp_path / "empty.py").write_text("pass\n")
        result = await tool_search_code("nonexistent_string", str(tmp_path))
        assert result.success is True
        assert "no matches" in result.output.lower()


class TestToolTreeView:
    """Test tree_view tool."""

    async def test_tree_output(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("x")
        (tmp_path / "README.md").write_text("x")
        result = await tool_tree_view(str(tmp_path))
        assert result.success is True
        assert "src/" in result.output
        assert "main.py" in result.output
        assert "README.md" in result.output


class TestToolRegistry:
    """Test ToolRegistry."""

    def test_builtins_registered(self):
        reg = ToolRegistry()
        tools = reg.list_tools()
        names = [t.name for t in tools]
        assert "read_file" in names
        assert "list_dir" in names
        assert "glob_files" in names
        assert "search_code" in names
        assert "tree_view" in names

    def test_get_tool_by_name(self):
        reg = ToolRegistry()
        tool = reg.get("read_file")
        assert tool is not None
        assert tool.name == "read_file"

    def test_get_unknown_tool(self):
        reg = ToolRegistry()
        tool = reg.get("nonexistent_tool")
        assert tool is None

    async def test_execute_tool(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        reg = ToolRegistry()
        result = await reg.execute_tool("read_file", {"path": str(f)})
        assert result.success is True
        assert result.output == "hello"

    async def test_execute_unknown_tool(self):
        reg = ToolRegistry()
        result = await reg.execute_tool("fake_tool", {})
        assert result.success is False
        assert "Unknown tool" in result.error

    def test_get_tool_descriptions(self):
        reg = ToolRegistry()
        desc = reg.get_tool_descriptions()
        assert "read_file" in desc
        assert "list_dir" in desc

    def test_get_tool_schemas(self):
        reg = ToolRegistry()
        schemas = reg.get_tool_schemas()
        assert len(schemas) >= 5
        assert all("toolSpec" in s for s in schemas)
        assert all("name" in s["toolSpec"] for s in schemas)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
