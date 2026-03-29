import pytest
import os
from unittest.mock import patch, MagicMock
from src.core.security.config import AWSSecurity, BedrockHardened
from src.core.security.docker_sandbox import DockerSandbox

def test_aws_security_get_session():
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda k, d=None: 'demo-key' if k == 'AWS_ACCESS_KEY_ID' else 'demo-secret' if k == 'AWS_SECRET_ACCESS_KEY_ID' else 'us-east-1'
        session = AWSSecurity.get_session()
        assert session.region_name == 'us-east-1'

def test_docker_sandbox_execute_no_client():
    sandbox = DockerSandbox()
    sandbox.client = None
    success, output = sandbox.execute('print("hi")')
    assert not success
    assert 'Docker client not initialized' in output
