"""Configuration management with environment and security support."""

import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv


class Settings:
    """Centralized configuration management."""

    def __init__(self) -> None:
        """Initialize settings from environment and config files."""
        load_dotenv()
        self.env = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

    # ------------------------------------------------------------------
    # AWS credentials
    # ------------------------------------------------------------------

    @property
    def aws_region(self) -> str:
        """AWS region for Bedrock API calls."""
        return os.getenv("AWS_REGION", "us-east-1")

    @property
    def aws_access_key(self) -> Optional[str]:
        """AWS access key ID (boto3 handles the full credential chain)."""
        return os.getenv("AWS_ACCESS_KEY_ID")

    @property
    def aws_secret_key(self) -> Optional[str]:
        """AWS secret access key (boto3 handles the full credential chain)."""
        return os.getenv("AWS_SECRET_ACCESS_KEY")

    # ------------------------------------------------------------------
    # Model registry — delegates to the mapping subsystem
    # ------------------------------------------------------------------

    @property
    def registry(self):
        """
        Return the process-global ModelRegistry (lazy singleton).

        Import is deferred to avoid circular import at module load time.
        """
        from src.core.mapping.registry import get_registry
        return get_registry()

    @property
    def bedrock_models(self) -> Dict[str, str]:
        """
        Backwards-compatible alias → aws_id mapping.

        Delegates to ModelRegistry so callers that iterated
        settings.bedrock_models directly continue to work unchanged.
        """
        return self.registry.to_dict()

    @property
    def default_model(self) -> str:
        """Default model alias (cheapest and most available)."""
        from src.core.mapping.models_catalog import DEFAULT_MODEL_ALIAS
        return DEFAULT_MODEL_ALIAS

    # ------------------------------------------------------------------
    # Token limits
    # ------------------------------------------------------------------

    @property
    def max_tokens(self) -> int:
        """Maximum tokens to request in a single AI response."""
        return int(os.getenv("MAX_TOKENS", "2000"))

    # ------------------------------------------------------------------
    # Docker sandbox
    # ------------------------------------------------------------------

    @property
    def docker_enabled(self) -> bool:
        """Whether Docker sandboxing is enabled for /execute."""
        return os.getenv("DOCKER_ENABLED", "true").lower() == "true"

    @property
    def docker_image(self) -> str:
        """Docker image used for the sandbox container."""
        return os.getenv("DOCKER_IMAGE", "python:3.11-slim")

    @property
    def docker_memory_limit(self) -> str:
        """Memory limit for the Docker sandbox container."""
        return os.getenv("DOCKER_MEMORY_LIMIT", "256m")

    @property
    def docker_user(self) -> str:
        """UID:GID to run the Docker container as (non-root by default)."""
        return os.getenv("DOCKER_USER", "1000:1000")

    @property
    def docker_capabilities(self) -> List[str]:
        """Linux capabilities to drop inside the Docker sandbox."""
        caps = os.getenv("DOCKER_CAP_DROP", "ALL")
        return [c.strip() for c in caps.split(",") if c.strip()]

    @property
    def docker_network_disabled(self) -> bool:
        """Whether to disable network access inside the Docker sandbox."""
        return os.getenv("DOCKER_NETWORK_DISABLED", "true").lower() == "true"

    # ------------------------------------------------------------------
    # Storage paths
    # ------------------------------------------------------------------

    @property
    def vector_db_path(self) -> Path:
        """Filesystem path for the ChromaDB vector database."""
        path = Path(os.getenv("VECTOR_DB_PATH", "./data/chroma_db"))
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def session_path(self) -> Path:
        """Filesystem path for saved session JSON files."""
        path = Path(os.getenv("SESSION_PATH", "./data/sessions"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ------------------------------------------------------------------
    # Logging & rate limiting
    # ------------------------------------------------------------------

    @property
    def log_level(self) -> str:
        """Python logging level."""
        return os.getenv("LOG_LEVEL", "DEBUG" if self.debug else "INFO")

    @property
    def rate_limit_rpm(self) -> int:
        """Maximum Bedrock API requests per minute."""
        return int(os.getenv("RATE_LIMIT_RPM", "30"))

    @property
    def rate_limit_tpm(self) -> int:
        """Maximum Bedrock API tokens per minute."""
        return int(os.getenv("RATE_LIMIT_TPM", "40000"))


# Global settings singleton
settings = Settings()
