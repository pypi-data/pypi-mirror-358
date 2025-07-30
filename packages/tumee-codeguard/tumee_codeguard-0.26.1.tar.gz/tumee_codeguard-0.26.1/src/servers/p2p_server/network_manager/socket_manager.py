"""
Socket Manager for P2P Network

Handles ZMQ socket management, port allocation, and resource cleanup.
"""

import asyncio
import socket
import time
from typing import Optional

import zmq
import zmq.asyncio

from ....core.console_shared import CONSOLE, animate_console_line_ending, clear_console_line, cprint
from ....utils.logging_config import get_logger
from ..config import P2PConfig
from ..exceptions import NetworkError

logger = get_logger(__name__)


class SocketManager:
    """Manages ZMQ sockets and port allocation for P2P network."""

    def __init__(self, config: P2PConfig):
        """Initialize socket manager with configuration."""
        self.config = config
        self.context = zmq.asyncio.Context()

        # Main communication sockets
        self.router: Optional[zmq.asyncio.Socket] = None
        self.port: Optional[int] = None

        # Discovery sockets
        self.discovery_sub: Optional[zmq.asyncio.Socket] = None

        # Broker sockets (when acting as discovery broker)
        self.discovery_broker_pub: Optional[zmq.asyncio.Socket] = None
        self.discovery_broker_pull: Optional[zmq.asyncio.Socket] = None

        # Client sockets (when connecting to broker)
        self.discovery_push: Optional[zmq.asyncio.Socket] = None

        # Streaming port
        self.streaming_port: Optional[int] = None

        # Connection pool for DEALER sockets
        self.dealer_pool: dict[str, zmq.asyncio.Socket] = {}

    async def initialize_sockets(self) -> tuple[int, int]:
        """Initialize all sockets and return (main_port, streaming_port)."""
        # Find and bind main router socket
        self.port = await self._find_free_port()
        self.router = self.context.socket(zmq.ROUTER)
        self._configure_socket(self.router)

        try:
            self.router.bind(f"tcp://*:{self.port}")
            logger.info(f"Router socket bound to port {self.port}")
        except zmq.ZMQError as e:
            logger.error(f"Failed to bind router socket to port {self.port}: {e}")
            raise NetworkError(f"Could not bind to port {self.port}") from e

        # Initialize discovery subscriber socket (all nodes have this)
        self.discovery_sub = self.context.socket(zmq.SUB)

        # Find streaming port
        self.streaming_port = await self._find_free_streaming_port(self.port + 1000)

        return self.port, self.streaming_port

    def setup_discovery_broker(self) -> bool:
        """Try to become discovery broker with PUB+PULL pattern. Returns True if successful."""
        logger.debug(
            f"Attempting to bind discovery broker on ports {self.config.discovery_port} and {self.config.discovery_port + 1}"
        )
        try:
            # PUB socket for broadcasting to all subscribers
            self.discovery_broker_pub = self.context.socket(zmq.PUB)
            pub_addr = f"tcp://*:{self.config.discovery_port}"

            # Show spinner while binding
            animate_console_line_ending("🏠", f"Binding PUB socket to {pub_addr}...")
            logger.debug(f"Binding PUB socket to port {self.config.discovery_port}")
            self.discovery_broker_pub.bind(pub_addr)
            clear_console_line()
            cprint(f"✅ PUB socket bound successfully", mode=CONSOLE.VERBOSE)

            # PULL socket for receiving client announcements
            self.discovery_broker_pull = self.context.socket(zmq.PULL)
            pull_addr = f"tcp://*:{self.config.discovery_port + 1}"

            # Show spinner while binding
            animate_console_line_ending("🏠", f"Binding PULL socket to {pull_addr}...")
            logger.debug(f"Binding PULL socket to port {self.config.discovery_port + 1}")
            self.discovery_broker_pull.bind(pull_addr)
            clear_console_line()
            cprint(f"✅ PULL socket bound successfully", mode=CONSOLE.VERBOSE)

            # Broker doesn't need to subscribe to its own broadcasts
            # Control messages are processed directly in the relay task

            cprint(
                f"✅ Became discovery broker - PUB:{self.config.discovery_port}, PULL:{self.config.discovery_port + 1}",
                mode=CONSOLE.VERBOSE,
            )
            logger.info(
                f"Became discovery broker - PUB:{self.config.discovery_port}, PULL:{self.config.discovery_port + 1}"
            )
            return True

        except zmq.ZMQError as e:
            # Log as debug during retry attempts, caller can log error if final failure
            logger.debug(f"ZMQ error setting up discovery broker: {e}")
            if "Address already in use" in str(e):
                logger.debug(
                    f"Discovery ports {self.config.discovery_port}+{self.config.discovery_port + 1} already in use"
                )
                # Clean up any partial setup
                if self.discovery_broker_pub:
                    self.discovery_broker_pub.close()
                    self.discovery_broker_pub = None
                if self.discovery_broker_pull:
                    self.discovery_broker_pull.close()
                    self.discovery_broker_pull = None
                return False
            else:
                raise

    def connect_to_discovery_broker(self):
        """Connect to existing discovery broker as client with SUB+PUSH pattern."""
        try:
            # Create SUB socket if it doesn't exist
            if not self.discovery_sub:
                self.discovery_sub = self.context.socket(zmq.SUB)

            # SUB socket for receiving broadcasts from broker
            sub_addr = f"tcp://{self.config.discovery_host}:{self.config.discovery_port}"
            cprint(f"📡 Connecting SUB socket to: {sub_addr}", mode=CONSOLE.VERBOSE)
            self.discovery_sub.connect(sub_addr)
            self.discovery_sub.setsockopt(zmq.SUBSCRIBE, b"")

            # PUSH socket for sending announcements to broker
            self.discovery_push = self.context.socket(zmq.PUSH)
            push_addr = f"tcp://{self.config.discovery_host}:{self.config.discovery_port + 1}"
            cprint(f"📡 Connecting PUSH socket to: {push_addr}", mode=CONSOLE.VERBOSE)
            self.discovery_push.connect(push_addr)

            cprint(
                f"✅ Connected to discovery broker - SUB:{self.config.discovery_port}, PUSH:{self.config.discovery_port + 1}",
                mode=CONSOLE.VERBOSE,
            )
            logger.info(
                f"Connected to discovery broker - SUB:{self.config.discovery_port}, PUSH:{self.config.discovery_port + 1}"
            )
        except zmq.ZMQError as e:
            print(f"❌ Failed to connect to discovery broker: {e}")
            logger.error(f"Failed to connect to discovery broker: {e}")
            raise

    def close_discovery_sockets(self):
        """Close ALL discovery sockets without terminating context."""
        # Close broker sockets
        if self.discovery_broker_pub:
            self.discovery_broker_pub.setsockopt(zmq.LINGER, 100)
            self.discovery_broker_pub.close()
            self.discovery_broker_pub = None
        if self.discovery_broker_pull:
            self.discovery_broker_pull.setsockopt(zmq.LINGER, 100)
            self.discovery_broker_pull.close()
            self.discovery_broker_pull = None

        # Close client sockets
        if self.discovery_sub:
            self.discovery_sub.setsockopt(zmq.LINGER, 100)
            self.discovery_sub.close()
            self.discovery_sub = None
        if self.discovery_push:
            self.discovery_push.close()
            self.discovery_push = None

    async def close_discovery_broker(self):
        """Close discovery broker sockets and disconnect SUB from broker mode."""
        # Set linger to 100ms to allow pending sends to complete
        if self.discovery_broker_pub:
            self.discovery_broker_pub.setsockopt(zmq.LINGER, 100)
            self.discovery_broker_pub.close()
            self.discovery_broker_pub = None
            logger.debug("Discovery broker PUB socket closed")
        if self.discovery_broker_pull:
            self.discovery_broker_pull.setsockopt(zmq.LINGER, 100)
            self.discovery_broker_pull.close()
            self.discovery_broker_pull = None
            logger.debug("Discovery broker PULL socket closed")

        # CRITICAL: Disconnect SUB socket from localhost when stepping down as broker
        # This releases the port so another node can become broker
        if self.discovery_sub:
            try:
                self.discovery_sub.disconnect(f"tcp://127.0.0.1:{self.config.discovery_port}")
                logger.debug(f"SUB socket disconnected from localhost:{self.config.discovery_port}")
            except zmq.ZMQError as e:
                logger.debug(f"Error disconnecting SUB socket: {e}")
                # If disconnect fails, close and recreate the socket
                self.discovery_sub.close()
                self.discovery_sub = self.context.socket(zmq.SUB)
                logger.debug("SUB socket recreated after disconnect failure")

    async def disconnect_from_discovery_broker(self):
        """Disconnect SUB and PUSH sockets when becoming broker."""
        if self.discovery_sub:
            try:
                self.discovery_sub.disconnect(
                    f"tcp://{self.config.discovery_host}:{self.config.discovery_port}"
                )
                logger.debug(
                    f"SUB socket disconnected from {self.config.discovery_host}:{self.config.discovery_port}"
                )
            except zmq.ZMQError as e:
                logger.debug(f"Error disconnecting SUB socket: {e}")

        if self.discovery_push:
            self.discovery_push.close()
            self.discovery_push = None
            logger.debug("PUSH socket closed")

        # Wait for any pending messages to drain
        await asyncio.sleep(0.1)

    async def send_discovery_message(self, message: str) -> bool:
        """Send a discovery message asynchronously. Returns True if successful."""
        try:
            if self.discovery_broker_pub and not self.discovery_broker_pub.closed:
                # We are the broker - publish directly to all subscribers
                if '"cmd":"takeover_request"' in message or '"cmd":"takeover_response"' in message:
                    cprint(
                        f"📡 Sending via BROKER PUB socket: {message[:100]}...",
                        mode=CONSOLE.VERBOSE,
                    )
                await asyncio.wait_for(
                    self.discovery_broker_pub.send_string(message),
                    timeout=0.5,
                )
                return True
            elif self.discovery_push and not self.discovery_push.closed:
                # We are a client - push to broker for relay
                if '"cmd":"takeover_request"' in message or '"cmd":"takeover_response"' in message:
                    cprint(
                        f"📡 Sending via CLIENT PUSH socket: {message[:100]}...",
                        mode=CONSOLE.VERBOSE,
                    )
                await asyncio.wait_for(self.discovery_push.send_string(message), timeout=0.5)
                return True
            else:
                return False
        except (asyncio.TimeoutError, zmq.ZMQError, Exception):
            return False

    def get_or_create_dealer_socket(self, address: str) -> zmq.asyncio.Socket:
        """Get an existing dealer socket from pool or create a new one."""
        if address not in self.dealer_pool:
            dealer = self.context.socket(zmq.DEALER)
            self._configure_socket(dealer)
            dealer.connect(f"tcp://{address}")
            self.dealer_pool[address] = dealer
            logger.debug(f"Created new DEALER socket for {address}")
        return self.dealer_pool[address]

    def create_dealer_socket(self, address: str) -> zmq.asyncio.Socket:
        """Create a configured dealer socket for node communication (deprecated - use get_or_create_dealer_socket)."""
        dealer = self.context.socket(zmq.DEALER)
        self._configure_socket(dealer)
        dealer.connect(f"tcp://{address}")
        return dealer

    def _configure_socket(self, socket: zmq.asyncio.Socket):
        """Apply common socket configuration."""
        socket.setsockopt(zmq.LINGER, 1000)  # 1 second linger
        # Remove socket-level timeouts since we use asyncio.wait_for() for timeout control
        socket.setsockopt(zmq.RCVTIMEO, -1)  # No receive timeout at socket level
        socket.setsockopt(zmq.SNDTIMEO, -1)  # No send timeout at socket level

    async def _test_port_available(self, port: int, socket_type: int) -> bool:
        """Test if a port is available using the specified ZMQ socket type."""
        test_context = None
        test_socket = None
        try:
            test_context = zmq.asyncio.Context()
            test_socket = test_context.socket(socket_type)
            test_socket.setsockopt(zmq.LINGER, 0)
            test_socket.bind(f"tcp://*:{port}")
            test_socket.close()
            test_context.term()
            return True
        except zmq.ZMQError:
            if test_socket:
                try:
                    test_socket.close()
                except:
                    pass
            if test_context:
                try:
                    test_context.term()
                except:
                    pass
            return False

    async def _find_free_port(self) -> int:
        """Find a free port within the configured range using ZMQ."""
        for port in range(self.config.port_range_start, self.config.port_range_end + 1):
            if await self._test_port_available(port, zmq.ROUTER):
                return port

        raise NetworkError(
            f"No free ports available in range {self.config.port_range_start}-{self.config.port_range_end}"
        )

    async def _find_free_streaming_port(self, preferred_port: int) -> int:
        """Find a free port for streaming server using ZMQ, starting with preferred port."""
        # Try preferred port first
        for port in range(preferred_port, preferred_port + 100):  # Try 100 ports
            if await self._test_port_available(port, zmq.PUB):
                return port

        # Fallback to the main port range if preferred range is full
        for port in range(self.config.port_range_start, self.config.port_range_end + 1):
            if await self._test_port_available(port, zmq.PUB):
                return port

        raise NetworkError(f"No free streaming ports available starting from {preferred_port}")

    def get_local_ip(self) -> str:
        """Get local IP address using hostname resolution."""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            logger.warning("Could not determine local IP, using localhost")
            return "127.0.0.1"

    def cleanup(self):
        """Clean up all sockets and terminate context."""
        logger.info("Cleaning up socket manager...")

        # Close all sockets
        sockets_to_close = [
            ("router", self.router),
            ("discovery_sub", self.discovery_sub),
            ("discovery_broker_pub", self.discovery_broker_pub),
            ("discovery_broker_pull", self.discovery_broker_pull),
            ("discovery_push", self.discovery_push),
        ]

        for socket_name, socket_obj in sockets_to_close:
            if socket_obj:
                try:
                    socket_obj.close()
                    logger.debug(f"Closed {socket_name} socket")
                except Exception as e:
                    logger.debug(f"Error closing {socket_name} socket: {e}")

        # Close dealer pool sockets
        for address, dealer_socket in self.dealer_pool.items():
            try:
                dealer_socket.close()
                logger.debug(f"Closed DEALER socket for {address}")
            except Exception as e:
                logger.debug(f"Error closing DEALER socket for {address}: {e}")
        self.dealer_pool.clear()

        # Terminate context
        if self.context:
            try:
                self.context.term()
                logger.debug("ZMQ context terminated")
            except Exception as e:
                logger.debug(f"Error terminating ZMQ context: {e}")
