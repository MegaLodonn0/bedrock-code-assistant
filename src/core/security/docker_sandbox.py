"""Docker sandbox for secure code execution (real isolation, not subprocess)."""

import docker
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of sandboxed code execution."""
    stdout: str
    stderr: str
    exit_code: int
    runtime_ms: int


class DockerSandbox:
    """Real Docker-based sandbox for code execution."""
    
    def __init__(self, memory_limit: str = "256m", image: str = "python:3.11-slim"):
        """Initialize Docker sandbox."""
        self.memory_limit = memory_limit
        self.image = image
        self.client = None
        self._connect()
    
    def _connect(self) -> bool:
        """Connect to Docker daemon."""
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info(f"✅ Docker connected")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Docker not available: {e}")
            self.client = None
            return False
    
    def is_available(self) -> bool:
        """Check if Docker is available."""
        return self.client is not None
    
    def execute_python(
        self,
        code: str,
        timeout: int = 30,
        workdir: Optional[str] = None
    ) -> ExecutionResult:
        """Execute Python code in isolated Docker container."""
        if not self.is_available():
            raise RuntimeError("Docker not available for sandboxing")
        
        import time
        start_time = time.time()
        
        try:
            # Create container with security constraints
            container = self.client.containers.run(
                self.image,
                f"python -c {code!r}",
                detach=False,
                remove=True,
                network_disabled=True,  # No network access
                mem_limit=self.memory_limit,
                memswap_limit=self.memory_limit,
                cpuset_cpus="0",  # Single CPU
                read_only=True,  # Read-only filesystem
                tmpfs={"/tmp": "size=128m,mode=1777"},  # Temporary writable space
                timeout=timeout,
            )
            
            # Get logs
            logs = container.logs(stdout=True, stderr=True)
            stdout = logs.decode() if isinstance(logs, bytes) else logs
            
            runtime_ms = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                stdout=stdout,
                stderr="",
                exit_code=0,
                runtime_ms=runtime_ms
            )
        
        except docker.errors.ContainerError as e:
            runtime_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else str(e),
                exit_code=e.exit_status,
                runtime_ms=runtime_ms
            )
        
        except Exception as e:
            runtime_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=1,
                runtime_ms=runtime_ms
            )
    
    def execute_bash(
        self,
        command: str,
        timeout: int = 30
    ) -> ExecutionResult:
        """Execute bash command in isolated Docker container."""
        if not self.is_available():
            raise RuntimeError("Docker not available for sandboxing")
        
        import time
        start_time = time.time()
        
        try:
            container = self.client.containers.run(
                self.image,
                ["sh", "-c", command],
                detach=False,
                remove=True,
                network_disabled=True,
                mem_limit=self.memory_limit,
                memswap_limit=self.memory_limit,
                cpuset_cpus="0",
                read_only=True,
                tmpfs={"/tmp": "size=128m,mode=1777"},
                timeout=timeout,
            )
            
            logs = container.logs(stdout=True, stderr=True)
            stdout = logs.decode() if isinstance(logs, bytes) else logs
            
            runtime_ms = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                stdout=stdout,
                stderr="",
                exit_code=0,
                runtime_ms=runtime_ms
            )
        
        except docker.errors.ContainerError as e:
            runtime_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else str(e),
                exit_code=e.exit_status,
                runtime_ms=runtime_ms
            )
        
        except Exception as e:
            runtime_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=1,
                runtime_ms=runtime_ms
            )
    
    def cleanup(self):
        """Clean up Docker resources."""
        if self.client:
            try:
                # Remove dangling containers
                self.client.containers.prune()
                logger.info("✅ Docker resources cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Could not cleanup Docker: {e}")


# Global sandbox instance
_sandbox_instance = None


def get_sandbox(memory_limit: str = "256m", image: str = "python:3.11-slim") -> DockerSandbox:
    """Get or create sandbox instance."""
    global _sandbox_instance
    if _sandbox_instance is None:
        _sandbox_instance = DockerSandbox(memory_limit, image)
    return _sandbox_instance
