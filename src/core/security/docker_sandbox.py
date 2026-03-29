import docker
import os
from typing import Tuple, List, Optional

class DockerSandbox:
    def __init__(self, image: str = 'python:3.10-slim'):
        try:
            self.client = docker.from_env()
            self.image = image
        except Exception as e:
            self.client = None
            self.image = image

    def execute(self, code: str, whitelist_dirs: Optional[List[str]] = None, timeout: int = 10, mem_limit: str = '256m') -> Tuple[bool, str]:
        if not self.client:
            return False, 'Docker client not initialized'
        try:
            container = self.client.containers.run(
                self.image,
                command=['python', '-c', code],
                network_disabled=True,
                mem_limit=mem_limit,
                timeout=timeout,
                remove=True
            )
            return True, container.decode('utf-8')
        except Exception as e:
            return False, str(e)
