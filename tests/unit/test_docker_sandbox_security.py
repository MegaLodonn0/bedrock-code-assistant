"""
Security tests for DockerSandbox.

Tests ensure that proper isolation parameters are passed to Docker.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.core.security.docker_sandbox import DockerSandbox


class TestDockerSandboxSecurity(unittest.TestCase):

    @patch("src.core.security.docker_sandbox.docker.from_env")
    def test_sandbox_security_defaults(self, mock_from_env):
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client

        sandbox = DockerSandbox()
        sandbox.execute("print('hello')")

        mock_client.containers.run.assert_called_once()
        kwargs = mock_client.containers.run.call_args[1]

        self.assertEqual(kwargs["user"], "1000:1000")
        self.assertEqual(kwargs["cap_drop"], ["ALL"])
        self.assertTrue(kwargs["network_disabled"])
        self.assertEqual(kwargs["pids_limit"], 50)
        self.assertTrue(kwargs["remove"])

    @patch("src.core.security.docker_sandbox.docker.from_env")
    def test_sandbox_security_custom(self, mock_from_env):
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client

        sandbox = DockerSandbox(user="2000:2000", cap_drop=["NET_RAW"], network_disabled=False)
        sandbox.execute("print('hello')", timeout=5, mem_limit="512m")

        mock_client.containers.run.assert_called_once()
        kwargs = mock_client.containers.run.call_args[1]

        self.assertEqual(kwargs["user"], "2000:2000")
        self.assertEqual(kwargs["cap_drop"], ["NET_RAW"])
        self.assertFalse(kwargs["network_disabled"])
        self.assertEqual(kwargs["mem_limit"], "512m")

        # timeout is embedded inside the 'command' kwarg list (not a Docker kwarg itself)
        command = kwargs["command"]
        self.assertIn("5", command)      # timeout value appears in command args
        self.assertIn("timeout", command)

    @patch("src.core.security.docker_sandbox.docker.from_env")
    def test_no_client_returns_error(self, mock_from_env):
        mock_from_env.side_effect = Exception("Docker unavailable")
        sandbox = DockerSandbox()
        success, msg = sandbox.execute("print('x')")
        self.assertFalse(success)
        self.assertIn("Docker", msg)


if __name__ == "__main__":
    unittest.main()
