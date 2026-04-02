import docker
import os
from typing import Tuple, List, Optional

class DockerSandbox:
    def __init__(self, image: str = 'python:3.10-slim', user: str = '1000:1000', cap_drop: Optional[List[str]] = None, network_disabled: bool = True):
        self.user = user
        self.cap_drop = cap_drop or ['ALL']
        self.network_disabled = network_disabled
        try:
            self.client = docker.from_env()
            self.image = image
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Docker client not initialized: {e}")
            self.client = None
            self.image = image

    def execute(self, code: str, whitelist_dirs: Optional[List[str]] = None, timeout: int = 10, mem_limit: str = '256m') -> Tuple[bool, str]:
        if not self.client:
            return False, 'Docker client not initialized'
        try:
            container = self.client.containers.run(
                self.image,
                command=['python', '-c', code],
                network_disabled=self.network_disabled,
                mem_limit=mem_limit,
                timeout=timeout,
                user=self.user,
                cap_drop=self.cap_drop,
                pids_limit=50,
                remove=True
            )
            return True, container.decode('utf-8')
        except Exception as e:
            return False, str(e)
