"""
src/core/code_map — Multi-language code mapping and context engine.

Public API:

    from src.core.code_map import get_code_mapper, CodeMapper
    from src.core.code_map.symbols import Symbol, ContextBundle, SymbolKind
    from src.core.code_map.languages import detect_language

Usage:

    mapper = get_code_mapper()
    mapper.index_file("src/core/executor.py")
    bundle = mapper.get_context(
        file="src/core/executor.py",
        symbol="Executor.ask_ai",
        query="How does cost tracking work?",
    )
    prompt = bundle.to_prompt()   # inject into Bedrock prompt
"""

from src.core.code_map.code_mapper import CodeMapper, get_code_mapper, reset_code_mapper
from src.core.code_map.languages import detect_language, is_parseable
from src.core.code_map.symbols import ContextBundle, ParseResult, Symbol, SymbolKind

__all__ = [
    "CodeMapper",
    "get_code_mapper",
    "reset_code_mapper",
    "detect_language",
    "is_parseable",
    "Symbol",
    "SymbolKind",
    "ParseResult",
    "ContextBundle",
]
