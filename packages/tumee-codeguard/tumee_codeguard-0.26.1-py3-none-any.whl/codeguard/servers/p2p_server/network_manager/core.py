"""
Core Network Manager - Main Orchestrator

The main HierarchicalNetworkManager that coordinates all specialized managers.
"""

import asyncio
import hashlib
import socket
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from ....ai_ownership.p2p_bridge import P2PAIOwnershipManager
from ....core.caching.manager import get_cache_manager
from ....core.interfaces import IFileSystemAccess, INetworkManager
from ....utils.logging_config import get_logger
from ..config import P2PConfig, get_p2p_service
from ..models import NodeMode
from ..p2p_manager.streaming_protocol import BrokerMessageSender, ZMQMessageSender
from ..worker_manager.worker_manager import BoundaryWorkerManager
from .discovery_manager import DiscoveryManager
from .health_monitor import HealthMonitor
from .message_handler import MessageHandler
from .socket_manager import SocketManager
from .topology_manager import TopologyManager

logger = get_logger(__name__)


class HierarchicalNetworkManager(INetworkManager):
    """P2P node that manages paths in a hierarchical network."""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_instance(
        cls,
        config: Optional[P2PConfig] = None,
        managed_paths: Optional[List[str]] = None,
        shutdown_event: Optional[asyncio.Event] = None,
        discovery_priority: int = 0,
        filesystem_access: Optional[IFileSystemAccess] = None,
        node_mode: NodeMode = NodeMode.SERVER,
    ) -> "HierarchicalNetworkManager":
        """Get or create the singleton instance."""
        async with cls._lock:
            if cls._instance is None:
                instance = cls.__new__(cls)
                instance.__init__(
                    config,
                    managed_paths,
                    shutdown_event,
                    discovery_priority,
                    filesystem_access,
                    node_mode,
                )
                cls._instance = instance
            return cls._instance

    def __init__(
        self,
        config: Optional[P2PConfig] = None,
        managed_paths: Optional[List[str]] = None,
        shutdown_event: Optional[asyncio.Event] = None,
        discovery_priority: int = 0,
        filesystem_access: Optional[IFileSystemAccess] = None,
        node_mode: NodeMode = NodeMode.SERVER,
    ):
        """
        Initialize a network node managing one or more paths.

        Args:
            config: P2P configuration object
            managed_paths: List of filesystem paths this node will manage
            shutdown_event: Shared shutdown event for graceful termination
            discovery_priority: Discovery service priority (0=monitor, 50=worker, 100=server)
            filesystem_access: Filesystem access interface for boundary discovery
        """
        # Configuration
        self.config = config or get_p2p_service().load_config()

        # Override managed paths if provided (keep them in original format)
        if managed_paths:
            self.config.managed_paths = [str(p) for p in managed_paths]

        # Validate configuration
        self.config.validate_paths()

        # Node identification - will be set in start_services() after port is determined
        self.node_id = ""
        self.discovery_priority = discovery_priority
        self.filesystem_access = filesystem_access
        self.node_mode = node_mode

        # Control
        self.running = False
        self.shutdown_event = shutdown_event or asyncio.Event()

        # Initialize specialized managers
        self.socket_manager = SocketManager(self.config)
        self.health_monitor = HealthMonitor(
            self.config, self.socket_manager, self.node_id, self.shutdown_event
        )
        self.message_handler = MessageHandler(
            self.socket_manager, self.health_monitor, self.node_id, self.shutdown_event, node_mode
        )
        self.topology_manager = TopologyManager(
            self.config,
            self.socket_manager,
            self.health_monitor,
            self.node_id,
            self.config.managed_paths,
            discovery_priority,
        )
        self.discovery_manager = DiscoveryManager(
            self.config,
            self.socket_manager,
            self.health_monitor,
            self.node_id,
            self.config.managed_paths,
            discovery_priority,
            self.shutdown_event,
            self.filesystem_access,
            get_cache_manager(),
            node_mode,
        )

        # Set up cross-references between managers
        self.message_handler.set_topology_manager(self.topology_manager)
        self.topology_manager.set_message_handler(self.message_handler)
        self.topology_manager.set_boundary_provider(self.discovery_manager)
        self.topology_manager.set_hierarchy_manager(self.discovery_manager.hierarchy_manager)

        # AI Ownership Management
        self.ai_ownership_manager = P2PAIOwnershipManager(self.config.managed_paths)
        self.message_handler.set_ai_ownership_manager(self.ai_ownership_manager)

        # Worker Management
        self.worker_manager = BoundaryWorkerManager(self.config, self)
        self.message_handler.set_worker_manager(self.worker_manager)
        self.message_handler.set_hierarchy_manager(self.discovery_manager.hierarchy_manager)

        # Streaming setup
        self.streaming_server: Optional[ZMQMessageSender] = None

        # Service tasks
        self.service_tasks: List[asyncio.Task] = []
        self._services_started: bool = False

        # Socket initialization will happen in start_services()
        self.port: int = 0  # Will be set to actual port in start_services()
        self.streaming_port: int = 0  # Will be set to actual port in start_services()

        # AI ownership registry - path -> AI capabilities
        self.ai_registry: Dict[str, Dict] = {}

        logger.info(f"P2P node {self.node_id} initialized (sockets will be bound on start)")
        logger.info(f"Managing paths: {self.config.managed_paths}")

        # Mark singleton as initialized
        self._initialized = True

    async def start_services(self):
        """Start all background services."""
        # Make idempotent - return early if already started
        if self._services_started:
            return

        # Skip all P2P networking for LOCAL mode
        if self.node_mode == NodeMode.LOCAL:
            logger.info("Node in LOCAL mode - skipping P2P network services")
            self._services_started = True
            self.running = True
            return

        logger.info("Starting P2P network services...")

        # Initialize sockets first (moved from __init__ to avoid blocking)
        self.port, self.streaming_port = await self.socket_manager.initialize_sockets()
        logger.info(
            f"Sockets initialized - Main port: {self.port}, Streaming port: {self.streaming_port}"
        )

        # Generate deterministic node ID based on host + stable ports (not discovery ports)
        hostname = socket.gethostname()
        host_ports_str = f"{hostname}:{self.port}:{self.streaming_port}"
        port_hash = hashlib.sha1(host_ports_str.encode()).hexdigest()[:8]
        self.node_id = f"{hostname}:{self.node_mode.value.lower()}:{port_hash}"
        logger.info(f"Node ID set to: {self.node_id} (from {host_ports_str})")

        # Update node_id in all managers that were created with empty node_id
        self.discovery_manager.node_id = self.node_id
        self.discovery_manager.hierarchy_manager.set_node_id(self.node_id)
        self.message_handler.node_id = self.node_id
        self.health_monitor.node_id = self.node_id

        try:
            # Initialize AI ownership manager
            await self.ai_ownership_manager.initialize()
        except Exception as e:
            logger.warning(f"AI ownership manager initialization failed: {e}")

        try:
            # Only servers and monitors get streaming servers for broadcasting
            if self.node_mode in [NodeMode.SERVER, NodeMode.MONITOR]:
                self.streaming_server = BrokerMessageSender(
                    self.streaming_port, self.socket_manager.context
                )
                await self.streaming_server.start()

                # Give message handler access to streaming server
                self.message_handler.streaming_server = self.streaming_server
            else:
                # Workers will create WorkerMessageSender per client in message handler
                self.streaming_server = None
                self.message_handler.streaming_server = None
        except Exception as e:
            logger.error(f"Streaming server start failed: {e}")
            print(f"🔧 STREAMING_SERVER_INIT: FAILED - {e}")
            self.streaming_server = None

        # Start specialized managers
        await self.health_monitor.start()
        await self.message_handler.start()
        await self.discovery_manager.start()

        # Start AI ownership monitoring task
        self.service_tasks = [
            asyncio.create_task(self._ai_ownership_monitor(), name="ai_ownership_monitor"),
        ]

        # Give services time to start
        await asyncio.sleep(0.1)

        # Mark as running now that services are started
        self.running = True
        self._services_started = True

        logger.info("P2P network services started successfully")

    async def shutdown(self):
        """Clean shutdown."""
        logger.info("Shutting down P2P network manager...")
        self.running = False
        self.shutdown_event.set()

        # Cancel service tasks first with graceful shutdown
        if hasattr(self, "service_tasks"):
            for task in self.service_tasks:
                if not task.done():
                    try:
                        await asyncio.wait_for(task, timeout=0.2)
                    except asyncio.TimeoutError:
                        if not task.done():
                            task.cancel()

            # Wait for tasks to complete cancellation
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.service_tasks, return_exceptions=True), timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some service tasks did not cancel in time")

        # Stop specialized managers
        await self.discovery_manager.stop()
        await self.message_handler.stop()
        await self.health_monitor.stop()

        # Stop streaming server
        if self.streaming_server:
            try:
                await asyncio.wait_for(self.streaming_server.stop(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Streaming server stop timed out")
            except Exception as e:
                logger.error(f"Error stopping streaming server: {e}")

        # Cleanup socket manager
        self.socket_manager.cleanup()

        logger.info("P2P network manager shut down complete")

    async def _ai_ownership_monitor(self):
        """Monitor AI ownership changes and update registry."""
        try:
            while self.running and not self.shutdown_event.is_set():
                try:
                    # Check for shutdown with timeout to prevent hanging
                    await asyncio.wait_for(
                        self.shutdown_event.wait(), timeout=30.0  # 30 second check interval
                    )
                    break  # Shutdown requested
                except asyncio.TimeoutError:
                    pass  # Continue with AI ownership check

                try:
                    # Refresh AI ownership registry periodically with timeout
                    await asyncio.wait_for(
                        self.ai_ownership_manager.refresh_ownership_registry(),
                        timeout=10.0,  # 10 second timeout for refresh
                    )

                    # Update our AI registry
                    self.ai_registry = self.ai_ownership_manager.generate_p2p_ownership_data()

                    # Log any changes
                    ai_owners = self.ai_ownership_manager.get_all_ai_owners()
                    if ai_owners:
                        logger.debug(f"AI ownership active for {len(ai_owners)} modules")

                except asyncio.TimeoutError:
                    logger.warning("AI ownership refresh timed out")
                except Exception as e:
                    if not self.shutdown_event.is_set():
                        logger.debug(f"AI ownership monitor error: {e}")

        except asyncio.CancelledError:
            logger.debug("AI ownership monitor task cancelled")

    # Convenience methods that delegate to managers
    def get_ai_owner_for_path(self, path: str) -> Optional[Dict]:
        """Get AI ownership information for a path."""
        return self.message_handler._get_ai_owner_for_path(path)

    def has_ai_capability_for_path(self, path: str, capability: str) -> bool:
        """Check if this node has AI capability for the given path."""
        return self.ai_ownership_manager.has_ai_capability_for_path(path, capability)

    async def query_ai_ownership(self, path: str) -> Optional[Dict]:
        """Query the network for AI ownership of a path."""
        # First check locally
        local_owner = self.get_ai_owner_for_path(path)
        if local_owner:
            return local_owner

        # Query other nodes
        for node_path, node_info in self.health_monitor.registry.items():
            if path.startswith(node_path):
                # Send AI ownership query
                query = {
                    "cmd": "query_ai_ownership",
                    "path": path,
                    "requesting_node": self.node_id,
                    "timestamp": time.time(),
                }

                response = await self.message_handler.send_to_node(node_info.address, query)
                if response and response.get("ai_owner"):
                    return response["ai_owner"]

        return None

    async def execute_ai_command(
        self, path: str, command: Dict, capability: Optional[str] = None
    ) -> Optional[Dict]:
        """Execute an AI command, routing to the appropriate owner."""
        # Find AI owner for this path
        ai_owner_info = self.ai_ownership_manager.get_ai_owner_for_path(path)

        if not ai_owner_info:
            return {"error": "No AI owner found for path", "path": path}

        # Check capability if specified
        if capability and capability not in ai_owner_info.capabilities:
            return {"error": f"AI owner does not have capability: {capability}", "path": path}

        # Execute locally since we have the AI owner
        return await self.message_handler._execute_local_ai_command(path, command, ai_owner_info)

    def find_owner(self, query_path: str):
        """Find the highest-level owner of a path."""
        return self.topology_manager.find_owner(query_path)

    # Interface compliance methods for INetworkManager
    async def start(self) -> None:
        """Start the network manager (INetworkManager interface method)."""
        await self.start_services()

    async def stop(self) -> None:
        """Stop the network manager (INetworkManager interface method)."""
        await self.shutdown()

    def is_running(self) -> bool:
        """Check if the network manager is running (INetworkManager interface method)."""
        return self.running

    async def register_path(self, path: str) -> bool:
        """Register a path with the P2P network (INetworkManager interface method)."""
        try:
            abs_path = str(Path(path).absolute())
            if abs_path not in self.config.managed_paths:
                self.config.managed_paths.append(abs_path)
                logger.info(f"Registered new path: {abs_path}")

                # Trigger re-discovery to announce new path
                await self.discovery_manager.send_announcement()
                return True
            return False
        except Exception as e:
            logger.error(f"Error registering path {path}: {e}")
            return False

    async def query_path_owner(self, path: str) -> Optional[str]:
        """Query who owns a specific path (INetworkManager interface method)."""
        owner = self.find_owner(path)
        return owner.node_id if owner else None

    async def query_path_ownership(self, path: str) -> Dict[str, Any]:
        """Query detailed path ownership information (INetworkManager interface method)."""
        owner = self.find_owner(path)
        if owner:
            # Parse host and port from address
            host, port = owner.address.split(":")
            return {
                "owner_node_id": owner.node_id,
                "owner_host": host,
                "owner_port": int(port),
                "managed_paths": owner.managed_paths,
                "is_owner": owner.node_id == self.node_id,
            }
        return {"is_owner": False}

    def get_managed_paths(self) -> List[str]:
        """Get list of managed paths (INetworkManager interface method)."""
        return self.config.managed_paths.copy()

    def get_local_ip(self) -> str:
        """Get local IP address for this network manager."""
        return self.socket_manager.get_local_ip()

    # Properties for accessing internal components
    @property
    def router(self):
        """Access to router socket."""
        return self.socket_manager.router

    @property
    def parent(self):
        """Access to parent node info."""
        return self.topology_manager.parent

    @property
    def children(self):
        """Access to children registry."""
        return self.topology_manager.children

    @property
    def registry(self):
        """Access to node registry."""
        return self.health_monitor.registry
