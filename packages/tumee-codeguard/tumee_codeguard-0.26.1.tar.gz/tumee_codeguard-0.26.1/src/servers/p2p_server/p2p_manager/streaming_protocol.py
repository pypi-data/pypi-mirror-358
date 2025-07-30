"""
P2P Streaming Protocol

ZMQ-specific implementation of streaming message infrastructure for P2P operations.
Extends core streaming with ZMQ transport capabilities.
"""

import asyncio
import base64
import json
import uuid
from typing import Any, Dict, List, Optional

import zmq
import zmq.asyncio

from ....core.streaming.base import MessageSender
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
    StreamingMessage,
    StreamingMessageType,
    StreamJson,
    StreamStart,
)
from ....utils.logging_config import get_logger

logger = get_logger(__name__)


class ZMQMessageSender(MessageSender):
    """Abstract base class for ZMQ-based message senders."""

    def __init__(self, port: Optional[int] = None, context: Optional[zmq.asyncio.Context] = None):
        super().__init__()
        self.context = context or zmq.asyncio.Context()
        self.protocol = StreamingProtocol(self.context)
        self.port = port
        self.socket: Optional[zmq.asyncio.Socket] = None

    async def _setup_destination(self):
        """Setup ZMQ socket. Must be implemented by derived classes."""
        raise NotImplementedError("Derived classes must implement _setup_destination")

    async def _cleanup_destination(self):
        """Cleanup ZMQ socket."""
        if self.socket:
            try:
                # Set linger to 0 for immediate close
                self.socket.setsockopt(zmq.LINGER, 0)
                self.socket.close()
            except Exception as e:
                logger.debug(f"Error closing ZMQ socket: {e}")
            finally:
                self.socket = None

    async def _send_message(self, message: StreamingMessage):
        """Send message via ZMQ."""
        if self.socket:
            await self.protocol.send_message(self.socket, message)


class BrokerMessageSender(ZMQMessageSender):
    """ZMQ message sender for broker broadcasting via PUB socket."""

    def __init__(self, port: int, context: Optional[zmq.asyncio.Context] = None):
        super().__init__(port, context)
        if not port:
            raise ValueError("Port is required for BrokerMessageSender")

    async def _setup_destination(self):
        """Setup PUB socket for broadcasting."""
        self.socket = self.context.socket(zmq.PUB)
        # Set socket options for non-blocking behavior
        self.socket.setsockopt(zmq.LINGER, 1000)  # 1 second linger
        self.socket.setsockopt(zmq.SNDTIMEO, 5000)  # 5 second send timeout
        try:
            self.socket.bind(f"tcp://*:{self.port}")
            logger.info(f"Broker message sender started on port {self.port}")
        except zmq.ZMQError as e:
            logger.error(f"Failed to bind PUB socket to port {self.port}: {e}")
            if self.socket:
                self.socket.close()
                self.socket = None
            raise RuntimeError(f"Could not bind broker message sender to port {self.port}") from e


class WorkerMessageSender(ZMQMessageSender):
    """ZMQ message sender for direct client communication via ROUTER socket."""

    def __init__(
        self,
        router_socket: zmq.asyncio.Socket,
        client_identity: bytes,
        context: Optional[zmq.asyncio.Context] = None,
    ):
        super().__init__(None, context)
        self.router_socket = router_socket
        self.client_identity = client_identity

    async def _setup_destination(self):
        """Setup is not needed as we use existing ROUTER socket."""
        # No setup needed - we use the existing router socket
        logger.info(f"Worker message sender initialized for client {self.client_identity}")

    async def _send_message(self, message: StreamingMessage):
        """Send message to specific client via ROUTER socket."""
        if self.router_socket:
            try:
                message_data = message.model_dump()
                message_json = json.dumps(message_data)
                await self.router_socket.send_multipart(
                    [self.client_identity, b"", message_json.encode()]
                )
            except Exception as e:
                logger.error(f"Error sending message to client via ROUTER: {e}")
                raise

    async def _cleanup_destination(self):
        """No cleanup needed for WorkerMessageSender as it uses shared router socket."""
        # No cleanup needed - we don't own the router socket
        pass


class StreamingProtocol:
    """Handles ZMQ streaming protocol for P2P command execution."""

    def __init__(self, context: Optional[zmq.asyncio.Context] = None):
        self.context = context or zmq.asyncio.Context()
        self.active_streams: Dict[str, Dict] = {}  # command_id -> stream_info
        self.message_handlers: Dict[StreamingMessageType, List] = {}

    def register_handler(self, message_type: StreamingMessageType, handler):
        """Register a handler for a specific message type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    async def handle_message(self, message_data: Dict):
        """Handle an incoming streaming message."""
        try:
            message_type = StreamingMessageType(message_data.get("type"))

            # Create appropriate message object
            message_classes = {
                StreamingMessageType.PROGRESS_UPDATE: ProgressUpdate,
                StreamingMessageType.STATUS_MESSAGE: StatusMessage,
                StreamingMessageType.STREAM_JSON: StreamJson,
                StreamingMessageType.COMMAND_COMPLETE: CommandComplete,
                StreamingMessageType.COMMAND_ERROR: CommandError,
                StreamingMessageType.STREAM_START: StreamStart,
                StreamingMessageType.STREAM_END: StreamEnd,
                StreamingMessageType.COMPONENT_START: ComponentStart,
                StreamingMessageType.COMPONENT_PROGRESS: ComponentProgress,
                StreamingMessageType.COMPONENT_COMPLETE: ComponentComplete,
                StreamingMessageType.COMPONENT_ERROR: ComponentError,
            }

            message_class = message_classes.get(message_type, StreamingMessage)
            message = message_class(**message_data)

            # Call registered handlers
            handlers = self.message_handlers.get(message_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
                except Exception as e:
                    logger.error(f"Handler error for {message_type}: {e}")

        except Exception as e:
            logger.error(f"Error handling streaming message: {e}")

    def create_command_id(self) -> str:
        """Create a unique command ID."""
        return f"cmd_{uuid.uuid4().hex[:12]}"

    async def send_message(self, socket: zmq.asyncio.Socket, message: StreamingMessage):
        """Send a streaming message over ZMQ."""
        try:
            message_data = message.model_dump()
            await socket.send_string(json.dumps(message_data))
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                logger.debug("Cannot send message, context terminated")
            else:
                logger.error(f"ZMQ error sending streaming message: {e}")
        except Exception as e:
            logger.error(f"Error sending streaming message: {e}")

    async def receive_message(self, socket: zmq.asyncio.Socket) -> Optional[StreamingMessage]:
        """Receive a streaming message from ZMQ."""
        try:
            message_data = await socket.recv_string()
            data = json.loads(message_data)
            return self._parse_message(data)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                logger.debug("Cannot receive message, context terminated")
            else:
                logger.error(f"ZMQ error receiving streaming message: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.debug(f"Invalid JSON in streaming message: {e}")
            return None
        except Exception as e:
            logger.error(f"Error receiving streaming message: {e}")
            return None

    def _parse_message(self, data: Dict) -> Optional[StreamingMessage]:
        """Parse raw message data into a StreamingMessage object."""
        try:
            message_type = StreamingMessageType(data.get("type"))

            message_classes = {
                StreamingMessageType.PROGRESS_UPDATE: ProgressUpdate,
                StreamingMessageType.STATUS_MESSAGE: StatusMessage,
                StreamingMessageType.STREAM_JSON: StreamJson,
                StreamingMessageType.COMMAND_COMPLETE: CommandComplete,
                StreamingMessageType.COMMAND_ERROR: CommandError,
                StreamingMessageType.STREAM_START: StreamStart,
                StreamingMessageType.STREAM_END: StreamEnd,
                StreamingMessageType.COMPONENT_START: ComponentStart,
                StreamingMessageType.COMPONENT_PROGRESS: ComponentProgress,
                StreamingMessageType.COMPONENT_COMPLETE: ComponentComplete,
                StreamingMessageType.COMPONENT_ERROR: ComponentError,
            }

            message_class = message_classes.get(message_type, StreamingMessage)
            return message_class(**data)

        except Exception as e:
            logger.error(f"Error parsing streaming message: {e}")
            return None


class StreamingClient:
    """Client for connecting to and receiving streaming messages from a P2P node."""

    def __init__(self, context: Optional[zmq.asyncio.Context] = None):
        self.context = context or zmq.asyncio.Context()
        self.protocol = StreamingProtocol(self.context)
        self.socket: Optional[zmq.asyncio.Socket] = None
        self.connected = False

    async def connect(self, address: str, port: int):
        """Connect to a streaming server."""
        if self.socket:
            self.socket.close()

        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{address}:{port}")
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")  # Subscribe to all messages
        self.connected = True
        logger.info(f"Connected to streaming server at {address}:{port}")

    async def disconnect(self):
        """Disconnect from the streaming server."""
        self.connected = False

        if self.socket:
            try:
                # Set linger to 0 for immediate close
                self.socket.setsockopt(zmq.LINGER, 0)
                self.socket.close()
            except Exception as e:
                logger.debug(f"Error closing streaming client socket: {e}")
            finally:
                self.socket = None

    async def listen_for_messages(self, command_id: Optional[str] = None):
        """Listen for streaming messages, optionally filtering by command_id."""
        if not self.connected or not self.socket:
            raise RuntimeError("Not connected to streaming server")

        try:
            while self.connected:
                try:
                    # Use proper async recv with timeout to prevent message drops
                    message = await asyncio.wait_for(
                        self.protocol.receive_message(self.socket),
                        timeout=0.5,  # 0.5 second timeout
                    )
                    if message:
                        # Filter by command_id if specified
                        if command_id is None or message.command_id == command_id:
                            await self.protocol.handle_message(message.model_dump())

                except asyncio.TimeoutError:
                    # Timeout on recv - continue to check connection status
                    continue
                except zmq.ZMQError as e:
                    if e.errno == zmq.ETERM:
                        # Context terminated, normal shutdown
                        break
                    logger.error(f"ZMQ error in message listener: {e}")
                    break
                except asyncio.CancelledError:
                    logger.debug("Message listener cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in message listener: {e}")
                    break
        except Exception as e:
            logger.error(f"Unexpected error in message listener: {e}")

    def register_progress_handler(self, handler):
        """Register a handler for progress updates."""
        self.protocol.register_handler(StreamingMessageType.PROGRESS_UPDATE, handler)

    def register_status_handler(self, handler):
        """Register a handler for status messages."""
        self.protocol.register_handler(StreamingMessageType.STATUS_MESSAGE, handler)

    def register_output_handler(self, handler):
        """Register a handler for stream chunks."""
        self.protocol.register_handler(StreamingMessageType.STREAM_JSON, handler)

    def register_completion_handler(self, handler):
        """Register a handler for command completion."""
        self.protocol.register_handler(StreamingMessageType.COMMAND_COMPLETE, handler)

    def register_component_start_handler(self, handler):
        """Register a handler for component start messages."""
        self.protocol.register_handler(StreamingMessageType.COMPONENT_START, handler)

    def register_component_progress_handler(self, handler):
        """Register a handler for component progress messages."""
        self.protocol.register_handler(StreamingMessageType.COMPONENT_PROGRESS, handler)

    def register_component_complete_handler(self, handler):
        """Register a handler for component completion messages."""
        self.protocol.register_handler(StreamingMessageType.COMPONENT_COMPLETE, handler)

    def register_component_error_handler(self, handler):
        """Register a handler for component error messages."""
        self.protocol.register_handler(StreamingMessageType.COMPONENT_ERROR, handler)
