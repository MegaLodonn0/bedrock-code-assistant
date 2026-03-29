"""
AWS Identity Center (SSO) Integration Module.

Provides seamless support for AWS IAM Identity Center (formerly AWS SSO).
Automatically handles SSO token caching and refresh via boto3.
"""

import os
import boto3
import logging
from pathlib import Path
from botocore.exceptions import ClientError, BotoCoreError
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class SSOProfileManager:
    """
    Manages AWS IAM Identity Center (SSO) profile configuration and usage.
    """

    def __init__(self):
        self.aws_config_dir = Path.home() / ".aws"
        self.config_file = self.aws_config_dir / "config"
        self.cache_dir = self.aws_config_dir / "sso" / "cache"

    def list_sso_profiles(self) -> List[str]:
        """
        List all configured SSO profiles from ~/.aws/config.

        Returns:
            list: Profile names that use SSO
        """
        sso_profiles = []

        try:
            if not self.config_file.exists():
                logger.warning(f"AWS config file not found: {self.config_file}")
                return sso_profiles

            with open(self.config_file, 'r') as f:
                current_section = None
                for line in f:
                    line = line.strip()
                    if line.startswith("["):
                        current_section = line.strip("[]").replace("profile ", "")
                    elif line.startswith("sso_session") or line.startswith("sso_start_url"):
                        if current_section and current_section not in sso_profiles:
                            sso_profiles.append(current_section)

            logger.info(f"Found SSO profiles: {sso_profiles}")
            return sso_profiles

        except Exception as e:
            logger.error(f"Error reading SSO profiles: {str(e)}")
            return sso_profiles

    def get_sso_session(self, profile_name: str, region: Optional[str] = None) -> boto3.Session:
        """
        Get a boto3 session using SSO authentication.

        Args:
            profile_name: SSO profile name from ~/.aws/config
            region: Optional AWS region override

        Returns:
            boto3.Session: Authenticated session

        Raises:
            ClientError: If SSO authentication fails
        """
        try:
            session = boto3.Session(
                profile_name=profile_name,
                region_name=region
            )

            # Validate credentials
            credentials = session.get_credentials()
            if credentials is None:
                raise ClientError(
                    {"Error": {"Code": "NoCredentials", "Message": "SSO credentials not found"}},
                    "GetCallerIdentity"
                )

            logger.info(f"SSO session created for profile: {profile_name}")
            return session

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnauthorizedOperation':
                logger.error(
                    f"SSO authentication failed for profile '{profile_name}'. "
                    "Try: aws sso login --profile {profile_name}"
                )
            raise

    def validate_sso_session(self, profile_name: str) -> bool:
        """
        Validate that an SSO session is active and not expired.

        Args:
            profile_name: SSO profile name

        Returns:
            bool: True if session is valid, False otherwise
        """
        try:
            session = boto3.Session(profile_name=profile_name)
            sts = session.client('sts')
            sts.get_caller_identity()
            logger.info(f"SSO session valid for profile: {profile_name}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ExpiredToken':
                logger.warning(
                    f"SSO session expired for profile '{profile_name}'. "
                    f"Run: aws sso login --profile {profile_name}"
                )
            else:
                logger.error(f"SSO validation failed: {str(e)}")
            return False

    def get_cache_directory(self) -> Path:
        """Get the SSO token cache directory."""
        return self.cache_dir

    def clear_sso_cache(self) -> bool:
        """
        Clear cached SSO tokens (useful for testing or logout).

        Returns:
            bool: True if successful
        """
        try:
            if self.cache_dir.exists():
                import shutil
                shutil.rmtree(self.cache_dir)
                logger.info("SSO cache cleared")
                return True
            return True
        except Exception as e:
            logger.error(f"Error clearing SSO cache: {str(e)}")
            return False


class SSOFederatedLogin:
    """
    Handles federated login scenarios with SSO.
    """

    @staticmethod
    def get_federated_credentials(
        profile_name: str,
        region: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get federated credentials from SSO.

        Args:
            profile_name: SSO profile name
            region: Optional AWS region

        Returns:
            dict: Credentials dictionary (access_key, secret_key, session_token)
        """
        try:
            session = boto3.Session(profile_name=profile_name, region_name=region)
            credentials = session.get_credentials()

            if credentials is None:
                raise ValueError(f"No credentials found for profile: {profile_name}")

            return {
                "access_key": credentials.access_key,
                "secret_key": credentials.secret_key,
                "session_token": credentials.token,
            }

        except Exception as e:
            logger.error(f"Error getting federated credentials: {str(e)}")
            raise

    @staticmethod
    def get_assumed_role_credentials(
        profile_name: str,
        role_arn: Optional[str] = None,
        session_name: str = "bedrock-copilot",
        duration_seconds: int = 3600
    ) -> Dict[str, str]:
        """
        Assume a role using SSO credentials and return temporary credentials.

        Args:
            profile_name: SSO profile name to use for assuming role
            role_arn: Optional role ARN (if not provided, uses profile's role)
            session_name: Name for the assumed role session
            duration_seconds: Duration of temporary credentials (1-43200 seconds)

        Returns:
            dict: Temporary credentials from STS assume_role
        """
        try:
            session = boto3.Session(profile_name=profile_name)
            sts = session.client('sts')

            # If no role ARN provided, try to get it from profile config
            if not role_arn:
                # This would need to be configured in AWS config file
                logger.warning("No role ARN provided; using default profile role")

            response = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=duration_seconds
            )

            credentials = response['Credentials']
            return {
                "access_key": credentials['AccessKeyId'],
                "secret_key": credentials['SecretAccessKey'],
                "session_token": credentials['SessionToken'],
                "expiration": credentials['Expiration'].isoformat(),
            }

        except Exception as e:
            logger.error(f"Error assuming role: {str(e)}")
            raise


class SSOLoginHelper:
    """
    Provides helper methods for SSO login workflows.
    """

    @staticmethod
    def get_login_command(profile_name: str) -> str:
        """Get the command to login via SSO."""
        return f"aws sso login --profile {profile_name}"

    @staticmethod
    def get_profile_info(profile_name: str) -> Dict[str, str]:
        """
        Get detailed information about an SSO profile.

        Returns:
            dict: Profile configuration and session details
        """
        try:
            session = boto3.Session(profile_name=profile_name)
            sts = session.client('sts')
            identity = sts.get_caller_identity()

            return {
                "profile": profile_name,
                "account": identity['Account'],
                "arn": identity['Arn'],
                "user_id": identity['UserId'],
                "region": session.region_name,
            }

        except Exception as e:
            logger.error(f"Error getting profile info: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def list_all_sso_info() -> List[Dict]:
        """
        List all SSO profiles with their current status.

        Returns:
            list: Information about all SSO profiles
        """
        manager = SSOProfileManager()
        profiles = manager.list_sso_profiles()
        info = []

        for profile in profiles:
            is_valid = manager.validate_sso_session(profile)
            profile_info = SSOLoginHelper.get_profile_info(profile)
            profile_info["is_valid"] = is_valid
            info.append(profile_info)

        return info


# Convenience function
def get_sso_session(profile_name: str, region: Optional[str] = None) -> boto3.Session:
    """
    Quick function to get an SSO session.

    Usage:
        session = get_sso_session("my-sso-profile")
        bedrock = session.client("bedrock-runtime")
    """
    manager = SSOProfileManager()
    return manager.get_sso_session(profile_name, region)
