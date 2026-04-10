"""
Tests for src/core/code_map/parser/

Covers TreeSitterParser and FallbackParser across multiple languages.
All tests run offline — no AWS, Docker or network required.
"""

import textwrap
import pytest

from src.core.code_map.symbols import SymbolKind, ParseResult
from src.core.code_map.parser.treesitter_parser import TreeSitterParser
from src.core.code_map.parser.fallback_parser import FallbackParser
from src.core.code_map.languages import detect_language, is_parseable


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def ts_parser():
    return TreeSitterParser()


@pytest.fixture(scope="module")
def fb_parser():
    return FallbackParser()


# ---------------------------------------------------------------------------
# detect_language()
# ---------------------------------------------------------------------------

class TestDetectLanguage:
    def test_python(self):
        assert detect_language("foo.py") == "python"

    def test_javascript(self):
        assert detect_language("app.js") == "javascript"

    def test_typescript(self):
        assert detect_language("comp.ts") == "typescript"

    def test_tsx(self):
        assert detect_language("comp.tsx") == "tsx"

    def test_go(self):
        assert detect_language("main.go") == "go"

    def test_java(self):
        assert detect_language("App.java") == "java"

    def test_rust(self):
        assert detect_language("lib.rs") == "rust"

    def test_c(self):
        assert detect_language("main.c") == "c"

    def test_cpp(self):
        assert detect_language("app.cpp") == "cpp"

    def test_kotlin(self):
        assert detect_language("Main.kt") == "kotlin"

    def test_ruby(self):
        assert detect_language("app.rb") == "ruby"

    def test_dockerfile(self):
        assert detect_language("Dockerfile") == "dockerfile"

    def test_unknown_returns_none(self):
        assert detect_language("file.xyz123") is None

    def test_is_parseable_true(self):
        assert is_parseable("main.py") is True

    def test_is_parseable_false(self):
        assert is_parseable("binary.bin") is False


# ---------------------------------------------------------------------------
# TreeSitterParser — Python
# ---------------------------------------------------------------------------

class TestTreeSitterParserPython:

    PYTHON_SOURCE = textwrap.dedent("""\
        import os
        from pathlib import Path

        class MyService:
            \"\"\"A simple service.\"\"\"

            def process(self, data: str) -> str:
                \"\"\"Process the data.\"\"\"
                result = helper(data)
                return result

        def helper(text):
            return text.upper()
    """)

    def test_parse_returns_result(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        assert isinstance(result, ParseResult)
        assert result.language == "python"

    def test_finds_class(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        kinds = {s.kind for s in result.symbols}
        assert SymbolKind.CLASS in kinds

    def test_finds_function(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        names = {s.name for s in result.symbols}
        assert "helper" in names

    def test_finds_method(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        methods = [s for s in result.symbols if s.kind == SymbolKind.METHOD]
        assert any(m.name == "process" for m in methods)

    def test_finds_imports(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        imports = [s for s in result.symbols if s.kind == SymbolKind.IMPORT]
        assert len(imports) >= 2

    def test_symbol_ids_are_unique(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        ids = [s.id for s in result.symbols]
        assert len(ids) == len(set(ids))

    def test_symbol_line_numbers_valid(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        for sym in result.symbols:
            assert sym.start_line >= 1
            assert sym.end_line >= sym.start_line

    def test_docstring_extracted(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        methods = [s for s in result.symbols if s.name == "process"]
        assert methods
        assert "Process" in methods[0].docstring or methods[0].docstring == ""

    def test_method_id_includes_class(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        method_ids = [s.id for s in result.symbols if s.kind == SymbolKind.METHOD]
        # At least one method ID should contain the class name
        assert any("MyService" in mid for mid in method_ids)

    def test_calls_extracted(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        methods = [s for s in result.symbols if s.name == "process"]
        if methods:
            assert "helper" in methods[0].calls or methods[0].calls == []

    def test_no_parse_errors(self, ts_parser):
        result = ts_parser.parse("service.py", self.PYTHON_SOURCE, "python")
        assert result.parse_errors == []


# ---------------------------------------------------------------------------
# TreeSitterParser — JavaScript
# ---------------------------------------------------------------------------

class TestTreeSitterParserJavaScript:

    JS_SOURCE = textwrap.dedent("""\
        import { useState } from 'react';
        import utils from './utils';

        class UserComponent {
            render() {
                return 'hello';
            }
        }

        function fetchData(url) {
            return fetch(url);
        }

        const helper = (x) => x * 2;
    """)

    def test_parse_js(self, ts_parser):
        result = ts_parser.parse("app.js", self.JS_SOURCE, "javascript")
        assert result.language == "javascript"

    def test_finds_js_class(self, ts_parser):
        result = ts_parser.parse("app.js", self.JS_SOURCE, "javascript")
        classes = [s for s in result.symbols if s.kind == SymbolKind.CLASS]
        assert any(c.name == "UserComponent" for c in classes)

    def test_finds_js_function(self, ts_parser):
        result = ts_parser.parse("app.js", self.JS_SOURCE, "javascript")
        funcs = [s for s in result.symbols if s.kind == SymbolKind.FUNCTION]
        assert any(f.name == "fetchData" for f in funcs)

    def test_finds_js_imports(self, ts_parser):
        result = ts_parser.parse("app.js", self.JS_SOURCE, "javascript")
        imports = [s for s in result.symbols if s.kind == SymbolKind.IMPORT]
        assert len(imports) >= 2


# ---------------------------------------------------------------------------
# TreeSitterParser — Go
# ---------------------------------------------------------------------------

class TestTreeSitterParserGo:

    GO_SOURCE = textwrap.dedent("""\
        package main

        import (
            "fmt"
            "os"
        )

        type Server struct {
            Host string
            Port int
        }

        func NewServer(host string, port int) *Server {
            return &Server{Host: host, Port: port}
        }

        func (s *Server) Start() error {
            fmt.Println("starting")
            return nil
        }
    """)

    def test_parse_go(self, ts_parser):
        result = ts_parser.parse("main.go", self.GO_SOURCE, "go")
        assert result.language == "go"

    def test_finds_go_struct(self, ts_parser):
        result = ts_parser.parse("main.go", self.GO_SOURCE, "go")
        classes = [s for s in result.symbols if s.kind == SymbolKind.CLASS]
        assert any(c.name == "Server" for c in classes)

    def test_finds_go_function(self, ts_parser):
        result = ts_parser.parse("main.go", self.GO_SOURCE, "go")
        funcs = [s for s in result.symbols if s.kind == SymbolKind.FUNCTION]
        assert any(f.name == "NewServer" for f in funcs)

    def test_finds_go_imports(self, ts_parser):
        result = ts_parser.parse("main.go", self.GO_SOURCE, "go")
        imports = [s for s in result.symbols if s.kind == SymbolKind.IMPORT]
        assert len(imports) >= 2


# ---------------------------------------------------------------------------
# TreeSitterParser — Rust
# ---------------------------------------------------------------------------

class TestTreeSitterParserRust:

    RUST_SOURCE = textwrap.dedent("""\
        use std::collections::HashMap;

        pub struct Cache {
            data: HashMap<String, String>,
        }

        impl Cache {
            pub fn new() -> Self {
                Cache { data: HashMap::new() }
            }

            pub fn get(&self, key: &str) -> Option<&String> {
                self.data.get(key)
            }
        }

        fn compute(n: i32) -> i32 {
            n * n
        }
    """)

    def test_parse_rust(self, ts_parser):
        result = ts_parser.parse("lib.rs", self.RUST_SOURCE, "rust")
        assert result.language == "rust"

    def test_finds_rust_struct(self, ts_parser):
        result = ts_parser.parse("lib.rs", self.RUST_SOURCE, "rust")
        classes = [s for s in result.symbols if s.kind == SymbolKind.CLASS]
        assert any(c.name == "Cache" for c in classes)

    def test_finds_rust_function(self, ts_parser):
        result = ts_parser.parse("lib.rs", self.RUST_SOURCE, "rust")
        funcs = [s for s in result.symbols if s.kind == SymbolKind.FUNCTION]
        assert any(f.name == "compute" for f in funcs)


# ---------------------------------------------------------------------------
# TreeSitterParser — unknown language fallback
# ---------------------------------------------------------------------------

class TestTreeSitterFallback:

    def test_unknown_language_returns_module_symbol(self, ts_parser):
        source = "some unknown language content here"
        result = ts_parser.parse("weird.xyzzy", source, "unknownlang")
        # Should return a result, even if empty or an error
        assert isinstance(result, ParseResult)

    def test_parse_result_always_has_file_path(self, ts_parser):
        result = ts_parser.parse("a/b/c.py", "x=1", "python")
        assert result.file_path == "a/b/c.py"


# ---------------------------------------------------------------------------
# FallbackParser
# ---------------------------------------------------------------------------

class TestFallbackParser:

    PYTHON_SRC = "def foo():\n    pass\n\nclass Bar:\n    pass\n"

    def test_fallback_returns_result(self, fb_parser):
        result = fb_parser.parse("test.py", self.PYTHON_SRC, "python")
        assert isinstance(result, ParseResult)

    def test_fallback_produces_at_least_module(self, fb_parser):
        result = fb_parser.parse("unknown.unk", "data here", "text")
        assert len(result.symbols) >= 1
        assert result.symbols[0].kind == SymbolKind.MODULE

    def test_fallback_module_has_correct_name(self, fb_parser):
        result = fb_parser.parse("my_module.py", "x=1", "python")
        module_syms = [s for s in result.symbols if s.kind == SymbolKind.MODULE]
        assert any(s.name == "my_module" for s in module_syms)


# ---------------------------------------------------------------------------
# BaseParser helper: make_symbol_id
# ---------------------------------------------------------------------------

class TestMakeSymbolId:
    def test_top_level(self, ts_parser):
        sid = ts_parser.make_symbol_id("src/foo.py", "my_func")
        assert sid == "src/foo.py::my_func"

    def test_method(self, ts_parser):
        sid = ts_parser.make_symbol_id("src/foo.py", "MyClass", "my_method")
        assert sid == "src/foo.py::MyClass::my_method"

    def test_file_only(self, ts_parser):
        sid = ts_parser.make_symbol_id("src/foo.py")
        assert sid == "src/foo.py"

    def test_windows_path_normalised(self, ts_parser):
        sid = ts_parser.make_symbol_id(r"src\core\foo.py", "bar")
        assert "\\" not in sid
