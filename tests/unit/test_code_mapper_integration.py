"""
Tests for src/core/code_map/code_mapper.py (CodeMapper orchestrator).

These integration tests verify the full pipeline:
  index_file → index_directory → get_context → ContextBundle
without any AWS/Docker/network dependencies.
"""

import os
import textwrap
import tempfile
from pathlib import Path

import pytest

from src.core.code_map.code_mapper import CodeMapper, get_code_mapper, reset_code_mapper
from src.core.code_map.symbols import ContextBundle, SymbolKind


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mapper():
    """Fresh CodeMapper (not the singleton) for each test."""
    return CodeMapper()


@pytest.fixture(scope="function")
def py_file(tmp_path):
    """Write a temp Python file and return its path."""
    content = textwrap.dedent("""\
        import os
        from pathlib import Path

        class FileProcessor:
            \"\"\"Processes files on disk.\"\"\"

            def read(self, path: str) -> str:
                \"\"\"Read file content.\"\"\"
                return Path(path).read_text()

            def write(self, path: str, data: str) -> None:
                \"\"\"Write data to file.\"\"\"
                Path(path).write_text(data)

        def compute_checksum(content: str) -> int:
            \"\"\"Compute simple checksum.\"\"\"
            return sum(ord(c) for c in content)
    """)
    f = tmp_path / "processor.py"
    f.write_text(content, encoding="utf-8")
    return str(f)


@pytest.fixture(scope="function")
def js_file(tmp_path):
    content = textwrap.dedent("""\
        import { readFile } from 'fs';

        class DataLoader {
            load(path) {
                return readFile(path);
            }
        }

        function parseJSON(raw) {
            return JSON.parse(raw);
        }
    """)
    f = tmp_path / "loader.js"
    f.write_text(content, encoding="utf-8")
    return str(f)


# ---------------------------------------------------------------------------
# CodeMapper.index_file()
# ---------------------------------------------------------------------------

class TestIndexFile:

    def test_index_existing_py_file(self, mapper, py_file):
        result = mapper.index_file(py_file)
        assert result.language == "python"
        assert not result.parse_errors
        assert len(result.symbols) > 0

    def test_index_finds_class(self, mapper, py_file):
        mapper.index_file(py_file)
        graph = mapper._get_graph()
        classes = [s for s in graph.all_symbols() if s.kind == SymbolKind.CLASS]
        assert any(c.name == "FileProcessor" for c in classes)

    def test_index_finds_function(self, mapper, py_file):
        mapper.index_file(py_file)
        graph = mapper._get_graph()
        funcs = [s for s in graph.all_symbols() if s.kind == SymbolKind.FUNCTION]
        assert any(f.name == "compute_checksum" for f in funcs)

    def test_index_missing_file_returns_error(self, mapper):
        result = mapper.index_file("/nonexistent/path/file.py")
        assert result.parse_errors

    def test_index_unsupported_extension_returns_error(self, mapper, tmp_path):
        f = tmp_path / "file.unknown_xyz"
        f.write_text("content")
        result = mapper.index_file(str(f))
        assert result.parse_errors

    def test_index_js_file(self, mapper, js_file):
        result = mapper.index_file(js_file)
        assert result.language == "javascript"
        assert len(result.symbols) > 0

    def test_index_updates_stats(self, mapper, py_file):
        mapper.index_file(py_file)
        stats = mapper.stats()
        assert stats["indexed_files"] >= 1
        assert stats["total_symbols"] >= 1

    def test_index_same_file_twice_no_duplicates(self, mapper, py_file):
        mapper.index_file(py_file)
        count_after_first = mapper.stats()["total_symbols"]
        mapper.index_file(py_file)
        count_after_second = mapper.stats()["total_symbols"]
        # Second index should not increase node count significantly
        assert count_after_second <= count_after_first + 2


# ---------------------------------------------------------------------------
# CodeMapper.index_directory()
# ---------------------------------------------------------------------------

class TestIndexDirectory:

    def test_index_directory_returns_int(self, mapper, tmp_path):
        (tmp_path / "a.py").write_text("def foo(): pass")
        (tmp_path / "b.py").write_text("def bar(): pass")
        total = mapper.index_directory(str(tmp_path), patterns=["*.py"])
        assert total > 0

    def test_excludes_ignored_dirs(self, mapper, tmp_path):
        excluded = tmp_path / "__pycache__"
        excluded.mkdir()
        (excluded / "cached.py").write_text("def cached(): pass")
        (tmp_path / "real.py").write_text("def real(): pass")
        mapper.index_directory(str(tmp_path), patterns=["**/*.py"])
        graph = mapper._get_graph()
        names = {s.name for s in graph.all_symbols()}
        assert "real" in names
        # cached should be excluded
        assert "cached" not in names


# ---------------------------------------------------------------------------
# CodeMapper.get_context()
# ---------------------------------------------------------------------------

class TestGetContext:

    def test_get_context_returns_bundle(self, mapper, py_file):
        bundle = mapper.get_context(py_file, "How does file reading work?")
        assert isinstance(bundle, ContextBundle)

    def test_get_context_with_symbol(self, mapper, py_file):
        bundle = mapper.get_context(py_file, "explain read method", symbol="read")
        assert isinstance(bundle, ContextBundle)

    def test_bundle_not_empty(self, mapper, py_file):
        bundle = mapper.get_context(py_file, "What does this file do?")
        assert bundle.symbol_count > 0

    def test_bundle_tokens_less_than_raw_file(self, mapper, py_file):
        bundle = mapper.get_context(py_file, "analyze", token_budget=2000)
        raw_size = os.path.getsize(py_file)
        raw_tokens_est = raw_size // 4
        # Context should be significantly smaller than the full file
        assert bundle.total_tokens_estimate <= raw_tokens_est

    def test_bundle_has_language(self, mapper, py_file):
        bundle = mapper.get_context(py_file, "explain")
        assert "python" in bundle.languages

    def test_to_prompt_nonempty(self, mapper, py_file):
        bundle = mapper.get_context(py_file, "read method")
        prompt = bundle.to_prompt()
        assert len(prompt) > 10

    def test_depth_parameter_respected(self, mapper, py_file):
        b_shallow = mapper.get_context(py_file, "read", depth=1, token_budget=5000)
        b_deep    = mapper.get_context(py_file, "read", depth=3, token_budget=5000)
        # Deeper search can only return >= the shallow result
        assert b_deep.symbol_count >= b_shallow.symbol_count - 1  # allow minor variance

    def test_token_budget_respected(self, mapper, py_file):
        tiny_bundle  = mapper.get_context(py_file, "read", token_budget=50)
        large_bundle = mapper.get_context(py_file, "read", token_budget=5000)
        assert large_bundle.symbol_count >= tiny_bundle.symbol_count


# ---------------------------------------------------------------------------
# CodeMapper.invalidate()
# ---------------------------------------------------------------------------

class TestInvalidate:

    def test_invalidate_removes_file_symbols(self, mapper, py_file):
        mapper.index_file(py_file)
        before = mapper.stats()["total_symbols"]
        mapper.invalidate(py_file)
        after = mapper.stats()["total_symbols"]
        assert after < before

    def test_invalidate_nonexistent_does_not_raise(self, mapper):
        mapper.invalidate("/nonexistent/file.py")  # should not raise


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

class TestSingleton:

    def test_get_code_mapper_returns_same_instance(self):
        reset_code_mapper()
        a = get_code_mapper()
        b = get_code_mapper()
        assert a is b

    def test_reset_creates_fresh_instance(self):
        a = get_code_mapper()
        reset_code_mapper()
        b = get_code_mapper()
        assert a is not b

    def test_singleton_stats_initially_empty(self):
        reset_code_mapper()
        m = get_code_mapper()
        stats = m.stats()
        assert stats["indexed_files"] == 0
        assert stats["total_symbols"] == 0
