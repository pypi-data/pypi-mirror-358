"""
Unified Worker Service for P2P and IDE Integration

Provides a unified worker mode that accepts CLI command strings via IPC
and executes them using the existing CLI infrastructure. This eliminates
the need for multiple command parsing layers.
"""

import asyncio
import io
import json
import os
import shlex
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Dict, Optional

from ..core.exit_codes import GENERAL_ERROR, SUCCESS
from ..servers.p2p_server.crypto import MessageProcessor
from ..utils.logging_config import get_logger
from ..utils.signal_handlers import create_shutdown_manager

logger = get_logger(__name__)


class StreamCapture:
    """Captures stdout/stderr and converts to chunks for IPC."""

    def __init__(
        self, stream_name: str, message_processor: MessageProcessor, activity_callback=None
    ):
        self.stream_name = stream_name
        self.message_processor = message_processor
        self.chunk_id = 0
        self.buffer = io.StringIO()
        self.activity_callback = activity_callback

    def write(self, data: str):
        """Capture written data and potentially emit chunks."""
        self.buffer.write(data)

        # Emit chunk if buffer is getting large or on newlines
        if len(self.buffer.getvalue()) > 1024 or "\n" in data:
            self._emit_chunk()

    def flush(self):
        """Flush any remaining data."""
        if self.buffer.getvalue():
            self._emit_chunk()

    def _emit_chunk(self):
        """Emit a chunk message to stdout."""
        if not self.buffer.getvalue():
            return

        self.chunk_id += 1
        data = self.buffer.getvalue()

        # Always base64 encode data for safe transport over JSON
        import base64

        encoded_data = base64.b64encode(data.encode("utf-8")).decode("ascii")

        chunk_msg = {
            "type": "output_chunk",
            "stream": self.stream_name,
            "data": encoded_data,
            "chunk_id": self.chunk_id,
            "encoding": "base64",
        }

        # Send to real stdout with proper message framing for boundary worker
        processed_msg = self.message_processor.process_outbound_message(chunk_msg)
        # Use double newline separator expected by message handler
        print(processed_msg, end="\n\n", file=sys.__stdout__, flush=True)

        # Update activity on any output
        if self.activity_callback:
            self.activity_callback()

        # Clear buffer
        self.buffer = io.StringIO()


class WorkerService:
    """Unified worker service for executing CLI commands via IPC or P2P."""

    def __init__(self, boundary_key: str, validated_path: str, token: str, mode: str = "ipc"):
        self.boundary_key = boundary_key
        self.validated_path = validated_path
        self.token = token
        self.mode = mode  # "ipc" for subdirectory processing, "p2p" for remote worker nodes
        self.shutdown_event, self.signal_manager = create_shutdown_manager(
            service_name=f"worker-{boundary_key}"
        )
        self.message_processor = MessageProcessor()
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.p2p_manager = None
        self.p2p_port = None
        self.p2p_streaming_port = None
        self.stdin_reader: Optional[asyncio.StreamReader] = None
        self.stdin_transport = None

        # Linger configuration - always initialize
        self.linger_time: Optional[int] = None
        self.last_activity_time: float = time.time()
        self.linger_monitor_task: Optional[asyncio.Task] = None

        # Get linger time from environment if set
        linger_env = os.environ.get("CODEGUARD_WORKER_LINGER")
        if linger_env:
            try:
                self.linger_time = int(linger_env)
                logger.info(
                    f"Worker {boundary_key} configured with linger time: {self.linger_time}s"
                )
            except ValueError:
                logger.error(f"Invalid linger time value: {linger_env}")
                # linger_time already set to None above

    async def start(self):
        """Start the worker service."""
        # Set worker mode in environment so commands know which progress sender to use
        os.environ["CODEGUARD_WORKER_MODE"] = self.mode

        # Start linger monitor if configured
        if self.linger_time:
            self.linger_monitor_task = asyncio.create_task(self._linger_monitor())

        with self.signal_manager:
            if self.mode == "p2p":
                # P2P mode: Start P2P server and wait for network commands
                await self._start_p2p_mode()
            else:
                # IPC mode: Process commands via stdin/stdout
                await self._start_ipc_mode()

    async def _start_p2p_mode(self):
        """Start worker in P2P mode - network communication only."""
        # Start P2P server for this worker
        await self._start_p2p_server()

        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        # Signal ready to parent process with connection details
        ready_msg = {
            "status": "ready",
            "boundary_key": self.boundary_key,
            "port": self.p2p_port,
            "streaming_port": self.p2p_streaming_port,
        }
        self._send_message(ready_msg)

        # Wait for P2P commands (no stdin processing)
        logger.info(f"Worker {self.boundary_key} running in P2P mode on port {self.p2p_port}")

        # Keep running until shutdown via P2P network
        try:
            while (
                not self.shutdown_event.is_set()
                and self.p2p_manager
                and not self.p2p_manager.shutdown_event.is_set()
            ):
                await asyncio.sleep(1.0)
        finally:
            # Cleanup resources when shutting down
            logger.info(f"Worker {self.boundary_key} shutting down from P2P mode")
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass

            if self.linger_monitor_task:
                self.linger_monitor_task.cancel()
                try:
                    await self.linger_monitor_task
                except asyncio.CancelledError:
                    pass

            if self.p2p_manager:
                await self.p2p_manager.stop()

    async def _start_ipc_mode(self):
        """Start worker in IPC mode - stdin/stdout communication only."""
        # Set up persistent stdin reader
        await self._setup_stdin_reader()

        # Signal ready to parent process (no P2P server)
        ready_msg = {
            "status": "ready",
            "boundary_key": self.boundary_key,
        }
        self._send_message(ready_msg)

        # Main IPC command processing loop
        while not self.shutdown_event.is_set():
            try:
                # Read command from stdin with 100ms polling
                line = await self._read_stdin_line()
                if not line:
                    continue

                # Parse command
                try:
                    command_data = self.message_processor.process_inbound_message(line)
                except json.JSONDecodeError as e:
                    error_msg = {"type": "error", "error": f"Invalid JSON: {e}", "exit_code": 1}
                    self._send_message(error_msg)
                    continue

                # Update activity on any command received
                self._update_activity()

                # Handle command
                if command_data.get("cmd") == "shutdown":
                    logger.info(f"Worker {self.boundary_key} received shutdown command")
                    # Send disconnect acknowledgment
                    disconnect_msg = {"type": "disconnect", "boundary_key": self.boundary_key}
                    self._send_message(disconnect_msg)
                    self.shutdown_event.set()
                    break
                elif command_data.get("cmd") == "ping":
                    # Handle ping command - send proper COMMAND_COMPLETE response
                    result = {
                        "type": "COMMAND_COMPLETE",
                        "status": "pong",
                        "boundary_key": self.boundary_key,
                    }
                    self._send_message(result)
                else:
                    # Validate token for all command executions
                    if not self._validate_token(command_data):
                        error_msg = {
                            "type": "error",
                            "error": "Invalid or missing token",
                            "exit_code": 401,  # Unauthorized
                        }
                        self._send_message(error_msg)
                        continue

                    # Execute CLI command with stream capture
                    await self._execute_cli_command_with_capture(command_data)

            except Exception as e:
                logger.error(f"Worker command processing error: {e}")
                error_msg = {"type": "error", "error": str(e), "exit_code": 1}
                self._send_message(error_msg)

        # Cleanup happens naturally when loop exits - no P2P resources to clean
        if self.linger_monitor_task:
            self.linger_monitor_task.cancel()
            try:
                await self.linger_monitor_task
            except asyncio.CancelledError:
                pass

        await self._cleanup_stdin_reader()
        logger.info(f"Worker {self.boundary_key} shutting down from IPC mode")
        # Force exit to ensure process terminates
        sys.exit(0)

    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages."""
        while not self.shutdown_event.is_set():
            try:
                heartbeat_msg = {"type": "heartbeat", "timestamp": time.time()}
                self._send_message(heartbeat_msg)
                await asyncio.sleep(5.0)  # Heartbeat every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    def _send_message(self, msg: Dict[str, Any]):
        """Send a message to parent process."""
        processed_msg = self.message_processor.process_outbound_message(msg)
        # Use double newline separator expected by message handler
        print(processed_msg, end="\n\n", flush=True)

    async def _setup_stdin_reader(self):
        """Set up persistent stdin reader."""
        try:
            self.stdin_reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(self.stdin_reader)

            loop = asyncio.get_event_loop()
            self.stdin_transport, _ = await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            logger.debug(f"Worker {self.boundary_key} stdin reader set up")
        except Exception as e:
            logger.error(f"Failed to set up stdin reader: {e}")
            raise

    async def _cleanup_stdin_reader(self):
        """Clean up stdin reader."""
        if self.stdin_transport:
            try:
                self.stdin_transport.close()
                # Wait briefly for transport to close
                await asyncio.sleep(0.01)
                self.stdin_transport = None
                self.stdin_reader = None
                logger.debug(f"Worker {self.boundary_key} stdin reader cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up stdin reader: {e}")

    async def _read_stdin_line(self) -> str:
        """Read a line from stdin with async polling using persistent reader."""
        if not self.stdin_reader:
            return ""

        try:
            line = await asyncio.wait_for(self.stdin_reader.readline(), timeout=0.1)
            return line.decode().strip() if line else ""
        except asyncio.TimeoutError:
            return ""
        except Exception as e:
            logger.debug(f"Stdin read error: {e}")
            return ""

    async def _execute_cli_command_with_capture(self, command_data: dict):
        """Execute CLI command with stdout/stderr capture and progress forwarding."""
        try:
            # Set up stream capture with activity callback
            activity_callback = self._update_activity if self.linger_time else None
            stdout_capture = StreamCapture("stdout", self.message_processor, activity_callback)
            stderr_capture = StreamCapture("stderr", self.message_processor, activity_callback)

            # Execute command with redirected streams
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):  # type: ignore
                result = await self._execute_cli_command(command_data)

            # Flush any remaining captured data
            stdout_capture.flush()
            stderr_capture.flush()

            # Send final result directly (BoundaryWorker expects the result object itself)
            self._send_message(result)

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            error_msg = {"type": "error", "error": str(e), "exit_code": 1}
            self._send_message(error_msg)

    async def _execute_cli_command(self, command_data: dict) -> dict:
        """
        Execute CLI command using the existing CLI infrastructure.

        Args:
            command_data: Command data containing either:
                - command_line: Full CLI command string (new format)
                - command_name/subcommand/args: Legacy format (for compatibility)

        Returns:
            Result dictionary
        """
        try:
            # Handle new format: direct CLI command string
            if "command_line" in command_data:
                command_line = command_data["command_line"]
                return await self._execute_cli_string(command_line)

            # Handle legacy format for backward compatibility
            elif "command_name" in command_data:
                return await self._execute_legacy_format(command_data)

            else:
                raise ValueError(
                    "Invalid command data format - missing command_line or command_name"
                )

        except Exception as e:
            logger.error(f"CLI command execution failed: {e}")
            raise

    async def _execute_cli_string(self, command_line: str) -> dict:
        """Execute a CLI command string using the main CLI infrastructure."""
        try:
            # Parse command line using shlex to handle quoted arguments
            args = shlex.split(command_line)

            # Check if parent is in LOCAL mode - if so, don't spawn P2P workers
            if os.environ.get("CODEGUARD_NODE_MODE") == "LOCAL":
                # In LOCAL mode, execute command directly without P2P worker subprocess
                cmd = ["codeguard", "--local"] + args
            else:
                # In P2P mode, execute in a subprocess to avoid asyncio conflicts
                # Include --worker args so subprocess knows it's in worker mode
                cmd = [
                    "codeguard",
                    "--worker",
                    self.boundary_key,
                    self.validated_path,
                    self.token,
                ] + args
            print(f"🔧 WORKER_EXEC: Running command: {' '.join(cmd)}")

            # Create clean environment that excludes CODEGUARD_COMMAND_ID for subprocess A1
            env = os.environ.copy()
            env.pop("CODEGUARD_COMMAND_ID", None)  # Remove command ID so A1 doesn't inherit it
            env.pop(
                "CODEGUARD_WORKER_LINGER", None
            )  # Remove linger config so children don't inherit it

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
                env=env,
            )

            # Stream output in real-time instead of buffering
            async def stream_output(stream, output_func):
                """Stream output from subprocess in real-time with Rich markup preservation."""
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded_line = line.decode().rstrip("\n")
                    # Use raw output to bypass Rich console processing that hangs with markup=False
                    output_func(decoded_line + "\n")

            # Create tasks for real-time streaming - bypass Rich console to prevent hang
            stdout_task = asyncio.create_task(
                stream_output(
                    process.stdout, lambda x: (sys.stdout.write(x), sys.stdout.flush())[1]
                )
            )
            stderr_task = asyncio.create_task(
                stream_output(
                    process.stderr, lambda x: (sys.stderr.write(x), sys.stderr.flush())[1]
                )
            )

            # Wait for process completion and all output to be streamed
            exit_code = await process.wait()
            await stdout_task
            await stderr_task

            return {
                "exit_code": exit_code,
                "command_line": command_line,
                "status": "completed" if exit_code == 0 else "failed",
            }

        except Exception as e:
            logger.error(f"Failed to execute CLI string '{command_line}': {e}")
            return {
                "exit_code": GENERAL_ERROR,
                "command_line": command_line,
                "error": str(e),
                "status": "failed",
            }

    async def _execute_legacy_format(self, command_data: dict) -> dict:
        """Execute command using legacy format for backward compatibility."""
        # Extract command components
        command_name = command_data.get("command_name", "")
        subcommand = command_data.get("subcommand", "")
        args = command_data.get("args", {})

        # Convert to CLI command string
        cmd_parts = [command_name]
        if subcommand:
            cmd_parts.append(subcommand)

        # Convert args dict to CLI arguments
        for key, value in args.items():
            if isinstance(value, bool):
                if value:  # Only add flag if True
                    cmd_parts.append(f"--{key.replace('_', '-')}")
            elif isinstance(value, list):
                for item in value:
                    cmd_parts.extend([f"--{key.replace('_', '-')}", str(item)])
            elif value is not None:
                cmd_parts.extend([f"--{key.replace('_', '-')}", str(value)])

        command_line = " ".join(cmd_parts)
        return await self._execute_cli_string(command_line)

    async def _start_p2p_server(self):
        """Start P2P server for this worker using existing P2P infrastructure."""
        try:
            # Import P2P components
            from ..core.filesystem.access import FileSystemAccess
            from ..core.security.roots import RootsSecurityManager
            from ..servers.p2p_server import HierarchicalNetworkManager
            from ..servers.p2p_server.config import get_p2p_service
            from ..servers.p2p_server.models import NodeMode

            # Set up filesystem access for the worker's boundary using the validated path
            security_manager = RootsSecurityManager([self.validated_path])
            filesystem_access = FileSystemAccess(security_manager)

            # Load P2P configuration
            p2p_service = get_p2p_service()
            config = p2p_service.load_config()

            # Create shutdown event for P2P manager
            p2p_shutdown_event = asyncio.Event()

            # Redirect stdout to stderr temporarily to avoid interfering with JSON output
            original_stdout = sys.stdout
            sys.stdout = sys.stderr

            try:
                # Create P2P manager with worker's validated path
                self.p2p_manager = HierarchicalNetworkManager(
                    config=config,
                    managed_paths=[self.validated_path],
                    shutdown_event=p2p_shutdown_event,
                    filesystem_access=filesystem_access,
                    node_mode=NodeMode.WORKER,  # This is a worker node
                )

                # Start P2P server
                await self.p2p_manager.start()

                # Store connection details
                self.p2p_port = self.p2p_manager.port
                self.p2p_streaming_port = self.p2p_manager.streaming_port

                logger.info(
                    f"Worker {self.boundary_key} started P2P server on port {self.p2p_port}"
                )

            finally:
                # Restore stdout
                sys.stdout = original_stdout

        except Exception as e:
            logger.error(f"Failed to start P2P server for worker {self.boundary_key}: {e}")
            raise

    def _validate_token(self, command_data: dict) -> bool:
        """Validate the token in the command data."""
        provided_token = command_data.get("token")
        return provided_token == self.token

    def _update_activity(self):
        """Update last activity timestamp."""
        self.last_activity_time = time.time()

    async def _linger_monitor(self):
        """Monitor idle time and shutdown when linger threshold is exceeded."""
        check_interval = 10.0  # Check every 10 seconds

        try:
            while not self.shutdown_event.is_set():
                await asyncio.sleep(check_interval)
                if self.linger_time is None:
                    continue

                # Check if we've been idle too long
                idle_time = time.time() - self.last_activity_time
                if idle_time >= self.linger_time:
                    logger.info(
                        f"Worker {self.boundary_key} idle for {idle_time:.1f}s "
                        f"(>= {self.linger_time}s), shutting down"
                    )
                    self.shutdown_event.set()
                    break

                # Log periodic status
                logger.debug(
                    f"Worker {self.boundary_key} idle for {idle_time:.1f}s "
                    f"(linger threshold: {self.linger_time}s)"
                )
        except asyncio.CancelledError:
            logger.debug(f"Linger monitor cancelled for worker {self.boundary_key}")
            raise


async def start_worker_service(
    boundary_key: str, validated_path: str, token: str, mode: str = "p2p"
) -> int:
    """Start the unified worker service."""
    try:
        service = WorkerService(boundary_key, validated_path, token, mode)
        await service.start()
        return SUCCESS
    except Exception as e:
        logger.error(f"Worker service failed: {e}")
        return GENERAL_ERROR
