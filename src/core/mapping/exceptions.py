"""
Typed exceptions for the ModelRegistry.

Raising specific exception types (instead of returning opaque strings) lets
callers distinguish mapping errors from other runtime errors and handle them
appropriately.
"""


class MappingError(Exception):
    """Base class for all mapping-related errors."""


class DuplicateAliasError(MappingError):
    """Raised when a model alias that already exists in the registry is registered again."""

    def __init__(self, alias: str) -> None:
        super().__init__(
            f"Model alias '{alias}' is already registered. "
            "Use registry.update() if you intend to replace an existing entry."
        )
        self.alias = alias


class DuplicateAwsIdError(MappingError):
    """Raised when an AWS model ID that already maps to a different alias is registered."""

    def __init__(self, aws_id: str, existing_alias: str) -> None:
        super().__init__(
            f"AWS ID '{aws_id}' is already mapped to alias '{existing_alias}'. "
            "Each AWS ID must map to exactly one alias."
        )
        self.aws_id = aws_id
        self.existing_alias = existing_alias


class UnknownModelError(MappingError):
    """Raised when a model alias or AWS ID cannot be resolved in the registry."""

    def __init__(self, key: str) -> None:
        super().__init__(
            f"Model '{key}' not found in the registry. "
            "Use /models to see available models or /models all to pull from AWS."
        )
        self.key = key
