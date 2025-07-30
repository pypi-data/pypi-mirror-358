import asyncio
from typing import Any, Callable, Dict, Literal, Optional, Union

import httpx

from ..common.settings import settings
from .action import SandboxAction
from .client.models import ProcessResponse, SuccessResponse
from .client.models.process_request import ProcessRequest
from .types import SandboxConfiguration


class ProcessResponseWithLogs(ProcessResponse):
    """Extended ProcessResponse that adds a logs property."""

    logs: Optional[str] = None

    @classmethod
    def from_process_response(cls, process_response: ProcessResponse, logs: Optional[str] = None):
        """Create ProcessResponseWithLogs from an existing ProcessResponse."""
        # Create a new instance from the dict representation
        instance = cls.from_dict(process_response.to_dict())
        # Add the logs
        instance.logs = logs
        return instance


class SandboxProcess(SandboxAction):
    def __init__(self, sandbox_config: SandboxConfiguration):
        super().__init__(sandbox_config)

    def stream_logs(
        self, identifier: str, options: Optional[Dict[str, Callable[[str], None]]] = None
    ) -> Dict[str, Callable[[], None]]:
        """Stream logs from a process with callbacks for different output types."""
        if options is None:
            options = {}

        closed = False

        async def start_streaming():
            nonlocal closed

            url = f"{self.url}/process/{identifier}/logs/stream"
            headers = {**settings.headers, **self.sandbox_config.headers}

            try:
                async with httpx.AsyncClient() as client_instance:
                    async with client_instance.stream("GET", url, headers=headers) as response:
                        if response.status_code != 200:
                            raise Exception(f"Failed to stream logs: {await response.aread()}")

                        buffer = ""
                        async for chunk in response.aiter_text():
                            if closed:
                                break

                            buffer += chunk
                            lines = buffer.split("\n")
                            buffer = lines.pop()  # Keep incomplete line in buffer

                            for line in lines:
                                if line.startswith("stdout:"):
                                    content = line[7:]  # Remove 'stdout:' prefix
                                    if options.get("on_stdout"):
                                        options["on_stdout"](content)
                                    if options.get("on_log"):
                                        options["on_log"](content)
                                elif line.startswith("stderr:"):
                                    content = line[7:]  # Remove 'stderr:' prefix
                                    if options.get("on_stderr"):
                                        options["on_stderr"](content)
                                    if options.get("on_log"):
                                        options["on_log"](content)
                                else:
                                    if options.get("on_log"):
                                        options["on_log"](line)
            except Exception as e:
                # Suppress AbortError when closing
                if not (hasattr(e, "name") and e.name == "AbortError"):
                    raise e

        # Start streaming in the background
        task = asyncio.create_task(start_streaming())

        def close():
            nonlocal closed
            closed = True
            task.cancel()

        return {"close": close}

    async def exec(
        self,
        process: Union[ProcessRequest, Dict[str, Any]],
        on_log: Optional[Callable[[str], None]] = None,
    ) -> ProcessResponseWithLogs:
        if isinstance(process, dict):
            process = ProcessRequest.from_dict(process)

        async with self.get_client() as client_instance:
            response = await client_instance.post("/process", json=process.to_dict())

            # Parse JSON response only once, with better error handling
            response_data = None
            if response.content:
                try:
                    response_data = response.json()
                except Exception:
                    # If JSON parsing fails, check the response first
                    self.handle_response_error(response, None, None)
                    raise

            self.handle_response_error(response, response_data, None)
            result = ProcessResponse.from_dict(response_data)

            # Setup log streaming if on_log is provided
            stream_control = None
            if on_log is not None:
                stream_control = self.stream_logs(result.pid, {"on_log": on_log})

            # Wait for completion if requested
            logs = None
            if process.wait_for_completion:
                try:
                    # Wait for process to complete
                    result = await self.wait(result.pid)

                    # Get the logs
                    logs = await self.logs(result.pid, "all")
                except Exception as e:
                    # If waiting fails, still try to return what we have
                    if stream_control:
                        stream_control["close"]()
                    raise e

            # Close stream if it was opened and we're done
            if stream_control and process.wait_for_completion:
                stream_control["close"]()

            # Return wrapped response with logs
            return ProcessResponseWithLogs.from_process_response(result, logs)

    async def wait(
        self, identifier: str, max_wait: int = 60000, interval: int = 1000
    ) -> ProcessResponse:
        """Wait for a process to complete."""
        start_time = asyncio.get_event_loop().time() * 1000  # Convert to milliseconds
        status = "running"
        data = await self.get(identifier)

        while status == "running":
            await asyncio.sleep(interval / 1000)  # Convert to seconds
            try:
                data = await self.get(identifier)
                status = data.status or "running"
            except:
                break

            if (asyncio.get_event_loop().time() * 1000) - start_time > max_wait:
                raise Exception("Process did not finish in time")

        return data

    async def get(self, identifier: str) -> ProcessResponse:
        async with self.get_client() as client_instance:
            response = await client_instance.get(f"/process/{identifier}")
            self.handle_response_error(
                response, response.json() if response.content else None, None
            )
            return ProcessResponse.from_dict(response.json())

    async def list(self) -> list[ProcessResponse]:
        async with self.get_client() as client_instance:
            response = await client_instance.get("/process")
            self.handle_response_error(
                response, response.json() if response.content else None, None
            )
            return [ProcessResponse.from_dict(item) for item in response.json()]

    async def stop(self, identifier: str) -> SuccessResponse:
        async with self.get_client() as client_instance:
            response = await client_instance.delete(f"/process/{identifier}")
            self.handle_response_error(
                response, response.json() if response.content else None, None
            )
            return SuccessResponse.from_dict(response.json())

    async def kill(self, identifier: str) -> SuccessResponse:
        async with self.get_client() as client_instance:
            response = await client_instance.delete(f"/process/{identifier}/kill")
            self.handle_response_error(
                response, response.json() if response.content else None, None
            )
            return SuccessResponse.from_dict(response.json())

    async def logs(
        self, identifier: str, log_type: Literal["stdout", "stderr", "all"] = "all"
    ) -> str:
        async with self.get_client() as client_instance:
            response = await client_instance.get(f"/process/{identifier}/logs")
            self.handle_response_error(
                response, response.json() if response.content else None, None
            )

            data = response.json()
            if log_type == "all":
                return data.get("logs", "")
            elif log_type == "stdout":
                return data.get("stdout", "")
            elif log_type == "stderr":
                return data.get("stderr", "")

            raise Exception("Unsupported log type")
