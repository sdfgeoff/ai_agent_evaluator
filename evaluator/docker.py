import asyncio
import os
from typing import Awaitable, Callable
import structlog

log = structlog.get_logger(__name__)

class Docker:
    def __init__(self, image: str, name: str, project_folder: str):
        self.image = image
        self.name = "".join([c for c in name if c.isalnum() or c in "_-"])
        self.project_folder = project_folder

    def __enter__(self) -> Callable[[str], Awaitable[str]]:
        # Start the docker container
        log.info(f"start_container", name={self.name}, image=self.image)
        assert os.system(f"docker run --rm -d -v {self.project_folder}:/project --name {self.name} {self.image} sleep 1d") == 0, "Failed to start docker container"

        def run_command(command: str) -> str:
            # Run a command inside the docker container
            log.info(f"container_run_command", name={self.name}, command=command)
            result = os.popen(f"docker exec {self.name} {command}").read()
            return result
        
        async def run_command_async(command: str) -> str:
            # Run a command inside the docker container
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_command, command)
            return result
        
        return run_command_async

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop the docker container
        log.info(f"stop_container", name=self.name)
        try:
            assert os.system(f"docker stop {self.name}") == 0, "Failed to stop docker container"
        except AssertionError as e:
            log.error(f"stop_container_failed", name=self.name, error=str(e))
