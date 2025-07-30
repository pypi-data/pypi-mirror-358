"""
Boundary Worker

Persistent worker process that handles multiple commands.
Each worker handles commands for exactly one boundary to prevent cache corruption.
"""

import asyncio
import json
import sys
import time
from typing import Any, Dict, Optional

from ....core.exit_codes import TIMEOUT_ERROR
from ....utils.logging_config import get_logger
from ..config import P2PConfig
from ..p2p_manager.streaming_cache import StreamingServerCache

logger = get_logger(__name__)


class BoundaryWorker:
    """Persistent worker process that handles multiple commands."""

    def __init__(
        self,
        boundary_key: str,
        validated_path: str,
        config: P2PConfig,
        shutdown_event: asyncio.Event,
        token: str,
        network_manager,
    ):
        self.boundary_key = boundary_key
        self.validated_path = validated_path
        self.config = config
        self.shutdown_event = shutdown_event
        self.token = token
        self.network_manager = network_manager
        self.process: Optional[asyncio.subprocess.Process] = None
        self.stdin_writer: Optional[asyncio.StreamWriter] = None
        self.stdout_reader: Optional[asyncio.StreamReader] = None
        self.stderr_reader: Optional[asyncio.StreamReader] = None
        self.worker_port: Optional[int] = None
        self.worker_streaming_port: Optional[int] = None

    async def start(self) -> None:
        """Start the persistent worker process."""
        try:
            # Use the new unified worker service via main CLI entry point
            # This leverages the existing CLI infrastructure

            # Start worker process with IPC communication including token and validated path
            self.process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "codeguard",
                "--worker",
                self.boundary_key,
                self.validated_path,
                self.token,
                "--linger",
                str(self.config.worker_linger_time),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.stdin_writer = self.process.stdin
            self.stdout_reader = self.process.stdout
            self.stderr_reader = self.process.stderr

            # Wait for worker to be ready with 100ms polling instead of long timeout
            start_time = time.time()
            while time.time() - start_time < self.config.worker_startup_timeout:
                try:
                    if self.stdout_reader is None:
                        continue
                    ready_line = await asyncio.wait_for(
                        self.stdout_reader.readline(), timeout=0.1  # 100ms polling
                    )
                    ready_msg = json.loads(ready_line.decode())
                    if ready_msg.get("status") == "ready":
                        # Extract worker connection details
                        self.worker_port = ready_msg.get("port")
                        self.worker_streaming_port = ready_msg.get("streaming_port")
                        break
                    elif ready_msg.get("status") == "error":
                        raise RuntimeError(f"Worker failed to start: {ready_msg}")
                except asyncio.TimeoutError:
                    continue  # Keep polling
            else:
                raise RuntimeError(
                    f"Worker startup timeout after {self.config.worker_startup_timeout}s"
                )

            # Start stderr forwarding task to make worker debug output visible
            self._start_stderr_forwarding()

            logger.info(f"Boundary worker {self.boundary_key} started successfully")

        except Exception as e:
            logger.error(f"Failed to start worker {self.boundary_key}: {e}")
            await self.shutdown(force=True)
            raise

    def is_running(self) -> bool:
        """Check if worker process is still running."""
        if self.process is None:
            return False

        # If returncode is already set, definitely not running
        if self.process.returncode is not None:
            return False

        # Check if stdin writer is closed (reliable indicator process died)
        if self.stdin_writer and self.stdin_writer.is_closing():
            return False

        return True

    async def get_connection_info(self) -> Dict[str, Any]:
        """Get worker connection information for direct client connections."""
        if not self.is_running():
            raise RuntimeError(f"Worker {self.boundary_key} is not running")

        return {
            "address": "127.0.0.1",  # Worker runs locally
            "port": self.worker_port,
            "streaming_port": self.worker_streaming_port,
            "token": self.token,
            "status": "running",
            "boundary_key": self.boundary_key,
        }

    def _start_stderr_forwarding(self):
        """Forward worker stderr to main process for debugging."""

        async def stderr_forwarder():
            if self.stderr_reader:
                try:
                    while not self.shutdown_event.is_set():
                        try:
                            # Use readline with timeout to prevent busy loops
                            line = await asyncio.wait_for(
                                self.stderr_reader.readline(), timeout=1.0
                            )
                            if not line:  # EOF reached
                                break
                            decoded = line.decode("utf-8", errors="replace").rstrip()
                            if decoded:
                                print(f"🔧 WORKER[{self.boundary_key}]: {decoded}", file=sys.stderr)
                        except asyncio.TimeoutError:
                            # No stderr output for 1 second, continue loop
                            continue
                        except Exception as e:
                            logger.debug(f"Stderr read error for {self.boundary_key}: {e}")
                            await asyncio.sleep(0.1)  # Brief pause on error
                except Exception as e:
                    logger.debug(f"Stderr forwarding ended for {self.boundary_key}: {e}")

        asyncio.create_task(stderr_forwarder())

    async def ping(self, _data: dict) -> bool:
        """Ping worker to check if it's alive and reset its linger timer."""
        if not self.is_running():
            return False

        try:
            # Send ping command via ZMQ
            worker_address = f"127.0.0.1:{self.worker_port}"
            response = await self.network_manager.message_handler.send_to_node(
                worker_address, {"cmd": "ping", "token": self.token}
            )
            return (
                response
                and response.get("type") == "COMMAND_COMPLETE"
                and response.get("status") == "pong"
            )
        except Exception as e:
            logger.error(f"Ping failed for {self.boundary_key}: {e}")
            return False

    async def shutdown(self, force: bool = False) -> bool:
        """Shutdown worker. Returns True if successful."""
        if not self.is_running():
            return True

        try:
            if not force:
                # Try graceful shutdown first
                if self.stdin_writer is not None:
                    shutdown_cmd = json.dumps({"cmd": "shutdown"}) + "\n"
                    self.stdin_writer.write(shutdown_cmd.encode())
                    await self.stdin_writer.drain()

                # Wait for graceful exit with 100ms polling AND listen for disconnect message
                start_time = time.time()
                while time.time() - start_time < 5.0:  # 5 second timeout
                    # Check if process exited
                    if self.process is not None and self.process.returncode is not None:
                        logger.info(f"Worker {self.boundary_key} shut down gracefully")
                        return True

                    # Check for disconnect message from worker
                    try:
                        if self.stdout_reader is not None:
                            line = await asyncio.wait_for(
                                self.stdout_reader.readline(), timeout=0.1
                            )
                            if line:
                                msg = json.loads(line.decode())
                                if msg.get("type") == "disconnect":
                                    logger.info(f"Worker {self.boundary_key} acknowledged shutdown")
                                    # Still wait for process to exit, but we know it's cooperating
                                    if self.process:
                                        await asyncio.wait_for(self.process.wait(), timeout=2.0)
                                    return True
                    except (asyncio.TimeoutError, json.JSONDecodeError):
                        pass  # Continue polling

                    await asyncio.sleep(0.1)  # 100ms polling

                logger.warning(f"Worker {self.boundary_key} graceful shutdown timeout")

            # Force shutdown
            if self.process and self.process.returncode is None:
                self.process.kill()
                await self.process.wait()
                logger.warning(f"Worker {self.boundary_key} force killed")

            return True

        except Exception as e:
            logger.error(f"Shutdown failed for {self.boundary_key}: {e}")
            return False
