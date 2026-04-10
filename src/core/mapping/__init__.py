"""
src/core/mapping — Advanced bidirectional model mapping subsystem.

Public API:
    from src.core.mapping import get_registry, ModelEntry, ModelRegistry
    from src.core.mapping.exceptions import DuplicateAliasError, UnknownModelError
"""

from src.core.mapping.exceptions import (
    DuplicateAliasError,
    DuplicateAwsIdError,
    MappingError,
    UnknownModelError,
)
from src.core.mapping.model_entry import ModelEntry
from src.core.mapping.registry import ModelRegistry, get_registry, reset_registry

__all__ = [
    "ModelEntry",
    "ModelRegistry",
    "get_registry",
    "reset_registry",
    "MappingError",
    "DuplicateAliasError",
    "DuplicateAwsIdError",
    "UnknownModelError",
]
