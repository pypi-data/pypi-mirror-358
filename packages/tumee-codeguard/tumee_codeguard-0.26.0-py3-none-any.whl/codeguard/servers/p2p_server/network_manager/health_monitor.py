"""
Health Monitor for P2P Network

Handles node health checking, dead node detection, and registry maintenance.
"""

import asyncio
import time
from typing import Dict, List, Optional

import zmq

from ....utils.logging_config import get_logger
from ..config import P2PConfig
from ..models import NodeInfo, PingMessage
from .socket_manager import SocketManager

logger = get_logger(__name__)


class HealthMonitor:
    """Monitors health of P2P network nodes and maintains registry."""

    def __init__(
        self,
        config: P2PConfig,
        socket_manager: "SocketManager",
        node_id: str,
        shutdown_event: asyncio.Event,
    ):
        """Initialize health monitor."""
        self.config = config
        self.socket_manager = socket_manager
        self.node_id = node_id
        self.shutdown_event = shutdown_event

        # Registry tracking
        self.registry: Dict[str, NodeInfo] = {}
        self.parent: Optional[NodeInfo] = None

        # Broker health tracking
        self.current_broker_priority = -1
        self.broker_last_seen = 0.0

        # Control
        self.running = False
        self.health_check_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start health monitoring."""
        self.running = True
        self.task_shutdown_event = asyncio.Event()
        self.health_check_task = asyncio.create_task(
            self._health_check_loop(self.task_shutdown_event)
        )
        logger.info("Health monitor started")

    async def stop(self):
        """Stop health monitoring."""
        self.running = False

        if self.health_check_task and not self.health_check_task.done():
            self.task_shutdown_event.set()
            try:
                await asyncio.wait_for(self.health_check_task, timeout=0.2)
            except asyncio.TimeoutError:
                if not self.health_check_task.done():
                    self.health_check_task.cancel()
                    try:
                        await self.health_check_task
                    except asyncio.CancelledError:
                        pass
        logger.info("Health monitor stopped")

    def update_node_registry(self, path: str, node_info: NodeInfo):
        """Update the node registry with new information."""
        self.registry[path] = node_info
        logger.debug(f"Updated registry for path {path}: {node_info.node_id}")

    def remove_node_from_registry(self, path: str) -> bool:
        """Remove a node from the registry. Returns True if removed."""
        if path in self.registry:
            del self.registry[path]
            logger.info(f"Removed dead node from registry: {path}")
            return True
        return False

    def set_parent(self, parent: Optional[NodeInfo]):
        """Set the parent node."""
        self.parent = parent
        if parent:
            logger.info(f"Parent set to: {parent.node_id}")
        else:
            logger.info("Parent cleared")

    def update_broker_status(self, priority: int, last_seen: float):
        """Update broker health status."""
        self.current_broker_priority = priority
        self.broker_last_seen = last_seen

    def is_broker_healthy(self) -> bool:
        """Check if current broker is healthy."""
        if self.current_broker_priority == -1 or self.broker_last_seen == 0:
            return False

        current_time = time.time()
        return (current_time - self.broker_last_seen) <= self.config.node_timeout

    def get_dead_nodes(self) -> List[str]:
        """Get list of paths for dead nodes."""
        current_time = time.time()
        dead_paths = []

        for path, info in self.registry.items():
            if current_time - info.timestamp > self.config.node_timeout:
                dead_paths.append(path)

        return dead_paths

    async def ping_node(self, node_info: NodeInfo) -> bool:
        """Ping a specific node to check if it's alive."""
        ping = PingMessage(node_id=self.node_id)

        try:
            dealer = self.socket_manager.create_dealer_socket(node_info.address)

            try:
                # Send ping
                await dealer.send_json(ping.model_dump())

                # Wait for response with timeout
                response = await asyncio.wait_for(dealer.recv_json(), timeout=5.0)
                return response.get("pong", False) is True

            except Exception as e:
                logger.debug(f"Ping error for {node_info.node_id}: {e}")
                return False
            finally:
                dealer.close()

        except Exception as e:
            logger.debug(f"Failed to create socket for ping to {node_info.node_id}: {e}")
            return False

    async def _health_check_loop(self, task_shutdown_event: asyncio.Event):
        """Main health checking loop."""
        try:
            start_time = time.time()
            while not task_shutdown_event.is_set() and not self.shutdown_event.is_set():
                if time.time() - start_time >= self.config.health_check_interval:
                    try:
                        await self._perform_health_checks()
                    except Exception as e:
                        if not self.shutdown_event.is_set():
                            logger.debug(f"Health checker error: {e}")
                    start_time = time.time()  # Reset timer for next interval
                await asyncio.sleep(0.1)  # Check shutdown every 100ms

        except asyncio.CancelledError:
            logger.debug("Health checker task cancelled")

    async def _perform_health_checks(self):
        """Perform all health checks."""
        # Check for dead nodes in registry
        dead_paths = self.get_dead_nodes()
        for path in dead_paths:
            self.remove_node_from_registry(path)

        # Check if our parent is alive
        if self.parent:
            try:
                is_alive = await asyncio.wait_for(self.ping_node(self.parent), timeout=5.0)
                if not is_alive:
                    logger.warning(f"Parent {self.parent.node_id} appears dead")
                    self.parent = None
                    # Signal topology change needed
                    await self._signal_topology_change()
            except asyncio.TimeoutError:
                if self.parent:
                    logger.warning(f"Parent {self.parent.node_id} ping timeout")
                else:
                    logger.error("Parent is None, cannot ping")
                self.parent = None
                await self._signal_topology_change()

    async def _signal_topology_change(self):
        """Signal that topology changes are needed (to be implemented by caller)."""
        # This will be connected to the topology manager
        logger.debug("Topology change signal triggered")

    def get_registry_stats(self) -> Dict:
        """Get registry statistics."""
        return {
            "total_nodes": len(self.registry),
            "has_parent": self.parent is not None,
            "parent_id": self.parent.node_id if self.parent else None,
            "broker_healthy": self.is_broker_healthy(),
            "broker_priority": self.current_broker_priority,
        }
