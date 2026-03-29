import pytest
import os
from unittest.mock import patch, MagicMock
from src.core.security.config import AWSSecurity

def test_aws_profile_support():
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda k, d=None: 'demo-profile' if k == 'AWS_PROFILE' else 'us-east-1'
        with patch('boto3.Session') as mock_boto3:
            AWSSecurity.get_session()
            mock_boto3.assert_called_with(profile_name='demo-profile', region_name='us-east-1')

def test_iam_role_detection():
    with patch('os.getenv', return_value=None):
        with patch('boto3.Session') as mock_boto3:
            AWSSecurity.get_session()
            mock_boto3.assert_called_with(region_name='us-east-1')

def test_iam_policy_validity():
    import json
    with open('bedrock_copilot_policy.json', 'r') as f:
        policy = json.load(f)
    assert policy['Version'] == '2012-10-17'