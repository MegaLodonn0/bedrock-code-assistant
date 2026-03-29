"""Security-first configuration and AWS credential handling."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Secure configuration with validation."""
    
    aws_region: str = "us-east-1"
    enable_docker: bool = True
    docker_memory_limit: str = "256m"
    rate_limit_rpm: int = 30
    rate_limit_tpm: int = 40000
    vector_db_path: str = "./data/chroma_db"
    session_path: str = "./data/sessions"
    
    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Load configuration from environment variables."""
        return cls(
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            enable_docker=os.getenv("DOCKER_ENABLED", "true").lower() == "true",
            docker_memory_limit=os.getenv("DOCKER_MEMORY_LIMIT", "256m"),
            rate_limit_rpm=int(os.getenv("RATE_LIMIT_RPM", "30")),
            rate_limit_tpm=int(os.getenv("RATE_LIMIT_TPM", "40000")),
            vector_db_path=os.getenv("VECTOR_DB_PATH", "./data/chroma_db"),
            session_path=os.getenv("SESSION_PATH", "./data/sessions"),
        )
    
    def validate(self) -> bool:
        """Validate configuration."""
        if self.rate_limit_rpm < 1:
            logger.warning("Invalid rate limit RPM, using default")
            self.rate_limit_rpm = 30
        
        if self.rate_limit_tpm < 1:
            logger.warning("Invalid rate limit TPM, using default")
            self.rate_limit_tpm = 40000
        
        Path(self.vector_db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.session_path).mkdir(parents=True, exist_ok=True)
        
        return True


class AWSCredentialChain:
    """AWS credential chain: env vars → ~/.aws/credentials → IAM role."""
    
    @staticmethod
    def get_credentials() -> Dict[str, Optional[str]]:
        """Get AWS credentials using boto3 credential chain."""
        import boto3
        
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            logger.error("❌ No AWS credentials found. Set AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY, or configure ~/.aws/credentials")
            return {"access_key": None, "secret_key": None}
        
        return {
            "access_key": credentials.access_key,
            "secret_key": credentials.secret_key,
        }
    
    @staticmethod
    def validate() -> bool:
        """Validate AWS credentials availability."""
        creds = AWSCredentialChain.get_credentials()
        if creds["access_key"] is None:
            return False
        logger.info("✅ AWS credentials validated")
        return True


def load_secure_config() -> SecurityConfig:
    """Load secure configuration."""
    config = SecurityConfig.from_env()
    config.validate()
    return config


# Global secure config
secure_config = load_secure_config()
