"""
P2P Remote Executor

Executes CLI commands on remote P2P nodes with full streaming support,
preserving progress bars, real-time output, and user experience identical
to local execution.
"""

import asyncio
import base64
import json
import shlex
import sys
import time
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional

from ....core.components import get_component_registry
from ....core.console_shared import clear_console_line, cprint, spinner_print
from ....core.exit_codes import GENERAL_ERROR, NETWORK_ERROR, TIMEOUT_ERROR
from ....core.formatters import FormatterRegistry
from ....core.formatters.base import DataType
from ....core.runtime import get_default_console
from ....utils.logging_config import get_logger
from ..config import get_p2p_service
from .command_router import RoutingDecision
from .streaming_protocol import (
    CommandComplete,
    ComponentComplete,
    ComponentProgress,
    ComponentStart,
    ProgressUpdate,
    StatusMessage,
    StreamingClient,
    StreamJson,
)

logger = get_logger(__name__)


class RemoteExecutionResult:
    """Result of remote command execution with streaming data."""

    def __init__(
        self,
        exit_code: int = 0,
        result_data: Optional[Dict] = None,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
        output_chunks: Optional[List[str]] = None,
    ):
        self.exit_code = exit_code
        self.result_data = result_data or {}
        self.error = error
        self.execution_time = execution_time
        self.output_chunks = output_chunks or []

    def is_success(self) -> bool:
        """Check if the execution was successful."""
        return self.exit_code == 0 and not self.error

    def get_combined_output(self) -> str:
        """Get all output chunks combined."""
        return "".join(self.output_chunks)


class ProgressHandler:
    """Handles progress updates from remote execution."""

    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self.current_progress = 0
        self.current_message = ""
        self.current_stage = None

    def update_progress_state(self, progress_msg: ProgressUpdate):
        """Update internal progress state tracking."""
        self.current_progress = progress_msg.progress
        self.current_message = progress_msg.message
        self.current_stage = progress_msg.stage

    def _format_progress_bar(self, percent: float, width: int = 30) -> str:
        """Format a progress bar."""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def _get_spinner(self) -> str:
        """Get a spinning character for indeterminate progress."""
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return spinners[int(time.time() * 4) % len(spinners)]

    def finish(self):
        """Finish progress display."""
        if self.show_progress:
            print(file=sys.stderr)  # New line after progress on stderr


class OutputHandler:
    """Handles streaming output from remote execution."""

    def __init__(
        self,
        capture_output: bool = False,
        original_format: str = "console",
        streaming_callback: Optional[Callable] = None,
    ):
        self.capture_output = capture_output
        self.captured_chunks = []
        self.original_format = original_format
        self.json_buffer = ""  # Buffer for JSON chunks
        self.streaming_callback = streaming_callback

        # Get formatter for the original format using registry instance
        try:
            registry = FormatterRegistry()
            self.formatter = registry.get_formatter(original_format)
        except Exception:
            # Fallback to console if formatter not found
            registry = FormatterRegistry()
            self.formatter = registry.get_formatter("console")

    async def handle_output(self, chunk_msg: StreamJson):
        """Handle an output chunk message."""
        # Clear any active spinner when we start outputting actual data
        clear_console_line()

        data = chunk_msg.data

        # Decode base64 if encoding is specified
        if hasattr(chunk_msg, "encoding") and chunk_msg.encoding == "base64":
            data = base64.b64decode(data.encode("ascii")).decode("utf-8")

        if self.capture_output:
            self.captured_chunks.append(data)

        # Try to parse as OUTPUT_LINE envelope first (single JSON parse)
        output_envelope = self._try_parse_output_line_envelope(data)
        if output_envelope:
            self._handle_output_line_envelope(output_envelope)
            return  # OUTPUT_LINE handled, don't process further
        # StreamJson contains complete JSON structures, always process through JSON handler
        elif self.original_format != "json":
            await self._handle_json_output(data)
        else:
            print(data, end="", flush=True)

    def _try_parse_output_line_envelope(self, data: str) -> Optional[Dict]:
        """Try to parse data as OUTPUT_LINE envelope. Returns parsed dict or None."""
        try:
            parsed = json.loads(data.strip())
            if (
                isinstance(parsed, dict)
                and parsed.get("type") == "OUTPUT_LINE"
                and "content" in parsed
            ):
                return parsed
        except (json.JSONDecodeError, AttributeError):
            pass
        return None

    def _handle_output_line_envelope(self, envelope: Dict):
        """Handle OUTPUT_LINE envelope - extract content and print directly."""
        content = envelope.get("content", "")
        # Print exact content - preserves blank lines and formatting
        console = get_default_console()
        console.print(content)

    def _looks_like_json(self, data: str) -> bool:
        """Check if data looks like JSON output."""
        stripped = data.strip()
        # Only consider as JSON if it starts with { or [ (not just contains quotes)
        return stripped.startswith("{") or stripped.startswith("[")

    async def _handle_json_output(self, data: str):
        """Handle mixed output that may contain JSON to be formatted."""
        # Check if we're currently in JSON mode (buffering JSON)
        if self.json_buffer:
            # We're already buffering JSON, add to buffer
            self.json_buffer += data
        else:
            # Look for JSON start in the new data
            json_start = data.find("{")
            if json_start == -1:
                json_start = data.find("[")

            if json_start != -1:
                # Found JSON start, print everything before it as regular output
                if json_start > 0:
                    print(data[:json_start], end="", flush=True)

                # Start buffering the JSON part
                self.json_buffer = data[json_start:]
            else:
                # No JSON found, print as regular output
                display_console = get_default_console()
                display_console.print(data)
                return

        # Check if we have a complete JSON structure in the buffer
        stripped_buffer = self.json_buffer.strip()

        if (stripped_buffer.startswith("{") and stripped_buffer.endswith("}")) or (
            stripped_buffer.startswith("[") and stripped_buffer.endswith("]")
        ):

            try:
                # Attempt to parse the entire buffer as JSON
                json_data = json.loads(stripped_buffer)

                # Route streaming protocol messages to handlers
                if json_data.get("type") in [
                    "OUTPUT_LINE",
                    "COMPONENT_START",
                    "COMPONENT_PROGRESS",
                    "COMPONENT_COMPLETE",
                ]:
                    if json_data.get("type") == "OUTPUT_LINE":
                        # Handle OUTPUT_LINE directly - print content
                        content = json_data.get("content", "")
                        console = get_default_console()
                        console.print(content)
                    elif self.streaming_callback:
                        await self.streaming_callback(json_data)
                    # Clear buffer and return - don't format streaming protocol messages
                    self.json_buffer = ""
                    return

                # Successfully parsed - convert to original format using formatter
                if self.formatter and hasattr(self.formatter, "format_collection"):
                    try:
                        # Pass JSON data directly - no wrapping needed as component system already provides correct structure
                        data_to_format = json_data

                        formatted_output = await self.formatter.format_collection(
                            [data_to_format], DataType.ANALYSIS_RESULTS
                        )
                        print(formatted_output, end="", flush=True)
                    except Exception as e:
                        print(f"DEBUG: Formatter error - {e}", file=sys.stderr)
                        print(f"DEBUG: json_data type: {type(json_data)}", file=sys.stderr)
                        print(
                            f"DEBUG: json_data keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'not a dict'}",
                            file=sys.stderr,
                        )
                        # Fallback to raw JSON output
                        print(json.dumps(json_data, indent=2), end="", flush=True)
                else:
                    # Fallback if formatter doesn't have format_collection method
                    print(json.dumps(json_data, indent=2), end="", flush=True)

                # Clear buffer after successful formatting
                self.json_buffer = ""

            except json.JSONDecodeError:
                # JSON not complete yet, keep buffering
                pass
            except Exception:
                # Formatting failed, print buffered data and continue
                print(self.json_buffer, end="", flush=True)
                self.json_buffer = ""

        # Safety valve - clear buffer if it's getting too large (prevent memory issues)
        if len(self.json_buffer) > 4 * 1024 * 1024:  # 4MB limit
            print(self.json_buffer, end="", flush=True)
            self.json_buffer = ""

    def get_captured_output(self) -> str:
        """Get all captured output."""
        return "".join(self.captured_chunks)


class StatusHandler:
    """Handles status messages from remote execution."""

    def __init__(self, show_status: bool = True):
        self.show_status = show_status

    def handle_status(self, status_msg: StatusMessage):
        """Handle a status message."""
        if self.show_status:
            if status_msg.level == "INFO":
                # Use spinner for INFO status messages like "Starting command execution"
                spinner_print("🔄", status_msg.message)
            elif status_msg.level in ["WARNING", "ERROR"]:
                prefix = f"[{status_msg.level}]"
                source = f" ({status_msg.source})" if status_msg.source else ""
                print(f"{prefix}{source} {status_msg.message}", file=sys.stderr)


class RemoteExecutor:
    """Executes commands on remote P2P nodes with streaming support."""

    def __init__(self, network_manager=None):
        self.network_manager = network_manager
        self.registry = get_component_registry()

    async def execute_command(
        self,
        progress_callback: Callable[..., Coroutine[Any, Any, None]],
        command_name: str,
        routing_decision: RoutingDecision,
        args: Dict,
        subcommand: Optional[str] = None,
        show_progress: bool = True,
        capture_output: bool = False,
    ) -> RemoteExecutionResult:
        """
        Execute a command on the remote node specified in the routing decision.

        Args:
            progress_callback: Progress callback for status updates
            command_name: Main command name
            routing_decision: Routing decision from command router
            args: Command arguments
            subcommand: Subcommand if applicable
            show_progress: Whether to show progress bars/status
            capture_output: Whether to capture output for return

        Returns:
            RemoteExecutionResult with execution details
        """
        if routing_decision.is_local():
            raise ValueError("Cannot execute remotely with a local routing decision")

        remote_address = routing_decision.get_remote_address()

        if not remote_address:
            raise ValueError("No remote address in routing decision")

        # Prepare command for remote execution
        remote_command = self._prepare_remote_command(command_name, subcommand, args)

        # Get worker connection info from server first
        cprint(f"🔧 Getting worker info from server at {remote_address}")
        worker_info = await self._get_worker_info(remote_address, remote_command)
        cprint(f"🔧 Worker info result: {worker_info}")

        if not worker_info:
            return RemoteExecutionResult(
                exit_code=NETWORK_ERROR, error="Failed to get worker information"
            )

        # Connect directly to worker
        worker_address = f"{worker_info['address']}:{worker_info['port']}"
        worker_streaming_port = worker_info.get("streaming_port")
        worker_token = worker_info["token"]

        # Add token to remote command
        remote_command["token"] = worker_token

        # Execute with or without streaming based on worker capability
        if worker_streaming_port:
            return await self._execute_with_streaming(
                progress_callback,
                worker_address,
                worker_streaming_port,
                remote_command,
                show_progress,
                capture_output,
            )
        else:
            return await self._execute_without_streaming(worker_address, remote_command)

    def _prepare_remote_command(
        self, command_name: str, subcommand: Optional[str], args: Dict
    ) -> Dict:
        """Prepare command data for remote execution."""
        # Use the original command line from args (should be passed by CLI)
        original_command_line = args.get("_original_command_line", "")

        # Remove executable part and keep the rest
        # Example: "python -m src context analyze ./" -> "context analyze ./"
        cmd_parts = shlex.split(original_command_line)

        # Find where the actual command starts (after python -m src or similar)
        command_start_idx = 0
        for i, part in enumerate(cmd_parts):
            if part in [command_name] or (subcommand and part == subcommand):
                command_start_idx = i
                break

        # Take everything from the command onwards
        if command_start_idx > 0:
            clean_command_parts = cmd_parts[command_start_idx:]
        else:
            clean_command_parts = cmd_parts

        # Store original format preference before forcing JSON
        original_format = None
        if "--format" in clean_command_parts:
            format_idx = clean_command_parts.index("--format")
            if format_idx + 1 < len(clean_command_parts):
                original_format = clean_command_parts[format_idx + 1]
                # Replace with JSON for reliable transport
                clean_command_parts[format_idx + 1] = "json"
        else:
            # No format specified, default is console
            original_format = "console"
            clean_command_parts.extend(["--format", "json"])

        command_line = " ".join(clean_command_parts)

        # Extract component metadata for progress initialization
        component_count = 0
        components_arg = args.get("components")
        if components_arg:
            # Parse component specs to get count for remote progress setup
            try:
                component_specs = self.registry.parse_components_argument(components_arg)
                component_count = len(component_specs)
            except Exception:
                # Fallback - parse simple comma-separated format
                component_count = len([c.strip() for c in components_arg.split(",") if c.strip()])
        else:
            # Default to summary preset (has 1 component)
            component_count = 1

        return {
            "cmd": "execute_command",
            "command_line": command_line,
            "working_directory": str(Path.cwd()),
            "streaming_requested": True,
            "original_format": original_format,  # Store for post-processing
            "component_count": component_count,  # For remote progress initialization
        }

    def _args_to_cli(self, args: Dict) -> List[str]:
        """Convert argument dictionary to CLI argument list."""
        cli_args = []

        for key, value in args.items():
            if key.startswith("_"):  # Skip internal args
                continue

            if value is None:
                continue

            # Convert to CLI format
            if isinstance(value, bool):
                if value:
                    cli_args.append(f"--{key.replace('_', '-')}")
            elif isinstance(value, list):
                for item in value:
                    cli_args.extend([f"--{key.replace('_', '-')}", str(item)])
            else:
                cli_args.extend([f"--{key.replace('_', '-')}", str(value)])

        return cli_args

    async def _get_worker_info(self, server_address: str, command: Dict) -> Optional[Dict]:
        """Get worker connection info from server (directory service pattern)."""
        try:
            # Send request to server for worker info - only need the boundary path
            response = await self._send_command_to_node(
                server_address,
                {
                    "cmd": "get_worker",
                    "working_directory": command["working_directory"],  # Only boundary path needed
                },
            )

            if not response:
                logger.error("No response from server when requesting worker info")
                return None

            if response.get("status") != "worker_available":
                logger.error(f"Server did not provide worker info: {response}")
                return None

            worker_info = response.get("worker_info")
            if not worker_info:
                logger.error("Server response missing worker_info")
                return None

            logger.info(f"Got worker info: {worker_info['address']}:{worker_info['port']}")
            return worker_info

        except Exception as e:
            logger.error(f"Failed to get worker info from server: {e}")
            return None

    async def _execute_with_streaming(
        self,
        progress_callback: Callable[..., Coroutine[Any, Any, None]],
        remote_address: str,
        streaming_port: int,
        command: Dict,
        show_progress: bool,
        capture_output: bool,
    ) -> RemoteExecutionResult:
        """Execute command with full streaming support."""
        # Parse address
        if ":" in remote_address:
            host, port = remote_address.split(":", 1)
        else:
            host = remote_address
            port = "5555"  # Default P2P port

        # Create streaming client
        streaming_client = StreamingClient()

        async def streaming_message_router(message_data: Dict):
            """Forward subprocess streaming messages directly to protocol handlers."""
            await streaming_client.protocol.handle_message(message_data)

        # Set up handlers
        progress_handler = ProgressHandler(show_progress)
        original_format = command.get("original_format", "console")
        output_handler = OutputHandler(
            capture_output, original_format, streaming_callback=streaming_message_router
        )
        status_handler = StatusHandler(show_progress)

        # Get component count for progress initialization
        component_count = command.get("component_count", 1)

        # Result tracking
        result = RemoteExecutionResult()
        command_completed = asyncio.Event()

        async def handle_progress(msg):
            # Update internal state
            progress_handler.update_progress_state(msg)

            logger.info(
                f"PROGRESS: stage={msg.stage}, progress={msg.progress}, total={msg.total}, message={msg.message}"
            )

            # Bridge streaming protocol with CLI progress callbacks
            # Use CLI progress callback for unified progress display
            await progress_callback(
                phase=msg.stage or "Processing",
                message=msg.message,
                current=msg.progress,
                total=msg.total or 100,
            )

        async def handle_output(msg):
            await output_handler.handle_output(msg)

        async def handle_status(msg):
            status_handler.handle_status(msg)

        async def handle_completion(msg):
            result.exit_code = msg.exit_code
            result.result_data = msg.result
            result.error = msg.error
            result.execution_time = msg.execution_time
            result.output_chunks = output_handler.captured_chunks
            command_completed.set()

        # Create ordered chunk queue to prevent race conditions
        chunk_queue = asyncio.Queue()

        async def chunk_sender():
            """Process chunks from queue in order to prevent race conditions."""
            while not command_completed.is_set():
                try:
                    chunk_msg = await asyncio.wait_for(chunk_queue.get(), timeout=0.5)
                    await output_handler.handle_output(chunk_msg)
                    chunk_queue.task_done()
                except asyncio.TimeoutError:
                    # Timeout is normal - continue checking exit condition
                    continue
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
                    break

            # Drain any remaining chunks after command completion
            while not chunk_queue.empty():
                try:
                    chunk_msg = chunk_queue.get_nowait()
                    await output_handler.handle_output(chunk_msg)
                    chunk_queue.task_done()
                except asyncio.QueueEmpty:
                    break

        # Start the chunk sender task
        chunk_sender_task = asyncio.create_task(chunk_sender())

        async def handle_component_start(msg):
            """Handle component start messages - forward to CLI progress callback."""
            logger.info(f"COMPONENT_START: {msg.component_name}, component_count={component_count}")
            progress_data = {
                "component_event": "start",
                "component_id": msg.component_name,  # Use component_name from protocol
                "total": 100,  # Default component total
                "phase": msg.component_name,
                "overall_total": component_count,  # Use the calculated component count
            }
            # Use CLI progress callback for unified progress display
            await progress_callback(**progress_data)

        async def handle_component_progress(msg):
            """Handle component progress messages - forward to CLI progress callback."""
            logger.info(f"COMPONENT_PROGRESS: {msg.component_name}, progress={msg.progress}")
            progress_data = {
                "component_event": "update",
                "component_id": msg.component_name,  # Use component_name from protocol
                "current": msg.progress,  # Use progress field from protocol
            }
            # Use CLI progress callback for unified progress display
            await progress_callback(**progress_data)

        async def handle_component_complete(msg):
            """Handle component completion messages - forward to CLI progress callback."""
            progress_data = {
                "component_event": "stop",
                "component_id": msg.component_name,  # Use component_name from protocol
            }
            # Use CLI progress callback for unified progress display
            await progress_callback(**progress_data)

        # Register handlers
        streaming_client.register_progress_handler(handle_progress)
        streaming_client.register_output_handler(handle_output)
        streaming_client.register_status_handler(handle_status)
        streaming_client.register_completion_handler(handle_completion)
        streaming_client.register_component_start_handler(handle_component_start)
        streaming_client.register_component_progress_handler(handle_component_progress)
        streaming_client.register_component_complete_handler(handle_component_complete)

        try:
            # Send command directly to worker with token (no streaming port needed)
            worker_command = {
                "cmd": "execute_command",
                "command_line": command["command_line"],
                "working_directory": command["working_directory"],
                "token": command.get("token"),  # Include token for worker validation
            }

            # Send initial command and get started response
            command_result = await self._send_command_to_node(remote_address, worker_command)

            if not command_result or command_result.get("status") != "started":
                result.error = f"Failed to start remote command: {command_result}"
                result.exit_code = GENERAL_ERROR
                return result

            # Process streaming messages directly through DEALER socket
            config = get_p2p_service().load_config()
            max_wait_time = config.command_timeout
            start_time = time.time()

            # Get the DEALER socket once and reuse it
            if not self.network_manager:
                result.error = "No network manager available"
                result.exit_code = NETWORK_ERROR
                return result
            dealer = self.network_manager.socket_manager.get_or_create_dealer_socket(remote_address)

            # Continue receiving messages until completion
            while not command_completed.is_set():
                if time.time() - start_time > max_wait_time:
                    result.error = "Remote command execution timed out"
                    result.exit_code = TIMEOUT_ERROR
                    break

                # Poll for streaming messages on the same DEALER socket
                streaming_message = await self._receive_streaming_message(dealer, timeout=0.1)
                if streaming_message:
                    # Process the streaming message through existing handlers
                    await self._process_streaming_message(
                        streaming_message,
                        handle_progress,
                        handle_output,
                        handle_status,
                        handle_completion,
                        handle_component_start,
                        handle_component_progress,
                        handle_component_complete,
                    )

        except Exception as e:
            logger.error(f"Streaming execution error: {e}")
            result.error = str(e)
            result.exit_code = GENERAL_ERROR

        finally:
            # Clean up chunk sender task
            if "chunk_sender_task" in locals():
                chunk_sender_task.cancel()
                try:
                    await asyncio.wait_for(chunk_sender_task, timeout=1.0)
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    pass

            await streaming_client.disconnect()
            progress_handler.finish()

        return result

    async def _receive_streaming_message(
        self, dealer_socket, timeout: float = 0.1
    ) -> Optional[Dict]:
        """Receive a streaming message from the provided DEALER socket."""
        try:
            # Use ZMQ's native async recv with timeout - no NOBLOCK needed
            frames = await asyncio.wait_for(dealer_socket.recv_multipart(), timeout=timeout)

            if len(frames) >= 1:
                response = json.loads(frames[-1].decode())
                if isinstance(response, dict):
                    return response
        except asyncio.TimeoutError:
            return None  # Normal timeout, no message available
        except Exception as e:
            logger.error(f"Error receiving streaming message: {e}")
            return None

        return None

    async def _process_streaming_message(
        self,
        message: Dict,
        handle_progress,
        handle_output,
        handle_status,
        handle_completion,
        handle_component_start,
        handle_component_progress,
        handle_component_complete,
    ):
        """Process a streaming message using the appropriate handler."""
        message_type = message.get("type")

        try:
            if message_type == "PROGRESS_UPDATE":
                progress_msg = ProgressUpdate(**message)
                await handle_progress(progress_msg)
            elif message_type == "STREAM_JSON":
                stream_msg = StreamJson(**message)
                await handle_output(stream_msg)
            elif message_type == "STATUS_UPDATE":
                status_msg = StatusMessage(**message)
                await handle_status(status_msg)
            elif message_type == "COMMAND_COMPLETE":
                complete_msg = CommandComplete(**message)
                await handle_completion(complete_msg)
            elif message_type == "COMPONENT_START":
                start_msg = ComponentStart(**message)
                await handle_component_start(start_msg)
            elif message_type == "COMPONENT_PROGRESS":
                progress_msg = ComponentProgress(**message)
                await handle_component_progress(progress_msg)
            elif message_type == "COMPONENT_COMPLETE":
                complete_msg = ComponentComplete(**message)
                await handle_component_complete(complete_msg)
            else:
                logger.debug(f"Unknown streaming message type: {message_type}")
        except Exception as e:
            logger.error(f"Error processing streaming message {message_type}: {e}")
            logger.debug(f"Message content: {message}")

    async def _execute_without_streaming(
        self, remote_address: str, command: Dict
    ) -> RemoteExecutionResult:
        """Execute command without streaming (fallback mode)."""
        try:
            # Send command directly to worker with token
            worker_command = {
                "cmd": "execute_command",
                "command_line": command["command_line"],
                "working_directory": command["working_directory"],
                "token": command.get("token"),  # Include token for worker validation
            }

            response = await self._send_command_to_node(remote_address, worker_command)

            if not response:
                return RemoteExecutionResult(
                    exit_code=NETWORK_ERROR, error="No response from remote node"
                )

            # Parse response
            result = RemoteExecutionResult(
                exit_code=response.get("exit_code", GENERAL_ERROR),
                result_data=response.get("result"),
                error=response.get("error"),
                execution_time=response.get("execution_time"),
            )

            # Handle output if present
            if "output" in response:
                print(response["output"], end="")
                result.output_chunks = [response["output"]]

            return result

        except Exception as e:
            logger.error(f"Remote execution error: {e}")
            return RemoteExecutionResult(exit_code=GENERAL_ERROR, error=str(e))

    async def _send_command_to_node(self, address: str, command: Dict) -> Optional[Dict]:
        """Send a command to a remote node."""
        cprint(f"🔧 SEND_COMMAND: Sending to {address} command: {command}")
        if not self.network_manager:
            raise RuntimeError("No network manager available")

        try:
            # Add timeout to prevent hanging on network calls
            result = await asyncio.wait_for(
                self.network_manager.message_handler.send_to_node(address, command),
                timeout=30.0,  # 30 second timeout for command sending
            )
            cprint(f"🔧 SEND_COMMAND: Received response: {result}")
            return result
        except asyncio.TimeoutError:
            print(f"Timeout sending command to {address}")
            return None

    async def execute_local_with_json(
        self, command_name: str, args: Dict, subcommand: Optional[str] = None
    ) -> RemoteExecutionResult:
        """
        Execute a command locally but with JSON output for consistency.
        Used when routing decision is local but we want structured output.
        """
        # Prepare command
        cmd_parts = ["codeguard", command_name]
        if subcommand:
            cmd_parts.append(subcommand)

        # Convert args to CLI format and ensure JSON output
        cli_args = self._args_to_cli(args)

        # Force JSON format
        if "--format" not in cli_args:
            cli_args.extend(["--format", "json"])
        else:
            # Replace existing format with json
            format_idx = cli_args.index("--format")
            if format_idx + 1 < len(cli_args):
                cli_args[format_idx + 1] = "json"

        cmd_parts.extend(cli_args)

        try:
            # Execute locally with timeout
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(Path.cwd()),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=300.0  # 5 minute timeout for local execution
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return RemoteExecutionResult(
                    exit_code=124, error="Local command execution timed out"  # Timeout exit code
                )

            execution_time = time.time() - start_time

            # Parse JSON result if available
            result_data = None
            if stdout:
                try:
                    result_data = json.loads(stdout.decode())
                except json.JSONDecodeError:
                    # Not JSON, treat as plain output
                    pass

            return RemoteExecutionResult(
                exit_code=process.returncode or 0,
                result_data=result_data,
                error=stderr.decode() if stderr else None,
                execution_time=execution_time,
                output_chunks=[stdout.decode()] if stdout else [],
            )

        except Exception as e:
            logger.error(f"Local JSON execution error: {e}")
            return RemoteExecutionResult(exit_code=GENERAL_ERROR, error=str(e))
