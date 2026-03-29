import pytest
import os
import json
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from src.core.security.docker_sandbox import DockerSandbox
from src.core.security.config import BedrockHardened

def test_docker_init():
    with patch('docker.from_env'):
        sandbox = DockerSandbox()
        assert sandbox.image == 'python:3.10-slim'

def test_bedrock_retry():
    with patch('src.core.security.config.AWSSecurity.get_session') as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        
        # Create a mock response body
        mock_body = MagicMock()
        mock_body.read.return_value = json.dumps({"completion": "Success"}).encode("utf-8")
        
        # Create a ClientError
        error_response = {"Error": {"Code": "ThrottlingException", "Message": "Rate exceeded"}}
        throttle_error = ClientError(error_response, "invoke_model")
        
        mock_client.invoke_model.side_effect = [throttle_error, {"body": mock_body}]
        bedrock = BedrockHardened()
        assert bedrock.invoke("model", "hi") == "Success"
