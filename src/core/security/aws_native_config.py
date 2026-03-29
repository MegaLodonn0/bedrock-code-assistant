"""AWS Native Security Configuration with Full Credential Chain Support.

Supports multiple credential sources in order:
1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
2. AWS_PROFILE for named profiles
3. ~/.aws/credentials file
4. ~/.aws/config file (with profiles and SSO)
5. EC2 IAM Role (via IMDSv2)
6. ECS Task IAM Role
7. Lambda Execution Role
"""

import os
import boto3
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AWSNativeConfig:
    """AWS Native configuration with secure credential chain."""
    
    # Credential Configuration
    aws_profile: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Infrastructure
    docker_enabled: bool = True
    docker_memory_limit: str = "256m"
    
    # Rate Limiting
    rate_limit_rpm: int = 30
    rate_limit_tpm: int = 40000
    
    # Storage
    vector_db_path: str = "./data/chroma_db"
    session_path: str = "./data/sessions"
    
    @classmethod
    def from_env(cls) -> "AWSNativeConfig":
        """Load AWS Native configuration from environment."""
        return cls(
            # NEW: AWS_PROFILE support for named profiles
            aws_profile=os.getenv("AWS_PROFILE"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            docker_enabled=os.getenv("DOCKER_ENABLED", "true").lower() == "true",
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


class AWSNativeCredentialChain:
    """AWS Native credential chain with full support for all credential sources.
    
    Credential Chain (in order):
    1. Explicit AWS_PROFILE env var
    2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    3. ~/.aws/credentials file
    4. ~/.aws/config file (with profiles and SSO)
    5. EC2 IAM Role (via IMDSv2)
    6. ECS Task IAM Role
    7. Lambda Execution Role
    """
    
    @staticmethod
    def get_session(profile_name: Optional[str] = None) -> boto3.Session:
        """Get AWS session using native credential chain.
        
        Args:
            profile_name: Optional AWS profile name from ~/.aws/credentials or ~/.aws/config
        
        Returns:
            Configured boto3 Session
        """
        # Use explicit profile if provided
        profile = profile_name or os.getenv("AWS_PROFILE")
        
        # Create session with credential chain
        session = boto3.Session(
            profile_name=profile,  # NEW: Supports named profiles
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        
        logger.info(f"✅ AWS Session created (profile: {profile or 'default'})")
        return session
    
    @staticmethod
    def validate_credentials(profile_name: Optional[str] = None) -> bool:
        """Validate AWS credentials availability.
        
        Tests that credentials can be obtained from any source in the chain.
        """
        try:
            session = AWSNativeCredentialChain.get_session(profile_name)
            credentials = session.get_credentials()
            
            if credentials is None:
                logger.error("❌ No AWS credentials found in credential chain")
                logger.error("   Please ensure ONE of these is configured:")
                logger.error("   1. Environment: AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY")
                logger.error("   2. File: ~/.aws/credentials")
                logger.error("   3. Config: ~/.aws/config (with profiles/SSO)")
                logger.error("   4. IAM Role: EC2, ECS, or Lambda execution role")
                return False
            
            logger.info("✅ AWS credentials validated successfully")
            
            # Log credential source for debugging
            cred_provider = session.get_credentials().access_key[:4] + "****"
            logger.debug(f"   Using credential source (access key starts with {cred_provider})")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Credential validation failed: {e}")
            return False
    
    @staticmethod
    def get_credential_info(profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about which credentials are being used.
        
        Useful for debugging and understanding credential source.
        """
        try:
            session = AWSNativeCredentialChain.get_session(profile_name)
            credentials = session.get_credentials()
            
            if credentials is None:
                return {
                    "status": "ERROR",
                    "message": "No credentials found",
                    "profile": profile_name or "default",
                }
            
            # Determine credential source
            access_key = credentials.access_key
            
            info = {
                "status": "OK",
                "profile": profile_name or "default",
                "region": session.region_name,
                "access_key_prefix": access_key[:4] + "****" if access_key else "N/A",
            }
            
            # Identify source
            if os.getenv("AWS_ACCESS_KEY_ID"):
                info["source"] = "Environment Variables (AWS_ACCESS_KEY_ID)"
            elif profile_name or os.getenv("AWS_PROFILE"):
                info["source"] = f"Named Profile ({profile_name or os.getenv('AWS_PROFILE')})"
            else:
                info["source"] = "Credential Chain (AWS credentials file, SSO, or IAM role)"
            
            return info
        
        except Exception as e:
            return {
                "status": "ERROR",
                "message": str(e),
                "profile": profile_name or "default",
            }


def create_bedrock_client(profile_name: Optional[str] = None):
    """Create Bedrock runtime client with AWS Native credential chain.
    
    Args:
        profile_name: Optional AWS profile name
    
    Returns:
        boto3 Bedrock Runtime client
    """
    session = AWSNativeCredentialChain.get_session(profile_name)
    return session.client("bedrock-runtime")


def create_bedrock_agent_client(profile_name: Optional[str] = None):
    """Create Bedrock Agents client for managing agents.
    
    Args:
        profile_name: Optional AWS profile name
    
    Returns:
        boto3 Bedrock Agents client
    """
    session = AWSNativeCredentialChain.get_session(profile_name)
    return session.client("bedrock-agent")


# Global config
aws_native_config = AWSNativeConfig.from_env()
aws_native_config.validate()
