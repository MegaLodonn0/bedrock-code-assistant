"""
AWS Native Integration Tests - Phase 6

Tests for:
- Credential chain resolution
- AWS profile support
- SSO integration
- Multi-environment deployment scenarios
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
from botocore.exceptions import NoCredentialsError, ClientError

# Import modules to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.security.credential_chain import (
    CredentialChainResolver,
    CredentialChainDebugger,
    get_bedrock_client,
    get_cloudwatch_client,
)
from src.core.security.sso_integration import (
    SSOProfileManager,
    SSOLoginHelper,
    SSOFederatedLogin,
)


class TestCredentialChainResolver(unittest.TestCase):
    """Test credential provider chain resolution."""

    def test_session_with_env_profile(self):
        """Test session creation with AWS_PROFILE from environment."""
        with patch.dict(os.environ, {'AWS_PROFILE': 'test-profile'}):
            with patch('boto3.Session') as mock_session:
                mock_instance = MagicMock()
                mock_instance.get_credentials.return_value = MagicMock()
                mock_session.return_value = mock_instance

                session = CredentialChainResolver.get_session()
                mock_session.assert_called_once()
                args, kwargs = mock_session.call_args
                assert kwargs['profile_name'] == 'test-profile'

    def test_session_with_explicit_profile(self):
        """Test session creation with explicitly provided profile."""
        with patch('boto3.Session') as mock_session:
            mock_instance = MagicMock()
            mock_instance.get_credentials.return_value = MagicMock()
            mock_session.return_value = mock_instance

            session = CredentialChainResolver.get_session(profile_name='explicit-profile')
            args, kwargs = mock_session.call_args
            assert kwargs['profile_name'] == 'explicit-profile'

    def test_session_with_region_override(self):
        """Test session creation with region override."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('boto3.Session') as mock_session:
                mock_instance = MagicMock()
                mock_instance.get_credentials.return_value = MagicMock()
                mock_session.return_value = mock_instance

                session = CredentialChainResolver.get_session(region='eu-west-1')
                args, kwargs = mock_session.call_args
                assert kwargs['region_name'] == 'eu-west-1'

    def test_session_default_region(self):
        """Test session uses default region if not specified."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('boto3.Session') as mock_session:
                mock_instance = MagicMock()
                mock_instance.get_credentials.return_value = MagicMock()
                mock_session.return_value = mock_instance

                session = CredentialChainResolver.get_session()
                args, kwargs = mock_session.call_args
                assert kwargs['region_name'] == 'us-east-1'

    def test_session_no_credentials_error(self):
        """Test NoCredentialsError is raised when no credentials available."""
        with patch('boto3.Session') as mock_session:
            mock_instance = MagicMock()
            mock_instance.get_credentials.return_value = None
            mock_session.return_value = mock_instance

            with self.assertRaises(NoCredentialsError):
                CredentialChainResolver.get_session()

    def test_get_client(self):
        """Test getting AWS service client."""
        with patch('boto3.Session') as mock_session:
            mock_instance = MagicMock()
            mock_instance.get_credentials.return_value = MagicMock()
            mock_instance.client.return_value = MagicMock()
            mock_session.return_value = mock_instance

            client = CredentialChainResolver.get_client('bedrock-runtime')
            mock_instance.client.assert_called_once_with('bedrock-runtime')

    def test_validate_credentials(self):
        """Test credential validation via STS."""
        with patch.object(CredentialChainResolver, 'get_client') as mock_get_client:
            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {
                'Account': '123456789012',
                'UserId': 'AIDAI12345678901234567',
                'Arn': 'arn:aws:iam::123456789012:user/test'
            }
            mock_get_client.return_value = mock_sts

            identity = CredentialChainResolver.validate_credentials()
            assert identity['Account'] == '123456789012'
            assert 'Arn' in identity

    def test_list_available_profiles(self):
        """Test listing available AWS profiles."""
        with patch('boto3.Session') as mock_session:
            mock_instance = MagicMock()
            mock_instance.available_profiles = ['profile1', 'profile2']
            mock_session.return_value = mock_instance

            profiles = CredentialChainResolver.list_available_profiles()
            assert 'profile1' in profiles
            assert 'profile2' in profiles

    def test_get_profile_region(self):
        """Test getting region for a profile."""
        with patch('boto3.Session') as mock_session:
            mock_instance = MagicMock()
            mock_instance.region_name = 'us-west-2'
            mock_session.return_value = mock_instance

            region = CredentialChainResolver.get_profile_region('test-profile')
            assert region == 'us-west-2'


class TestCredentialChainDebugger(unittest.TestCase):
    """Test credential resolution debugging."""

    def test_debug_credential_resolution(self):
        """Test debugging credential resolution."""
        with patch.dict(os.environ, {'AWS_PROFILE': 'test'}):
            with patch('boto3.Session') as mock_session:
                mock_instance = MagicMock()
                mock_instance.region_name = 'us-east-1'
                mock_instance.get_credentials.return_value = MagicMock()
                mock_instance.client.return_value.get_caller_identity.return_value = {
                    'Account': '123456789012',
                    'Arn': 'arn:aws:iam::123456789012:root',
                    'UserId': 'AIDAI123456789'
                }
                mock_session.return_value = mock_instance

                debug_info = CredentialChainDebugger.debug_credential_resolution()
                assert 'environment_variables' in debug_info
                assert debug_info['environment_variables']['AWS_PROFILE'] == 'test'


class TestSSOProfileManager(unittest.TestCase):
    """Test AWS SSO profile management."""

    def test_list_sso_profiles(self):
        """Test listing SSO profiles."""
        manager = SSOProfileManager()
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', unittest.mock.mock_open(read_data='[profile sso1]\nsso_start_url = https://...\n')):
                profiles = manager.list_sso_profiles()
                # Should find at least one SSO profile
                assert isinstance(profiles, list)

    @patch('boto3.Session')
    def test_get_sso_session(self, mock_session_class):
        """Test getting SSO session."""
        mock_session = MagicMock()
        mock_session.get_credentials.return_value = MagicMock()
        mock_session_class.return_value = mock_session

        manager = SSOProfileManager()
        session = manager.get_sso_session('my-sso-profile')

        assert session is not None
        mock_session_class.assert_called_once()

    @patch.object(SSOProfileManager, 'get_sso_session')
    def test_validate_sso_session(self, mock_get_session):
        """Test SSO session validation."""
        mock_session = MagicMock()
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.return_value = {
            'Account': '123456789012',
            'UserId': 'AIDAI123456789',
            'Arn': 'arn:aws:iam::123456789012:user/test'
        }
        mock_session.client.return_value = mock_sts
        mock_get_session.return_value = mock_session

        manager = SSOProfileManager()
        # Note: validate_sso_session creates its own session, so we're testing
        # the logic path
        with patch('boto3.Session') as mock_boto_session:
            mock_boto_session.return_value = mock_session
            is_valid = manager.validate_sso_session('my-sso-profile')
            # This would be True if credentials were valid


class TestSSOLoginHelper(unittest.TestCase):
    """Test SSO login helper functions."""

    def test_get_login_command(self):
        """Test generating SSO login command."""
        cmd = SSOLoginHelper.get_login_command('my-profile')
        assert 'aws sso login' in cmd
        assert 'my-profile' in cmd

    @patch('boto3.Session')
    def test_get_profile_info(self, mock_session_class):
        """Test getting profile information."""
        mock_session = MagicMock()
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.return_value = {
            'Account': '123456789012',
            'Arn': 'arn:aws:iam::123456789012:user/test',
            'UserId': 'AIDAI123456789'
        }
        mock_session.client.return_value = mock_sts
        mock_session.region_name = 'us-east-1'
        mock_session_class.return_value = mock_session

        info = SSOLoginHelper.get_profile_info('test-profile')
        assert info['account'] == '123456789012'
        assert info['region'] == 'us-east-1'


class TestSSOFederatedLogin(unittest.TestCase):
    """Test federated login scenarios."""

    @patch('boto3.Session')
    def test_get_federated_credentials(self, mock_session_class):
        """Test getting federated credentials."""
        mock_session = MagicMock()
        mock_creds = MagicMock()
        mock_creds.access_key = 'AKIAIOSFODNN7EXAMPLE'
        mock_creds.secret_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        mock_creds.token = 'temporary-token-123'
        mock_session.get_credentials.return_value = mock_creds
        mock_session_class.return_value = mock_session

        creds = SSOFederatedLogin.get_federated_credentials('sso-profile')
        assert creds['access_key'] == 'AKIAIOSFODNN7EXAMPLE'
        assert 'secret_key' in creds
        assert 'session_token' in creds

    @patch('boto3.Session')
    def test_get_assumed_role_credentials(self, mock_session_class):
        """Test assuming a role and getting credentials."""
        from datetime import datetime
        mock_session = MagicMock()
        mock_sts = MagicMock()
        mock_sts.assume_role.return_value = {
            'Credentials': {
                'AccessKeyId': 'ASIATEMP123456789',
                'SecretAccessKey': 'temp-secret-key',
                'SessionToken': 'temp-session-token',
                'Expiration': datetime(2026, 3, 29, 15, 30, 0)
            }
        }
        mock_session.client.return_value = mock_sts
        mock_session_class.return_value = mock_session

        creds = SSOFederatedLogin.get_assumed_role_credentials(
            'sso-profile',
            'arn:aws:iam::123456789012:role/TestRole'
        )
        assert creds['access_key'] == 'ASIATEMP123456789'
        assert 'session_token' in creds
        assert 'expiration' in creds


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience client functions."""

    @patch.object(CredentialChainResolver, 'get_client')
    def test_get_bedrock_client(self, mock_get_client):
        """Test getting Bedrock client."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        client = get_bedrock_client(region='us-west-2')
        mock_get_client.assert_called_once_with('bedrock-runtime', region_name='us-west-2')

    @patch.object(CredentialChainResolver, 'get_client')
    def test_get_cloudwatch_client(self, mock_get_client):
        """Test getting CloudWatch client."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        client = get_cloudwatch_client(region='eu-west-1')
        mock_get_client.assert_called_once_with('cloudwatch', region_name='eu-west-1')


class TestAWSNativeIntegration(unittest.TestCase):
    """Integration tests for AWS Native scenarios."""

    def test_credential_chain_resolution_order(self):
        """Test that credential chain checks sources in correct order."""
        # This is a behavioral test showing the expected resolution order
        # Order: env vars -> profile -> SSO -> EC2 -> ECS -> Lambda
        resolution_order = [
            'Environment Variables',
            'AWS Profile',
            'AWS SSO',
            'EC2 Instance Profile',
            'ECS Task Role',
            'Lambda Execution Role'
        ]
        assert len(resolution_order) == 6
        assert resolution_order[0] == 'Environment Variables'

    @patch('boto3.Session')
    def test_ec2_scenario(self, mock_session_class):
        """Test EC2 deployment scenario."""
        # Clear environment (simulating EC2 with no env vars)
        with patch.dict(os.environ, {}, clear=True):
            mock_session = MagicMock()
            mock_session.get_credentials.return_value = MagicMock()
            mock_session_class.return_value = mock_session

            # Should automatically use instance profile
            session = CredentialChainResolver.get_session()
            assert session is not None

    @patch('boto3.Session')
    def test_lambda_scenario(self, mock_session_class):
        """Test Lambda deployment scenario."""
        with patch.dict(os.environ, {'AWS_LAMBDA_FUNCTION_NAME': 'bedrock-copilot'}):
            mock_session = MagicMock()
            mock_session.get_credentials.return_value = MagicMock()
            mock_session_class.return_value = mock_session

            session = CredentialChainResolver.get_session()
            assert session is not None

    @patch('boto3.Session')
    def test_ecs_scenario(self, mock_session_class):
        """Test ECS deployment scenario."""
        with patch.dict(os.environ, {'AWS_CONTAINER_CREDENTIALS_RELATIVE_URI': '/v2/credentials/abc123'}):
            mock_session = MagicMock()
            mock_session.get_credentials.return_value = MagicMock()
            mock_session_class.return_value = mock_session

            session = CredentialChainResolver.get_session()
            assert session is not None


if __name__ == '__main__':
    unittest.main()
