"""
Hardened v3.5 tests — updated to match the current Bedrock Converse API.

test_bedrock_retry previously called invoke_model (the old API).
BedrockHardened.invoke() now calls client.converse() via the Converse API.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.core.security.docker_sandbox import DockerSandbox
from src.core.security.config import BedrockHardened


def test_docker_init():
    with patch("docker.from_env"):
        sandbox = DockerSandbox()
        # Default Docker image uses python:3.11-slim in the new config
        assert "python" in sandbox.image


def test_bedrock_invoke_converse():
    """BedrockHardened.invoke() calls client.converse() and parses the response."""
    with patch("src.core.security.config.AWSSecurity.get_session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client

        # Mock the Converse API response structure
        mock_client.converse.return_value = {
            "output": {
                "message": {
                    "content": [{"text": "Success"}]
                }
            }
        }

        bedrock = BedrockHardened()
        result = bedrock.invoke("model", "hi")
        assert result == "Success"
        mock_client.converse.assert_called_once()
