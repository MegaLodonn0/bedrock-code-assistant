"""
Hardened AWS native credential tests.

Tests the AWSSecurity.get_session() credential selection logic.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.core.security.config import AWSSecurity


def test_aws_profile_support():
    """When AWS_ACCESS_KEY_ID is absent and AWS_PROFILE is set, use profile session."""
    env_map = {
        "AWS_PROFILE": "demo-profile",
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": None,       # explicitly absent
        "AWS_SECRET_ACCESS_KEY": None,   # explicitly absent
    }
    with patch("os.getenv", side_effect=lambda k, d=None: env_map.get(k, d)):
        with patch("boto3.Session") as mock_boto3:
            AWSSecurity.get_session()
            mock_boto3.assert_called_with(profile_name="demo-profile", region_name="us-east-1")


def test_iam_role_detection():
    """When no credentials or profile are present, fall back to default credential chain."""
    with patch("os.getenv", return_value=None):
        with patch("boto3.Session") as mock_boto3:
            AWSSecurity.get_session()
            mock_boto3.assert_called_with(region_name="us-east-1")


def test_direct_credentials_take_priority():
    """When AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY are set, use them directly."""
    env_map = {
        "AWS_ACCESS_KEY_ID": "AKIATEST",
        "AWS_SECRET_ACCESS_KEY": "secrettest",
        "AWS_REGION": "eu-west-1",
        "AWS_PROFILE": None,
    }
    with patch("os.getenv", side_effect=lambda k, d=None: env_map.get(k, d)):
        with patch("boto3.Session") as mock_boto3:
            AWSSecurity.get_session()
            mock_boto3.assert_called_with(
                aws_access_key_id="AKIATEST",
                aws_secret_access_key="secrettest",
                region_name="eu-west-1",
            )