"""Configuration management with environment and security support."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class Settings:
    """Centralized configuration management."""

    def __init__(self):
        """Initialize settings from environment and config files."""
        load_dotenv()
        self.env = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
    @property
    def aws_region(self) -> str:
        """Get AWS region from environment."""
        return os.getenv("AWS_REGION", "us-east-1")
    
    @property
    def aws_access_key(self) -> Optional[str]:
        """Get AWS access key - boto3 handles credential chain."""
        return os.getenv("AWS_ACCESS_KEY_ID")
    
    @property
    def aws_secret_key(self) -> Optional[str]:
        """Get AWS secret key - boto3 handles credential chain."""
        return os.getenv("AWS_SECRET_ACCESS_KEY")
    
    @property
    def bedrock_models(self) -> Dict[str, str]:
        """Get supported Bedrock models."""
        return {
            "claude-opus": "anthropic.claude-3-opus-20250219-v1:0",
            "claude-sonnet": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "claude-haiku": "anthropic.claude-3-5-haiku-20241022-v1:0",
            "nova-lite": "amazon.nova-lite-v1:0",
            "nova-pro": "amazon.nova-pro-v1:0",
        }
    
    @property
    def default_model(self) -> str:
        """Get default model (cheapest)."""
        return "nova-lite"
    
    @property
    def max_tokens(self) -> int:
        """Get max tokens for responses."""
        return int(os.getenv("MAX_TOKENS", "2000"))
    
    @property
    def docker_enabled(self) -> bool:
        """Check if Docker sandboxing is enabled."""
        return os.getenv("DOCKER_ENABLED", "true").lower() == "true"
    
    @property
    def docker_image(self) -> str:
        """Get Docker image for sandboxing."""
        return os.getenv("DOCKER_IMAGE", "python:3.11-slim")
    
    @property
    def docker_memory_limit(self) -> str:
        """Get Docker memory limit."""
        return os.getenv("DOCKER_MEMORY_LIMIT", "256m")
    
    @property
    def vector_db_path(self) -> Path:
        """Get path for vector database."""
        path = Path(os.getenv("VECTOR_DB_PATH", "./data/chroma_db"))
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def session_path(self) -> Path:
        """Get path for session files."""
        path = Path(os.getenv("SESSION_PATH", "./data/sessions"))
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv("LOG_LEVEL", "INFO" if not self.debug else "DEBUG")
    
    @property
    def rate_limit_rpm(self) -> int:
        """Get requests per minute limit."""
        return int(os.getenv("RATE_LIMIT_RPM", "30"))
    
    @property
    def rate_limit_tpm(self) -> int:
        """Get tokens per minute limit."""
        return int(os.getenv("RATE_LIMIT_TPM", "40000"))


# Global settings instance
settings = Settings()
