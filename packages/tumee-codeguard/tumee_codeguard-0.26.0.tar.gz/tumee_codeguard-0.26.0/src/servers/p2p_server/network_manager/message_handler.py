"""
Message Handler for P2P Network

Handles ZMQ message processing, command routing, and response generation.
"""

import asyncio
import json
import os
import shlex
import sys
import time
import uuid
from typing import Dict, Optional

import zmq

from ....core.console_shared import cprint
from ....core.exit_codes import GENERAL_ERROR, INPUT_VALIDATION_FAILED, WORKER_MANAGER_UNAVAILABLE
from ....core.runtime import set_current_command_id
from ....core.streaming.protocol import (
    CommandComplete,
    CommandError,
    ComponentComplete,
    ComponentError,
    ComponentProgress,
    ComponentStart,
    ProgressUpdate,
    StatusMessage,
    StreamEnd,
    StreamJson,
    StreamStart,
)
from ....utils.logging_config import get_logger
from ..models import (
    NewParentNotification,
    NodeMode,
    PathQuery,
    PathQueryResponse,
    PongResponse,
    RegistrationRequest,
    StatusResponse,
)
from ..p2p_manager.streaming_cache import StreamingServerCache
from ..p2p_manager.streaming_protocol import WorkerMessageSender, ZMQMessageSender
from .health_monitor import HealthMonitor
from .interfaces import IHierarchyManager, IMessageHandler, ITopologyManager
from .socket_manager import SocketManager

logger = get_logger(__name__)


class MessageHandler(IMessageHandler):
    """Handles incoming ZMQ messages and command processing."""

    def __init__(
        self,
        socket_manager: "SocketManager",
        health_monitor: "HealthMonitor",
        node_id: str,
        shutdown_event: asyncio.Event,
        node_mode: NodeMode = NodeMode.SERVER,
    ):
        """Initialize message handler."""
        self.socket_manager = socket_manager
        self.health_monitor = health_monitor
        self.node_id = node_id
        self.shutdown_event = shutdown_event
        self.node_mode = node_mode

        # Will be set by the core manager
        self.topology_manager: Optional[ITopologyManager] = None
        self.ai_ownership_manager = None
        self.worker_manager = None
        self.hierarchy_manager: Optional[IHierarchyManager] = None
        self.streaming_server: Optional[ZMQMessageSender] = None

        # Control
        self.running = False
        self.handler_task: Optional[asyncio.Task] = None
        self.task_shutdown_event = asyncio.Event()

    def set_topology_manager(self, topology_manager: ITopologyManager):
        """Set topology manager reference."""
        self.topology_manager = topology_manager

    def set_ai_ownership_manager(self, ai_ownership_manager):
        """Set AI ownership manager reference."""
        self.ai_ownership_manager = ai_ownership_manager

    def set_worker_manager(self, worker_manager):
        """Set boundary worker manager reference."""
        self.worker_manager = worker_manager

    def set_hierarchy_manager(self, hierarchy_manager):
        """Set hierarchy manager reference."""
        self.hierarchy_manager = hierarchy_manager

    def _is_acting_as_broker(self) -> bool:
        """Check if this node is currently acting as a discovery broker."""
        return (
            self.socket_manager.discovery_broker_pub is not None
            and not self.socket_manager.discovery_broker_pub.closed
        )

    async def start(self):
        """Start message handling."""
        if self.running and self.handler_task and not self.handler_task.done():
            logger.warning("Message handler already running")
            return

        # Clean up any existing task
        if self.handler_task and not self.handler_task.done():
            self.handler_task.cancel()
            try:
                await self.handler_task
            except asyncio.CancelledError:
                pass

        self.running = True
        self.handler_task = asyncio.create_task(self._message_handler_loop())
        logger.info("Message handler started")

    async def stop(self):
        """Stop message handling."""
        self.running = False
        self.task_shutdown_event.set()

        if self.handler_task and not self.handler_task.done():
            try:
                await asyncio.wait_for(self.handler_task, timeout=0.2)
            except asyncio.TimeoutError:
                if not self.handler_task.done():
                    self.handler_task.cancel()
                    try:
                        await self.handler_task
                    except asyncio.CancelledError:
                        pass
        logger.info("Message handler stopped")

    async def send_to_node(self, address: str, message: Dict) -> Optional[Dict]:
        """Send a message to a specific node and wait for response."""
        dealer = self.socket_manager.get_or_create_dealer_socket(address)

        try:
            try:
                await dealer.send_json(message)
                cprint(f"🔧 SEND_TO_NODE: Message sent successfully to {address}")
            except Exception as e:
                print(f"Send error to {address}: {e}")
                return None

            # Wait for response with timeout
            raw_response = None
            try:
                frames = await asyncio.wait_for(dealer.recv_multipart(), timeout=5.0)
                cprint(f"🔧 SEND_TO_NODE: Received {len(frames)} frames from {address}: {frames}")

                # DEALER receives response without identity frame, so it should be just the message
                if len(frames) >= 1:
                    raw_response = frames[-1]  # Last frame should be the JSON message
                    response = json.loads(raw_response.decode())
                    if isinstance(response, dict):
                        return response
                    else:
                        print(f"Unexpected response type from {address}: {type(response)}")
                        return None
                else:
                    print(f"No frames received from {address}")
                    return None
            except asyncio.TimeoutError:
                print(f"No response from {address}")
                return None
            except json.JSONDecodeError as e:
                print(f"JSON decode error from {address}: {e}, raw: {raw_response}")
                return None

        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                print("Cannot send message, context terminated")
            else:
                print(f"ZMQ error sending to node {address}: {e}")
        except Exception as e:
            print(f"Send to node error: {e}")

        return None

    async def _message_handler_loop(self):
        """Handle incoming ZMQ messages."""
        try:
            while not self.task_shutdown_event.is_set() and not self.shutdown_event.is_set():
                try:
                    # Use async recv with timeout
                    if self.socket_manager.router is None:
                        break
                    frames = await asyncio.wait_for(
                        self.socket_manager.router.recv_multipart(), timeout=0.5
                    )
                    cprint(f"🔧 MESSAGE_LOOP: Received {len(frames)} frames")

                    if self.shutdown_event.is_set():
                        break

                    if len(frames) >= 2:
                        # Handle both 2-frame and 3-frame messages
                        if len(frames) == 3:
                            identity, _, message = frames[0], frames[1], frames[2]
                        else:  # len(frames) == 2
                            identity, message = frames[0], frames[1]
                        cprint(f"🔧 MESSAGE_LOOP: Processing message: {message.decode()}")
                        data = json.loads(message.decode())

                        response = await self._handle_command(data, client_identity=identity)

                        if response and self.socket_manager.router is not None:
                            response_json = json.dumps(response)
                            cprint(f"🔧 MESSAGE_LOOP: Sending response: {response_json}")
                            await self.socket_manager.router.send_multipart(
                                [identity, b"", response_json.encode()]
                            )
                        else:
                            cprint(
                                f"🔧 MESSAGE_LOOP: No response to send (response={response}, router={self.socket_manager.router is not None})"
                            )
                    else:
                        cprint(f"🔧 MESSAGE_LOOP: Unexpected {len(frames)} frames")
                        continue

                except asyncio.TimeoutError:
                    # No message received - this is normal, continue
                    continue
                except json.JSONDecodeError as e:
                    logger.debug(f"Invalid JSON in message: {e}")
                except Exception as e:
                    if not self.shutdown_event.is_set():
                        logger.debug(f"Message handler error: {e}")
                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            logger.debug("Message handler task cancelled")

    async def _handle_command(
        self, data: Dict, client_identity: Optional[bytes] = None
    ) -> Optional[Dict]:
        """Handle a command and return response."""
        cmd = data.get("cmd")
        cprint(f"🔧 HANDLE_COMMAND: Processing command '{cmd}' with data: {data}")

        # Check if this node is currently acting as elected broker
        is_elected_broker = self._is_acting_as_broker()

        # Define command categories based on node modes
        broker_only_commands = {
            "register_child",
            "new_parent",
            "query_path",
        }  # Only elected brokers handle these
        server_only_commands = {"get_worker"}  # Only servers can create workers
        worker_only_commands = {
            "execute_command",
            "execute_ai_command",
        }  # Only workers execute
        # general_commands = {"ping", "query_ai_ownership"}  # All nodes can handle these

        # Role-based command filtering
        if cmd in broker_only_commands and not is_elected_broker:
            logger.warning(f"Non-broker node received broker command: {cmd}")
            return {
                "status": "error",
                "error": f"Command '{cmd}' only supported by elected broker nodes",
                "exit_code": GENERAL_ERROR,
                "node_id": self.node_id,
            }
        elif cmd in server_only_commands and self.node_mode != NodeMode.SERVER:
            logger.warning(f"Non-server node received server command: {cmd}")
            return {
                "status": "error",
                "error": f"Command '{cmd}' only supported by server nodes",
                "exit_code": GENERAL_ERROR,
                "node_id": self.node_id,
            }
        elif cmd in worker_only_commands and self.node_mode != NodeMode.WORKER:
            logger.warning(f"Non-worker node received worker command: {cmd}")
            return {
                "status": "error",
                "error": f"Command '{cmd}' only supported by worker nodes",
                "exit_code": GENERAL_ERROR,
                "node_id": self.node_id,
            }

        # Process commands
        if cmd == "register_child":
            return await self._handle_register_child(data)
        elif cmd == "new_parent":
            return await self._handle_new_parent(data)
        elif cmd == "query_path":
            return await self._handle_query_path(data)
        elif cmd == "ping":
            return self._handle_ping(data)
        elif cmd == "query_ai_ownership":
            return await self._handle_query_ai_ownership(data)
        elif cmd == "execute_ai_command":
            return await self._handle_execute_ai_command(data)
        elif cmd == "execute_command":
            return await self._handle_execute_command(data, client_identity)
        elif cmd == "get_worker":
            return await self._handle_get_worker(data)

        return None

    async def _handle_register_child(self, data: Dict) -> Dict:
        """Handle child registration request."""
        try:
            request = RegistrationRequest(**data)

            if self.topology_manager:
                self.topology_manager.register_child(request)

            logger.info(f"Child {request.node_id} registered for paths: {request.paths}")
            return StatusResponse(status="registered").model_dump()

        except Exception as e:
            logger.error(f"Error handling child registration: {e}")
            return StatusResponse(status="error", message=str(e)).model_dump()

    async def _handle_new_parent(self, data: Dict) -> Dict:
        """Handle new parent notification."""
        try:
            notification = NewParentNotification(**data)

            if self.topology_manager:
                await self.topology_manager.handle_new_parent(notification)

            logger.info(f"Reorganized under new parent: {notification.parent_node_id}")
            return StatusResponse(status="reorganized").model_dump()

        except Exception as e:
            logger.error(f"Error handling new parent: {e}")
            return StatusResponse(status="error", message=str(e)).model_dump()

    async def _handle_query_path(self, data: Dict) -> Dict:
        """Handle path ownership query."""
        try:
            query = PathQuery(**data)

            if self.topology_manager:
                return await self.topology_manager.handle_path_query(query.path)
            else:
                return PathQueryResponse(error="Topology manager not available").model_dump()

        except Exception as e:
            logger.error(f"Error handling path query: {e}")
            return PathQueryResponse(error=str(e)).model_dump()

    def _handle_ping(self, data: Dict) -> Dict:
        """Handle ping request."""
        # Return the format expected by BoundaryWorker.ping()
        return {
            "type": "COMMAND_COMPLETE",
            "status": "pong",
            "boundary_key": getattr(self, "boundary_key", "unknown"),
        }

    async def _handle_query_ai_ownership(self, data: Dict) -> Dict:
        """Handle AI ownership query."""
        try:
            path = data.get("path")
            if path is None:
                return {"error": "No path specified in AI ownership query"}

            if self.ai_ownership_manager:
                ai_owner = self._get_ai_owner_for_path(path)
                return {"ai_owner": ai_owner}
            else:
                return {"error": "AI ownership manager not available"}

        except Exception as e:
            logger.error(f"Error handling AI ownership query: {e}")
            return {"error": str(e)}

    async def _handle_execute_ai_command(self, data: Dict) -> Dict:
        """Handle AI command execution request."""
        try:
            command = data.get("command", {})
            path = command.get("path")

            if not path:
                return {"error": "No path specified in AI command"}

            if not self.ai_ownership_manager:
                return {"error": "AI ownership manager not available"}

            ai_owner_info = self.ai_ownership_manager.get_ai_owner_for_path(path)
            if ai_owner_info:
                result = await self._execute_local_ai_command(path, command, ai_owner_info)
                return result
            else:
                return {"error": "No AI owner found for path", "path": path}

        except Exception as e:
            logger.error(f"Error handling AI command execution: {e}")
            return {"error": str(e)}

    def _get_ai_owner_for_path(self, path: str) -> Optional[Dict]:
        """Get AI ownership information for a path."""
        if not self.ai_ownership_manager:
            return None

        ai_owner = self.ai_ownership_manager.get_ai_owner_for_path(path)
        if ai_owner:
            return {
                "module_name": ai_owner.module_name,
                "capabilities": list(ai_owner.capabilities),
                "roles": list(ai_owner.roles.keys()),
                "config_path": str(ai_owner.path),
                "node_id": self.node_id,
                "address": f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
                "streaming_port": self.socket_manager.streaming_port,
            }
        return None

    async def _execute_local_ai_command(self, _path: str, command: Dict, ai_owner_info) -> Dict:
        """Execute AI command locally."""
        try:
            # Execute the command based on type
            command_type = command.get("type", "unknown")

            if command_type == "analysis":
                result = await self._execute_ai_analysis(ai_owner_info, command)
            elif command_type == "generation":
                result = await self._execute_ai_generation(ai_owner_info, command)
            else:
                result = {"error": f"Unknown AI command type: {command_type}"}

            return {"status": "success", "result": result, "node_id": self.node_id}

        except Exception as e:
            logger.error(f"Local AI command execution error: {e}")
            return {"status": "error", "error": str(e), "node_id": self.node_id}

    async def _execute_ai_analysis(self, ai_owner, command: Dict) -> Dict:
        """Execute AI analysis command."""
        # Placeholder for actual AI analysis implementation
        # This would integrate with the actual AI models/services
        return {
            "analysis_type": command.get("analysis_type", "general"),
            "module": ai_owner.module_name,
            "capabilities": list(ai_owner.capabilities),
            "result": "AI analysis placeholder result",
        }

    async def _execute_ai_generation(self, ai_owner, command: Dict) -> Dict:
        """Execute AI code generation command."""
        # Placeholder for actual AI generation implementation
        return {
            "generation_type": command.get("generation_type", "code"),
            "module": ai_owner.module_name,
            "result": "AI generation placeholder result",
        }

    async def _handle_execute_command(
        self, data: Dict, client_identity: Optional[bytes] = None
    ) -> Dict:
        """Handle execute_command request - unified streaming execution."""
        cprint(f"🔧 HANDLE_EXECUTE_COMMAND: Received request with data: {data}")
        try:
            command_line = data.get("command_line")
            working_dir = data.get("working_directory")

            if not command_line:
                return {
                    "error": "No command_line provided",
                    "exit_code": INPUT_VALIDATION_FAILED,
                }

            if not working_dir:
                return {
                    "error": "No working_directory provided",
                    "exit_code": INPUT_VALIDATION_FAILED,
                }

            # Only NodeMode.SERVER at top of hierarchy can spawn P2P workers
            if (
                self.worker_manager
                and self.node_mode == NodeMode.SERVER
                and self.hierarchy_manager
                and self.hierarchy_manager.is_top_of_hierarchy(working_dir)
            ):
                # Top-level server: Delegate to worker via directory service
                command_data = {
                    "command_line": command_line,
                    "validated_path": working_dir,
                }

                # Get worker connection info via worker manager (directory service)
                worker_info = await self.worker_manager.get_or_create_worker_info(command_data)

                # Return worker connection details for direct client connection
                return {
                    "status": "worker_available",
                    "worker_info": worker_info,
                    "node_id": self.node_id,
                }

            # NodeMode.WORKER or sub-hierarchy server: Execute locally with streaming
            else:
                streaming_port = data.get("streaming_port")
                command_id = str(uuid.uuid4())

                # Start background streaming execution
                cprint(f"🔧 EXECUTE_COMMAND: Creating background streaming task for {command_id}")
                asyncio.create_task(
                    self._execute_streaming_command_background(
                        command_id, data, streaming_port, client_identity
                    )
                )

                cprint(f"🔧 EXECUTE_COMMAND: Started streaming command {command_id}")
                return {
                    "status": "started",
                    "command_id": command_id,
                    "streaming_port": streaming_port,
                    "node_id": self.node_id,
                }

        except Exception as e:
            logger.error(f"Error handling execute_command: {e}")
            return {
                "status": "error",
                "error": str(e),
                "exit_code": GENERAL_ERROR,
                "node_id": self.node_id,
            }

    async def _execute_streaming_command_background(
        self,
        command_id: str,
        data: Dict,
        streaming_port: Optional[int],
        client_identity: Optional[bytes] = None,
    ):
        """Execute command in background with streaming updates."""
        start_time = time.time()
        streaming_server = None
        cprint(f"🔧 STREAMING_EXEC: Background task started for command {command_id}")
        cprint(f"🔧 STREAMING_EXEC: Command data: {data}")

        try:
            # Create appropriate streaming server based on whether we have a client identity
            if client_identity and self.socket_manager.router:
                # Worker mode: create direct client communication via ROUTER
                streaming_server = WorkerMessageSender(
                    router_socket=self.socket_manager.router,
                    client_identity=client_identity,
                    context=self.socket_manager.context,
                )
                await streaming_server.start()
                cprint(
                    f"🔧 STREAMING_EXEC: Created WorkerMessageSender for client {client_identity}"
                )
            else:
                # Broker/Server mode: use existing streaming server
                streaming_server = getattr(self, "streaming_server", None)
                cprint(
                    f"🔧 STREAMING_EXEC: Using existing streaming_server: {streaming_server is not None}"
                )

            if not streaming_server:
                error_msg = f"No streaming server available for command {command_id}"
                logger.error(error_msg)
                cprint(f"🔧 STREAMING_EXEC: ERROR - {error_msg}")
                return

            # Register streaming server in cache for direct access by components
            cache = StreamingServerCache.get_instance()
            cache.register(command_id, streaming_server)
            cprint(
                f"🔧 STREAMING_EXEC: Registered streaming server in cache for command {command_id}"
            )

            # Send initial status
            await streaming_server.send_status(
                command_id=command_id,
                level="INFO",
                message="Starting command execution",
                source="worker_manager",
            )

            # Execute the actual CLI command with streaming
            execute_result = await self._execute_cli_command_with_streaming(
                command_id, data, streaming_server
            )
            execution_time = time.time() - start_time

            # Send completion message
            if execute_result.get("status") == "success":
                await streaming_server.send_completion(
                    command_id=command_id,
                    status="success",
                    exit_code=0,
                    result=execute_result.get("result"),
                    execution_time=execution_time,
                )
            else:
                await streaming_server.send_completion(
                    command_id=command_id,
                    status="error",
                    exit_code=execute_result.get("exit_code", GENERAL_ERROR),
                    error=execute_result.get("error", "Unknown error"),
                    execution_time=execution_time,
                )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error in streaming command background execution: {e}"
            logger.error(error_msg)
            cprint(f"🔧 STREAMING_EXEC: EXCEPTION - {error_msg}")
            cprint(f"🔧 STREAMING_EXEC: Exception details: {type(e).__name__}: {e}")
            # Send error completion if possible
            try:
                if streaming_server:
                    cprint(
                        "🔧 STREAMING_EXEC: Attempting to send error completion via streaming server"
                    )
                    await streaming_server.send_completion(
                        command_id=command_id,
                        status="error",
                        exit_code=GENERAL_ERROR,
                        error=str(e),
                        execution_time=execution_time,
                    )
                else:
                    cprint("🔧 STREAMING_EXEC: Cannot send error completion - no streaming server")
            except Exception as completion_error:
                cprint(f"🔧 STREAMING_EXEC: Failed to send error completion: {completion_error}")
                pass  # Best effort error reporting

        finally:
            # Always unregister streaming server from cache when command completes
            try:
                cache = StreamingServerCache.get_instance()
                cache.unregister(command_id)
                cprint(
                    f"🔧 STREAMING_EXEC: Unregistered streaming server from cache for command {command_id}"
                )
            except Exception as e:
                cprint(f"🔧 STREAMING_EXEC: Failed to unregister streaming server: {e}")

            # Clean up WorkerMessageSender if we created one
            try:
                if streaming_server and isinstance(streaming_server, WorkerMessageSender):
                    await streaming_server.stop()
                    cprint(
                        f"🔧 STREAMING_EXEC: Cleaned up WorkerMessageSender for command {command_id}"
                    )
            except Exception as e:
                cprint(f"🔧 STREAMING_EXEC: Failed to cleanup WorkerMessageSender: {e}")

    async def _execute_cli_command_with_streaming(
        self, command_id: str, data: Dict, streaming_server
    ) -> Dict:
        """Execute CLI command with real-time streaming output."""
        command_line = data.get("command_line", "")
        working_directory = data.get("working_directory", ".")

        try:
            # Parse command line
            args = shlex.split(command_line)
            # Use console script instead of python -m module (works in both dev and production)
            # Force local execution to prevent P2P recursion
            cmd = ["codeguard", "--local"] + args

            # Start subprocess with worker process environment (exclude command ID)

            env = os.environ.copy()
            # Set CODEGUARD_COMMAND_ID for subprocess to inherit
            set_current_command_id(command_id, env)
            env["CODEGUARD_WORKER_PROCESS"] = "1"
            env["CODEGUARD_WORKER_MODE"] = "ipc"
            env["PYTHONUNBUFFERED"] = "1"
            logger.warning(f"🔧 EXECUTE_CLI: Executing command: {cmd} in {working_directory}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory,
                env=env,
            )

            # Stream output in chunks rather than line-by-line to preserve JSON structure
            async def stream_output(stream, stream_name):
                logger.warning(f"Stream_output started for {stream_name}")
                buffer = b""
                chunk_size = 4096  # Read in larger chunks

                try:
                    while True:
                        chunk = await stream.read(chunk_size)
                        if not chunk:
                            break

                        buffer += chunk

                        # Process complete messages separated by \n\n
                        while b"\n\n" in buffer:
                            separator_pos = buffer.find(b"\n\n")
                            message_data = buffer[:separator_pos]  # Single JSON message
                            buffer = buffer[
                                separator_pos + 2 :
                            ]  # Remove processed message + separator
                            logger.warning(
                                f"STREAM_OUTPUT: Processed message of size {len(message_data)} bytes from {stream_name}"
                            )
                            if len(message_data) > 40000:
                                logger.warning(message_data)
                            # Process single complete message
                            await self._process_stream_lines(
                                message_data, stream_name, streaming_server, command_id
                            )

                        # Memory management - error if buffer gets too large without complete messages
                        if len(buffer) > 8 * 1024 * 1024:  # 8MB limit
                            logger.error(
                                f"Stream buffer exceeded 8MB without complete message - possible malformed data"
                            )
                            buffer = b""  # Clear buffer and continue

                    # Send any remaining buffered data
                    if buffer:
                        try:
                            text = buffer.decode("utf-8", errors="replace")
                            if text:
                                await streaming_server.send_output(
                                    command_id=command_id, stream=stream_name, data=text
                                )
                        except Exception as e:
                            logger.error(f"Error streaming final {stream_name}: {e}")

                except Exception as e:
                    logger.error(f"Error in stream_output for {stream_name}: {e}")

            # Start streaming tasks
            stdout_task = asyncio.create_task(stream_output(process.stdout, "stdout"))
            stderr_task = asyncio.create_task(stream_output(process.stderr, "stderr"))
            logger.warning(f"EXECUTE_CLI: Started streaming tasks for stdout and stderr")
            # Wait for process AND streaming to complete together
            results = await asyncio.gather(
                process.wait(), stdout_task, stderr_task, return_exceptions=True
            )
            exit_code = results[0]  # First result is from process.wait()
            logger.warning(f"EXECUTE_CLI: Command completed with exit code {exit_code}")
            return {"status": "success" if exit_code == 0 else "error", "exit_code": exit_code}

        except Exception as e:
            logger.error(f"CLI command execution failed: {e}")
            return {"status": "error", "error": str(e), "exit_code": GENERAL_ERROR}

    async def _process_stream_lines(
        self, message_data: bytes, stream_name: str, streaming_server, command_id: str
    ):
        """Process a single complete message and wrap in appropriate envelope."""
        try:
            # Decode the single message
            text = message_data.decode("utf-8", errors="replace").strip()

            # Process the single message
            if text:  # Skip empty messages
                await self._wrap_and_send_line(text, stream_name, streaming_server, command_id)

        except Exception as e:
            logger.error(f"Error processing stream message: {e}")

    async def _wrap_and_send_line(
        self, line: str, stream_name: str, streaming_server, command_id: str
    ):
        """Wrap a complete line in appropriate envelope and send via streaming."""
        try:
            logger.warning(
                f"WRAP_AND_SEND_LINE: Processing line for stream '{stream_name}': {line[:100]}..."
            )
            if stream_name == "stdout":
                # Try to parse as streaming JSON message
                try:
                    message_data = json.loads(line)
                    if isinstance(message_data, dict):
                        message_type = message_data.get("type", "").lower()

                        if message_type == "progress_update":
                            # This is a progress update - forward to streaming server
                            # Replace 'default' command_id with actual command_id for proper routing
                            if message_data.get("command_id") == "default":
                                message_data["command_id"] = command_id

                            if streaming_server:
                                # Ensure progress and total are never None - default to 0
                                if message_data.get("progress") is None:
                                    message_data["progress"] = 0
                                if message_data.get("total") is None:
                                    message_data["total"] = 0
                                progress_msg = ProgressUpdate(**message_data)
                                await streaming_server.send_message(progress_msg)
                            return
                        elif message_type == "stream_json":
                            # StreamJson contains complete component results - forward via streaming server
                            # Replace 'default' command_id with actual command_id for proper routing
                            if message_data.get("command_id") == "default":
                                message_data["command_id"] = command_id

                            if streaming_server:
                                stream_msg = StreamJson(**message_data)
                                await streaming_server.send_message(stream_msg)
                            return
                        elif message_type in [
                            "status_message",
                            "command_complete",
                            "command_error",
                            "component_start",
                            "component_progress",
                            "component_complete",
                            "component_error",
                            "stream_start",
                            "stream_end",
                        ]:
                            # Forward streaming messages directly
                            cprint(f"🔧 STREAM_MSG: Forwarding {message_type} message")
                            message_classes = {
                                "status_message": StatusMessage,
                                "command_complete": CommandComplete,
                                "command_error": CommandError,
                                "component_start": ComponentStart,
                                "component_progress": ComponentProgress,
                                "component_complete": ComponentComplete,
                                "component_error": ComponentError,
                                "stream_start": StreamStart,
                                "stream_end": StreamEnd,
                            }
                            msg_class = message_classes.get(message_type)
                            if msg_class:
                                if message_data.get("command_id") == "default":
                                    message_data["command_id"] = command_id
                                msg = msg_class(**message_data)
                                await streaming_server.send_message(msg)
                                return
                        elif "component" in message_data:
                            # This is a component result - wrap in ComponentComplete message
                            cprint(
                                f"🔧 STREAM_JSON: Detected component JSON: {message_data.get('component', 'unknown')}"
                            )
                            message = ComponentComplete(
                                command_id=command_id,
                                component_name=message_data.get("component", "unknown"),
                                data=message_data,  # Send complete component data structure
                                execution_time=0.0,  # Will be filled by component system later
                            )
                            await streaming_server.send_message(message)
                            cprint(f"🔧 STREAM_JSON: Broadcasted ComponentComplete message")
                            return
                except (json.JSONDecodeError, KeyError) as e:
                    # Not JSON or not streaming JSON - send as regular output
                    cprint(
                        f"🔧 JSON_PARSE_ERROR: Failed to parse line as JSON: {line[:100]}... Error: {e}"
                    )
                    pass  # Fall through to regular output handling

            # For non-component stdout or stderr, send as regular stream chunk
            await streaming_server.send_output(command_id=command_id, stream=stream_name, data=line)

        except Exception as e:
            logger.error(f"Error wrapping and sending line: {e}")

    async def _flush_incomplete_buffer(
        self, buffer: bytes, stream_name: str, streaming_server, command_id: str
    ):
        """Flush incomplete buffer data when memory limit reached."""
        try:
            text = buffer.decode("utf-8", errors="replace")
            if text is not None:
                await streaming_server.send_output(
                    command_id=command_id, stream=stream_name, data=text
                )
        except Exception as e:
            logger.error(f"Error flushing incomplete buffer: {e}")

    async def _handle_get_worker(self, data: Dict) -> Dict:
        """Handle get_worker request from remote executor (directory service pattern)."""
        cprint(f"🔧 HANDLE_GET_WORKER: Received request with data: {data}")
        cprint(f"🔧 HANDLE_GET_WORKER: Node role - is_broker: {self._is_acting_as_broker()}")
        cprint(f"🔧 HANDLE_GET_WORKER: Worker manager available: {self.worker_manager is not None}")

        try:
            if not self.worker_manager:
                cprint("🔧 HANDLE_GET_WORKER: ERROR - Worker manager not available")
                return {
                    "error": "Worker manager not available",
                    "exit_code": WORKER_MANAGER_UNAVAILABLE,
                }

            working_dir = data.get("working_directory")

            if not working_dir:
                cprint("🔧 HANDLE_GET_WORKER: ERROR - No working_directory provided")
                return {
                    "error": "No working_directory provided",
                    "exit_code": INPUT_VALIDATION_FAILED,
                }

            cprint(f"🔧 HANDLE_GET_WORKER: Working directory: {working_dir}")

            # Create command data for worker manager - only need the boundary path
            command_data = {
                "validated_path": working_dir,
            }

            cprint("🔧 HANDLE_GET_WORKER: Calling worker_manager.get_or_create_worker_info")
            # Get worker connection info via worker manager (directory service pattern)
            worker_info = await self.worker_manager.get_or_create_worker_info(command_data)
            cprint(f"🔧 HANDLE_GET_WORKER: Worker info received: {worker_info}")

            # Return worker connection details for direct client connection
            response = {
                "status": "worker_available",
                "worker_info": worker_info,
                "node_id": self.node_id,
            }
            cprint(f"🔧 HANDLE_GET_WORKER: Returning response: {response}")
            return response

        except Exception as e:
            cprint(f"🔧 HANDLE_GET_WORKER: EXCEPTION - {e}")
            logger.error(f"Error handling get_worker: {e}")
            return {
                "status": "error",
                "error": str(e),
                "exit_code": GENERAL_ERROR,
                "node_id": self.node_id,
            }
