"""
AWS Native Credential Provider Chain Implementation.

Supports the complete AWS credential resolution order:
1. Environment Variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
2. AWS Profile (~/.aws/credentials via AWS_PROFILE)
3. SSO Profile (~/.aws/config with SSO settings)
4. EC2 Instance Profile (IAM role on EC2)
5. ECS Task Role (running in ECS)
6. Lambda Execution Role (running in Lambda)
"""

import os
import boto3
import logging
from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CredentialChainResolver:
    """
    Resolves AWS credentials using the native AWS credential provider chain.
    No hardcoded credentials required.
    """

    @staticmethod
    def get_session(
        profile_name: Optional[str] = None,
        region: Optional[str] = None
    ) -> boto3.Session:
        """
        Get a boto3 Session with full credential chain support.

        Args:
            profile_name: Optional AWS profile name (overrides AWS_PROFILE env var)
            region: Optional AWS region (defaults to AWS_REGION or us-east-1)

        Returns:
            boto3.Session: Configured session with credentials from the chain

        Raises:
            NoCredentialsError: If no credentials found in the chain
        """
        profile = profile_name or os.getenv('AWS_PROFILE')
        region = region or os.getenv('AWS_REGION', 'us-east-1')

        try:
            # boto3.Session automatically checks the credential provider chain
            session = boto3.Session(
                profile_name=profile,
                region_name=region
            )

            # Validate that credentials are actually available
            credentials = session.get_credentials()
            if credentials is None:
                raise NoCredentialsError()

            logger.info(
                f"Credentials resolved from chain. "
                f"Profile: {profile or 'default'}, Region: {region}"
            )
            return session

        except NoCredentialsError:
            logger.error(
                "No AWS credentials found. Checked:\n"
                "  1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)\n"
                "  2. AWS Profile (~/.aws/credentials via AWS_PROFILE)\n"
                "  3. SSO Profile (~/.aws/config)\n"
                "  4. EC2 Instance Profile\n"
                "  5. ECS Task Role\n"
                "  6. Lambda Execution Role"
            )
            raise

    @staticmethod
    def get_client(
        service_name: str,
        profile_name: Optional[str] = None,
        region: Optional[str] = None,
        **kwargs
    ):
        """
        Get an AWS service client with credential chain resolution.

        Args:
            service_name: AWS service name (e.g., 'bedrock-runtime')
            profile_name: Optional AWS profile name
            region: Optional AWS region
            **kwargs: Additional arguments to pass to client()

        Returns:
            Configured AWS service client
        """
        session = CredentialChainResolver.get_session(profile_name, region)
        return session.client(service_name, **kwargs)

    @staticmethod
    def validate_credentials() -> Dict[str, Any]:
        """
        Validate that credentials are available and retrieve identity info.

        Returns:
            dict: Identity information including Account ID, User ARN, etc.

        Raises:
            ClientError: If credentials are invalid
        """
        try:
            sts_client = CredentialChainResolver.get_client('sts')
            identity = sts_client.get_caller_identity()

            logger.info(f"Credentials valid. Account: {identity['Account']}")
            return identity

        except ClientError as e:
            logger.error(f"Credential validation failed: {str(e)}")
            raise

    @staticmethod
    def list_available_profiles() -> list:
        """
        List all available AWS profiles from ~/.aws/credentials and ~/.aws/config.

        Returns:
            list: Available profile names
        """
        session = boto3.Session()
        profiles = session.available_profiles
        logger.info(f"Available AWS profiles: {profiles}")
        return profiles

    @staticmethod
    def get_profile_region(profile_name: str) -> Optional[str]:
        """
        Get the region configured for a specific profile.

        Args:
            profile_name: AWS profile name

        Returns:
            str: Region name or None if not configured
        """
        session = boto3.Session(profile_name=profile_name)
        region = session.region_name
        logger.debug(f"Profile '{profile_name}' region: {region}")
        return region


class CredentialChainDebugger:
    """
    Helper class to debug credential resolution issues.
    """

    @staticmethod
    def debug_credential_resolution() -> Dict[str, Any]:
        """
        Debug the credential resolution process.

        Returns:
            dict: Detailed information about credential sources and resolution
        """
        debug_info = {
            "environment_variables": {
                "AWS_ACCESS_KEY_ID": bool(os.getenv("AWS_ACCESS_KEY_ID")),
                "AWS_SECRET_ACCESS_KEY": bool(os.getenv("AWS_SECRET_ACCESS_KEY")),
                "AWS_SESSION_TOKEN": bool(os.getenv("AWS_SESSION_TOKEN")),
                "AWS_PROFILE": os.getenv("AWS_PROFILE"),
                "AWS_REGION": os.getenv("AWS_REGION"),
            },
            "available_profiles": boto3.Session().available_profiles,
            "default_region": boto3.DEFAULT_SESSION.region_name if boto3.DEFAULT_SESSION else None,
        }

        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            debug_info["credentials_resolved"] = credentials is not None
            if credentials:
                debug_info["credential_provider"] = credentials.method

            identity = session.client('sts').get_caller_identity()
            debug_info["identity"] = {
                "account": identity["Account"],
                "arn": identity["Arn"],
                "user_id": identity["UserId"],
            }
        except Exception as e:
            debug_info["error"] = str(e)

        return debug_info

    @staticmethod
    def print_debug_info():
        """Print formatted debug information to logger."""
        debug_info = CredentialChainDebugger.debug_credential_resolution()
        logger.debug(f"Credential Resolution Debug:\n{debug_info}")


# Convenience functions for common use cases

def get_bedrock_client(region: Optional[str] = None):
    """Get Bedrock runtime client with credential chain."""
    return CredentialChainResolver.get_client('bedrock-runtime', region_name=region)


def get_bedrock_agents_client(region: Optional[str] = None):
    """Get Bedrock Agents client with credential chain."""
    return CredentialChainResolver.get_client('bedrock-agent', region_name=region)


def get_s3_client(region: Optional[str] = None):
    """Get S3 client with credential chain."""
    return CredentialChainResolver.get_client('s3', region_name=region)


def get_cloudwatch_client(region: Optional[str] = None):
    """Get CloudWatch client with credential chain."""
    return CredentialChainResolver.get_client('cloudwatch', region_name=region)


def get_logs_client(region: Optional[str] = None):
    """Get CloudWatch Logs client with credential chain."""
    return CredentialChainResolver.get_client('logs', region_name=region)
