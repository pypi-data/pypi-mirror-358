"""
Discovery Manager for P2P Network

Handles discovery protocol, broker management, and node announcements.
"""

import asyncio
import hashlib
import json
import os
import time
import traceback
from typing import Callable, Dict, List, Optional, Tuple

import zmq

from ....core.console_shared import (
    CONSOLE,
    clear_console_line,
    cprint,
    spinner_print,
    update_spinner,
)
from ....core.filesystem.path_utils import (
    convert_to_username_path,
    expand_path_for_io,
    normalize_path_for_storage,
)
from ....core.interfaces import ICacheManager, IFileSystemAccess
from ....core.project.boundary_discovery import (
    discover_managed_boundaries,
    get_boundary_display_info,
)
from ....core.project.hierarchy_display import format_hierarchy_display_for_server
from ....utils.logging_config import get_logger
from ..config import P2PConfig
from ..models import DiscoveryAnnouncement, NodeInfo
from .boundary_manager import BoundaryManager
from .health_monitor import HealthMonitor
from .hierarchy_manager import HierarchyManager
from .interfaces import IBoundaryManager, IHierarchyManager
from .socket_manager import SocketManager

logger = get_logger(__name__)


def _zmq_exception_handler(discovery_manager):
    """Create a ZMQ exception handler that can access the discovery manager's state."""

    def handler(loop, context):
        """Custom exception handler to suppress expected ZMQ callback exceptions during shutdown."""
        # Check if this is the expected ZMQ callback CancelledError during shutdown
        if (
            discovery_manager.shutting_down  # Only suppress during shutdown
            and context.get("exception")
            and isinstance(context["exception"], asyncio.CancelledError)
            and context.get("handle")
            and "_AsyncSocket._deserialize" in str(context["handle"])
        ):
            # This is the known ZMQ callback issue during shutdown - suppress it
            logger.debug("Suppressed ZMQ callback CancelledError during shutdown")
            return

        # For all other exceptions, use the default handler
        loop.default_exception_handler(context)

    return handler


class DiscoveryManager:
    """Manages P2P discovery protocols and broker functionality."""

    def __init__(
        self,
        config: P2PConfig,
        socket_manager: SocketManager,
        health_monitor: HealthMonitor,
        node_id: str,
        managed_paths: List[str],
        discovery_priority: int,
        shutdown_event: asyncio.Event,
        filesystem_access: Optional[IFileSystemAccess] = None,
        cache_manager: Optional[ICacheManager] = None,
        node_mode=None,
    ):
        """Initialize discovery manager."""
        self.config = config
        self.socket_manager = socket_manager
        self.health_monitor = health_monitor
        self.node_id = node_id
        self.managed_paths = managed_paths
        self.discovery_priority = discovery_priority
        self.shutdown_event = shutdown_event
        self.filesystem_access = filesystem_access
        self.cache_manager = cache_manager

        # Initialize boundary manager
        self.boundary_manager: IBoundaryManager = BoundaryManager(
            config=config,
            managed_paths=managed_paths,
            filesystem_access=filesystem_access,
            cache_manager=cache_manager,
        )

        # Initialize hierarchy manager
        self.hierarchy_manager: IHierarchyManager = HierarchyManager(
            node_id=node_id,
            managed_paths=managed_paths,
            discovery_priority=discovery_priority,
            node_mode=node_mode,
        )

        # Broker management
        self.is_discovery_broker = False
        self.current_broker_priority = -1
        self.current_broker_address = ""
        self.current_broker_node_id = ""
        self.last_broker_announce_print = 0

        # Parent tracking for announcements
        self.parent_node_id: Optional[str] = None

        # Control
        self.running = False
        self.shutting_down = False  # Flag for suppressing ZMQ exceptions during shutdown
        self.tasks: Dict[str, Tuple[asyncio.Task, asyncio.Event]] = {}

        # Announcement tracking to reduce spam
        self._seen_nodes: Dict[str, float] = {}  # node_id -> last_announced_time

    async def start(self):
        """Start discovery services."""
        # Discover boundaries for all managed paths
        await self.boundary_manager.discover_boundaries()

        # Setup discovery based on priority
        await self._setup_priority_discovery()

        # Use common startup logic
        await self._start_common()

        logger.info("Discovery manager started")

    async def stop(self):
        """Stop discovery services."""
        self.running = False
        self.shutting_down = True

        # Set shutdown events and wait for graceful shutdown
        cprint("⏳ Stopping discovery manager...")
        for _, (task, shutdown_event) in self.tasks.items():
            if task and not task.done():
                shutdown_event.set()
        for _, (task, _) in self.tasks.items():
            if task and not task.done():
                try:
                    await asyncio.wait_for(task, timeout=1.0)
                except asyncio.TimeoutError:
                    if not task.done():
                        task.cancel()

        # Wait for all tasks to complete
        try:
            await asyncio.gather(
                *[task for task, _ in self.tasks.values() if task], return_exceptions=True
            )
        except Exception as e:
            logger.debug(f"Error stopping discovery tasks: {e}")

        # Clear task state for clean restart
        self.tasks.clear()
        self.shutdown_event.clear()

        logger.info("Discovery manager stopped")

    async def _stop_single_task(self, task_name: str, timeout: float = 1.0) -> bool:
        """Stop a single task gracefully using shutdown event, then cancel if needed.

        Args:
            task_name: Name of the task to stop
            timeout: Timeout for graceful shutdown before canceling

        Returns:
            True if task was stopped, False if task wasn't found
        """
        if task_name not in self.tasks:
            return False

        task, shutdown_event = self.tasks[task_name]
        if task.done():
            return True

        # Signal graceful shutdown first
        shutdown_event.set()

        try:
            # Wait for graceful shutdown
            await asyncio.wait_for(task, timeout=timeout)
        except asyncio.TimeoutError:
            # Force cancel if graceful shutdown failed
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        except Exception as e:
            logger.debug(f"Error stopping task {task_name}: {e}")

        # Remove from tasks dict
        del self.tasks[task_name]
        return True

    def set_parent(self, parent_node_id: Optional[str]):
        """Set parent node ID for announcements."""
        self.parent_node_id = parent_node_id

    def get_boundaries(self) -> Dict[str, List[Dict]]:
        """Get discovered boundaries keyed by managed path."""
        return self.boundary_manager.get_boundaries()

    async def send_announcement(self):
        """Send immediate discovery announcement."""
        # Skip announcements during shutdown or socket transitions
        if self.shutting_down or not self.running:
            return

        try:
            announcement = DiscoveryAnnouncement(
                node_id=self.node_id,
                address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
                managed_paths=self.managed_paths,
                boundaries=self.boundary_manager.get_boundaries(),
                parent=self.parent_node_id,
                discovery_priority=self.discovery_priority,
            )

            success = await self.socket_manager.send_discovery_message(
                announcement.model_dump_json()
            )
            if not success and not self.shutting_down:
                logger.warning("Failed to send discovery announcement (socket transitioning)")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if not self.shutting_down:
                logger.error(f"Error sending announcement: {e}")

    async def _setup_priority_discovery(self):
        """Setup discovery system based on priority."""
        try:
            # Only try to become broker if priority > 0
            if self.discovery_priority > 0:
                spinner_print("🏠", "Setting up discovery broker...")
                # Try to become discovery broker first
                broker_result = self.socket_manager.setup_discovery_broker()
                if broker_result:
                    # print("✅ Became discovery broker")
                    logger.info(f"Became discovery broker (priority={self.discovery_priority})")
                    self.is_discovery_broker = True
                    self.current_broker_priority = self.discovery_priority
                    self.current_broker_address = (
                        f"tcp://{self.config.discovery_host}:{self.config.discovery_port}"
                    )

                    # Add ourselves to known_nodes so we appear in hierarchy
                    self.hierarchy_manager.add_self_to_known_nodes(
                        address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
                        boundaries=self.boundary_manager.get_boundaries(),
                    )

                    # Build hierarchy tree from known nodes (including ourselves)
                    self.hierarchy_manager.rebuild_hierarchy_tree(is_broker=True)

                    # Small delay to ensure sockets are fully ready before clients connect
                    await asyncio.sleep(0.1)
                else:
                    # Port in use - existing broker detected, connect as client
                    cprint("📡 🔗 Connecting to existing discovery broker...", mode=CONSOLE.VERBOSE)
                    logger.debug(
                        f"Port in use, connecting as client (priority={self.discovery_priority})"
                    )
                    self.socket_manager.connect_to_discovery_broker()

                    # Send immediate announcement to trigger broker response
                    await self.send_announcement()

                    # Brief wait to ensure announcement is processed
                    await asyncio.sleep(0.2)

                    # Request takeover immediately if we have higher priority
                    await self._request_takeover_if_higher_priority()
            else:
                # Priority 0 - workers never try to become broker, just connect as client
                cprint(
                    f"🔧 Priority 0 worker connecting as client (priority={self.discovery_priority})"
                )
                logger.info(
                    f"Worker connecting as client only (priority={self.discovery_priority})"
                )
                self.socket_manager.connect_to_discovery_broker()
                cprint("🔧 Broker connection attempt completed")

                # Wait for broker announcements - priority 0 workers never request takeover
                cprint("🔧 Waiting for broker announcements...")
                logger.info(
                    "Priority 0 worker waiting for broker announcements (no takeover requests)"
                )

                # Poll for broker announcements with early break when received
                start_time = time.time()
                max_wait_time = 1.0  # Maximum 1 second (same as before)
                poll_interval = 0.05  # Check every 50ms

                while time.time() - start_time < max_wait_time:
                    if self.current_broker_priority != -1:
                        # Broker announcement received - break early
                        elapsed = time.time() - start_time
                        logger.debug(f"Broker announcement received after {elapsed:.2f}s")
                        break
                    await asyncio.sleep(poll_interval)
                cprint(
                    f"🔧 Connected as priority 0 worker - broker priority: {self.current_broker_priority}"
                )
                logger.info(
                    f"Priority 0 worker connected - current broker priority: {self.current_broker_priority}"
                )
        except Exception as e:
            logger.error(f"Failed to setup priority discovery: {e}")
            raise

    async def _broadcast_presence(self, task_shutdown_event: asyncio.Event):
        """Broadcast our presence via ZMQ PUB socket."""
        try:
            # Small delay to ensure sockets are fully initialized before first announcement
            await asyncio.sleep(0.2)

            # Send initial broadcast after socket setup is complete
            await self.send_announcement()
            logger.info(f"Started heartbeat broadcasts every {self.config.broadcast_interval}s")

            start_time = time.time()
            heartbeat_count = 0
            while not task_shutdown_event.is_set() and not self.shutdown_event.is_set():
                if time.time() - start_time >= self.config.broadcast_interval:
                    await self.send_announcement()

                    # Update our own timestamp if we're the broker (since we don't receive our own announcements)
                    if self.is_discovery_broker:
                        known_nodes = self.hierarchy_manager.get_known_nodes()
                        if self.node_id in known_nodes:
                            known_nodes[self.node_id]["last_seen"] = time.time()

                    heartbeat_count += 1
                    if heartbeat_count % 10 == 0:  # Log every 10th heartbeat
                        logger.info(f"Sent {heartbeat_count} heartbeats for {self.node_id}")
                    start_time = time.time()  # Reset timer for next interval
                await asyncio.sleep(0.1)  # Check shutdown every 100ms

        except asyncio.CancelledError:
            logger.debug("Broadcast presence task cancelled")

    async def _discovery_listener(self, task_shutdown_event: asyncio.Event):
        """Listen for ZMQ discovery broadcasts using proper async patterns."""
        try:
            logger.debug(f"Discovery listener active on port {self.config.discovery_port}")

            # Client spinner timing
            animation_time = time.time()
            last_heartbeat_time = time.time()

            while not task_shutdown_event.is_set() and not self.shutdown_event.is_set():
                try:
                    # Only display this in monitor mode (no paths managed)
                    if len(self.managed_paths) == 0:
                        current_time = time.time()

                        # Trigger heartbeat visualization every 10 seconds
                        if current_time - last_heartbeat_time >= 10:
                            if not self.is_discovery_broker:
                                spinner_print("📡", "Listening for messages...", custom_icon="💓")
                            last_heartbeat_time = current_time

                        # Show client spinner every 333ms (if not broker)
                        if not self.is_discovery_broker and current_time - animation_time >= 0.333:
                            # Show continuous client spinner animation
                            spinner_print("📡", "Listening for messages...")
                            animation_time = current_time

                    # Use proper async recv with timeout
                    try:
                        if not self.socket_manager.discovery_sub:
                            await asyncio.sleep(0.1)  # Brief sleep if no socket
                            continue
                        # Use direct recv - ZMQ asyncio handles integration properly
                        message_data = await self.socket_manager.discovery_sub.recv_string()
                        announcement_data = json.loads(message_data)

                        # Skip ALL messages from ourselves (including broker announcements)
                        if announcement_data.get("node_id") == self.node_id:
                            continue

                        # Track nodes for join/leave detection using hierarchy manager
                        sender_node = announcement_data.get("node_id", "unknown")
                        current_time = time.time()

                        # Detect new nodes joining and update node registry
                        is_new_node = self.hierarchy_manager.add_known_node(
                            sender_node, announcement_data
                        )

                        # Add metadata for targeted announcements
                        announcement_data["_is_new_node"] = is_new_node

                        # Check if this is a discovery control message
                        if "cmd" in announcement_data and announcement_data["cmd"] in [
                            "announce",
                            "broker_announce",
                            "takeover_request",
                            "broker_stepdown",
                            "takeover_response",
                        ]:
                            await self._handle_discovery_control_message(announcement_data)
                            continue

                        # Regular discovery announcement
                        await self._handle_discovery_announcement(announcement_data)

                    except zmq.ZMQError as e:
                        # Socket closed or other ZMQ error
                        logger.debug(f"ZMQ error in discovery listener: {e}")
                        break
                    except asyncio.CancelledError:
                        # Task cancelled during recv operation - this is expected during shutdown
                        logger.debug("Discovery listener recv cancelled during shutdown")
                        break
                    except json.JSONDecodeError as e:
                        logger.debug(f"Invalid JSON in discovery message: {e}")
                    except Exception as e:
                        logger.debug(f"Discovery message processing error: {e}")

                except asyncio.CancelledError:
                    # Task cancelled in outer loop
                    break
                except Exception as e:
                    logger.debug(f"Discovery listener error: {e}")
                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            logger.debug("Discovery listener task cancelled")
        except Exception as e:
            logger.error(f"Discovery listener setup error: {e}")
        finally:
            # Clear the animated line when task ends (for clients)
            if not self.is_discovery_broker:
                clear_console_line()

    async def _broker_announcer(self, task_shutdown_event: asyncio.Event):
        """Announce broker status if we are the discovery broker."""
        try:
            start_time = time.time()
            animation_time = time.time()
            last_cleanup_time = time.time()
            last_heartbeat_time = time.time()

            while not task_shutdown_event.is_set() and not self.shutdown_event.is_set():
                current_time = time.time()

                # Send broker announcement periodically
                if current_time - start_time >= self.config.broadcast_interval:
                    if self.is_discovery_broker:
                        await self._send_broker_announcement()
                    start_time = current_time  # Reset timer for next interval

                # Trigger heartbeat visualization every 10 seconds
                if current_time - last_heartbeat_time >= 10:
                    if self.is_discovery_broker:
                        spinner_print("🏠", "Waiting for others to join...", custom_icon="💓")
                    last_heartbeat_time = current_time

                # Check for nodes that have left (every 10 seconds)
                if current_time - last_cleanup_time >= 10:
                    departed_nodes = self.hierarchy_manager.check_for_departed_nodes(
                        self.config.node_timeout
                    )
                    # Handle broker failover if needed
                    for node_id in departed_nodes:
                        if (
                            not self.is_discovery_broker
                            and self.current_broker_node_id
                            and node_id == self.current_broker_node_id
                        ):
                            print(f"🔄 Current broker left, attempting takeover...")
                            # Reset broker state
                            self.current_broker_priority = -1
                            self.current_broker_address = ""
                            self.current_broker_node_id = ""
                            asyncio.create_task(self._setup_priority_discovery())
                    last_cleanup_time = current_time

                # Show animated status every 333ms (3 times per second)
                if self.is_discovery_broker and current_time - animation_time >= 0.333:
                    update_spinner()  # Update current spinner state
                    animation_time = current_time

                await asyncio.sleep(0.1)  # Check shutdown every 100ms

        except asyncio.CancelledError:
            logger.debug("Broker announcer task cancelled")
        finally:
            # Clear the animated line when task ends
            if self.is_discovery_broker:
                clear_console_line()

    async def _send_broker_announcement(self, target_nodes: Optional[List[str]] = None):
        """Send broker announcement (used for both periodic and immediate announcements).

        Args:
            target_nodes: List of specific node IDs to send to. If None, broadcasts to all.
        """
        if not self.is_discovery_broker:
            return

        # Check if broker sockets are available before attempting to send
        if not self.socket_manager.discovery_broker_pub:
            logger.debug("Broker announcement skipped: no broker socket available")
            return

        try:
            # Get current hierarchy state
            hierarchy_state = self.hierarchy_manager.get_hierarchy_state()

            broker_announcement = {
                "cmd": "broker_announce",
                "node_id": self.node_id,
                "broker_priority": self.discovery_priority,
                "broker_address": self.current_broker_address,
                "active_since": time.time(),
                "hierarchy": hierarchy_state,
            }

            success = await self.socket_manager.send_discovery_message(
                json.dumps(broker_announcement)
            )
            if success:
                if target_nodes:
                    logger.debug(
                        f"Targeted broker announcement sent to {target_nodes} (priority={self.discovery_priority})"
                    )
                else:
                    logger.debug(
                        f"Broadcast broker announcement sent (priority={self.discovery_priority})"
                    )
            else:
                logger.debug("Broker announcement failed (socket may be transitioning)")
        except asyncio.CancelledError:
            logger.debug("Broker announcement cancelled during task transition")
        except Exception as e:
            logger.error(f"Broker announcement error: {e}")
            print(f"💥 EXCEPTION in _send_broker_announcement: {e}")
            traceback.print_exc()

    async def _handle_discovery_announcement(self, announcement_data: Dict):
        """Handle regular discovery announcements."""
        try:
            announcement = DiscoveryAnnouncement(**announcement_data)

            if announcement.node_id != self.node_id:
                # Only log announcement once per minute per node to avoid spam
                current_time = time.time()
                last_announced = self._seen_nodes.get(announcement.node_id, 0)
                if current_time - last_announced >= 60:  # 60 seconds
                    cprint(
                        f"📡 Broker received announcement from: {announcement.node_id}",
                        mode=CONSOLE.VERBOSE,
                    )
                    self._seen_nodes[announcement.node_id] = current_time

                # Update registry with new node information
                for path in announcement.managed_paths:
                    node_info = NodeInfo(
                        node_id=announcement.node_id,
                        address=announcement.address,
                        managed_paths=announcement.managed_paths,
                        boundaries=announcement.boundaries,
                        parent=announcement.parent,
                        timestamp=announcement.timestamp or time.time(),
                    )
                    self.health_monitor.update_node_registry(path, node_info)

                logger.debug(f"Updated registry from announcement: {announcement.node_id}")

                # Add node to hierarchy manager's known nodes
                is_new_node = self.hierarchy_manager.add_known_node(
                    announcement.node_id, announcement_data
                )

                # CRITICAL: If we're the broker, respond to announcements IMMEDIATELY
                if self.is_discovery_broker:
                    if is_new_node:
                        # New node - rebuild hierarchy and broadcast to all
                        self.hierarchy_manager.rebuild_hierarchy_tree(is_broker=True)
                        await self._send_broker_announcement()
                    else:
                        # Existing node - send targeted announcement immediately
                        await self._send_broker_announcement(target_nodes=[announcement.node_id])

                    self._seen_nodes[announcement.node_id] = current_time
                # Clients don't send broker announcements - no need to log this

        except Exception as e:
            logger.error(f"Error handling discovery announcement: {e}")
            print(f"💥 EXCEPTION in _handle_discovery_announcement: {e}")
            traceback.print_exc()

    async def _handle_discovery_control_message(self, data: Dict):
        """Handle discovery control messages for broker priority management."""
        cmd = data.get("cmd", "")

        if cmd == "announce":
            await self._handle_discovery_announcement(data)
        elif cmd == "broker_announce":
            await self._handle_broker_announcement(data)
        elif cmd == "takeover_request":
            await self._handle_takeover_request(data)
        elif cmd == "broker_stepdown":
            await self._handle_broker_stepdown(data)
        elif cmd == "takeover_response":
            await self._handle_takeover_response(data)

    async def _handle_broker_announcement(self, data: Dict):
        """Handle announcement from an active broker."""
        broker_priority = data.get("broker_priority", 0)
        broker_address = data.get("broker_address", "")
        broker_node_id = data.get("node_id", "unknown")

        # Only print status once per minute to avoid spam
        current_time = time.time()
        if current_time - self.last_broker_announce_print >= 60:
            if self.is_discovery_broker:
                cprint(f"🏠 I am broker: {self.node_id} (priority={self.discovery_priority})")
            else:
                cprint(
                    f"📡 Using remote broker: {broker_node_id} (priority={broker_priority})",
                    mode=CONSOLE.VERBOSE,
                )
            self.last_broker_announce_print = current_time

        # Update broker info if this is from the current broker or a higher priority one
        if (
            self.current_broker_priority == -1  # Haven't seen a broker yet
            or broker_priority >= self.current_broker_priority  # Higher/equal priority
            or broker_node_id == self.current_broker_node_id  # Same broker
        ):
            self.current_broker_priority = broker_priority
            self.current_broker_address = broker_address
            self.current_broker_node_id = broker_node_id

            # Update health monitor
            self.health_monitor.update_broker_status(broker_priority, time.time())

            # Extract and cache hierarchy data from broker announcement
            if not self.is_discovery_broker:  # Only clients cache hierarchy from broker
                hierarchy_data = data.get("hierarchy", {})
                self.hierarchy_manager.update_hierarchy_cache_from_broker(hierarchy_data)

            if self.is_discovery_broker and broker_priority > self.discovery_priority:
                logger.info(f"Higher priority broker ({broker_priority}) detected, stepping down")
                await self._step_down_as_broker()

    async def _handle_takeover_request(self, data: Dict):
        """Handle takeover request from another service."""
        requester_priority = data.get("requester_priority", 0)
        requester_node = data.get("node_id", "unknown")

        cprint(
            f"🏠 Received takeover request from {requester_node} (priority={requester_priority})",
            mode=CONSOLE.VERBOSE,
        )

        if not self.is_discovery_broker:
            cprint(f"❌ Not a broker, ignoring takeover request", mode=CONSOLE.VERBOSE)
            return
        if requester_priority > self.discovery_priority:
            logger.info(
                f"Approving takeover request from higher priority service ({requester_priority})"
            )

            # Send approval response with hierarchy state transfer
            response = {
                "cmd": "takeover_response",
                "node_id": self.node_id,
                "approved": True,
                "current_broker_priority": self.discovery_priority,
                "handover_delay": 0.2,
                "hierarchy": self.hierarchy_manager.get_hierarchy_tree(),
            }

            cprint(
                f"🏠 📤 Sending takeover approval to priority {requester_priority}",
                mode=CONSOLE.VERBOSE,
            )
            success = await self.socket_manager.send_discovery_message(json.dumps(response))
            if not success:
                cprint("❌ Failed to send takeover approval - socket may be closed")
                return

            # Wait to ensure response is delivered before closing sockets
            await asyncio.sleep(0.5)  # Longer delay to ensure message delivery

            cprint(
                f"🏠 📤 STEPPING DOWN: Handing broker role to higher priority service (priority={requester_priority})"
            )
            await self._step_down_as_broker()
            # Add extra delay after stepdown to ensure socket is fully released
            await asyncio.sleep(0.3)
            # Create restart task after stop is completely done
            asyncio.create_task(self._deferred_client_restart())
        else:
            # Deny takeover
            response = {
                "cmd": "takeover_response",
                "node_id": self.node_id,
                "approved": False,
                "current_broker_priority": self.discovery_priority,
            }

            await self.socket_manager.send_discovery_message(json.dumps(response))

    async def _handle_takeover_response(self, data: Dict):
        """Handle takeover response from current broker."""
        approved = data.get("approved", False)
        current_broker_priority = data.get("current_broker_priority", 0)

        if approved:
            handover_delay = data.get("handover_delay", 0.2)
            logger.info(f"Takeover approved, waiting {handover_delay}s for handover")

            # Inherit hierarchy state from outgoing broker
            hierarchy_data = data.get("hierarchy")
            if hierarchy_data:
                logger.info("Inheriting hierarchy state from outgoing broker")
                self.hierarchy_manager.inherit_hierarchy_state(
                    hierarchy_state=hierarchy_data,
                    address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
                    boundaries=self.boundary_manager.get_boundaries(),
                )

            await asyncio.sleep(handover_delay)

            # Attempt to become broker with retry loop
            if not self.is_discovery_broker:
                max_attempts = 20  # 2 seconds total (20 * 100ms)

                # Show spinner for takeover attempts
                for attempt in range(max_attempts):
                    spinner_print(
                        "🏠", f"Taking over broker role... (attempt {attempt + 1}/{max_attempts})"
                    )

                    # Disconnect from old broker before becoming new broker
                    if attempt == 0:  # Only disconnect on first attempt
                        await self.socket_manager.disconnect_from_discovery_broker()
                        await asyncio.sleep(0.2)  # Brief pause to ensure disconnect
                    if self.socket_manager.setup_discovery_broker():
                        self.is_discovery_broker = True
                        self.current_broker_priority = self.discovery_priority
                        cprint(
                            f"✅ TAKEOVER SUCCESS: Now acting as discovery broker (priority={self.discovery_priority})"
                        )
                        logger.info(
                            f"Successfully took over as discovery broker (priority={self.discovery_priority}) after {attempt + 1} attempts"
                        )

                        # Finalize broker takeover by adding ourselves to hierarchy
                        self.hierarchy_manager.finalize_broker_takeover(
                            address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
                            boundaries=self.boundary_manager.get_boundaries(),
                            is_broker=self.is_discovery_broker,
                        )

                        # Restart tasks with new broker sockets to prevent message drops
                        await self._restart_tasks_for_broker_mode()

                        # Send immediate broker announcement with inherited hierarchy data
                        await self._send_broker_announcement()
                        break
                    else:
                        if attempt < max_attempts - 1:  # Don't sleep on last attempt
                            await asyncio.sleep(0.4)  # 400ms between attempts
                else:
                    cprint(
                        f"❌ TAKEOVER FAILED: Could not bind broker socket after {max_attempts} attempts"
                    )
                    logger.error(
                        f"Failed to setup discovery broker after {max_attempts} attempts over 2 seconds"
                    )
        else:
            logger.debug(f"Takeover denied by broker (priority={current_broker_priority})")

    async def _stop_tasks(self, task_names: Optional[List[str]] = None):
        """Stop specified tasks cleanly. If no task_names provided, stops all tasks."""
        stopping_all = task_names is None
        if stopping_all:
            task_names = list(self.tasks.keys())

        stopped_count = 0
        for task_name in task_names:
            if await self._stop_single_task(task_name):
                stopped_count += 1

        if stopped_count > 0:
            logger.debug(f"Stopped {stopped_count} tasks: {task_names}")

        # Clear the tasks dictionary when stopping all tasks
        if stopping_all:
            self.tasks.clear()

    async def _start_mode_appropriate_tasks(self):
        """Start tasks appropriate for current mode (broker vs client)."""
        tasks_to_start = [
            ("broadcast", self._broadcast_presence),
            ("listener", self._discovery_listener),
            ("announcer", self._broker_announcer),
        ]

        # Add boundary monitoring task if cache manager is available
        if self.cache_manager and self.config.boundary_cache_enabled:
            tasks_to_start.append(("boundary_monitor", self._boundary_monitor_wrapper))

        if self.is_discovery_broker:
            tasks_to_start.append(("relay", self._broker_message_relay))
            cprint(
                f"🏠 Added relay task - is_broker={self.is_discovery_broker}", mode=CONSOLE.VERBOSE
            )

        cprint(
            f"🔧 Starting {len(tasks_to_start)} tasks: {[name for name, _ in tasks_to_start]}".replace(
                "'", ""
            )
            .replace("[", "")
            .replace("]", ""),
            mode=CONSOLE.VERBOSE,
        )
        for task_name, task_func in tasks_to_start:
            task_event = asyncio.Event()
            self.tasks[task_name] = (
                asyncio.create_task(task_func(task_event)),
                task_event,
            )

    async def _start_tasks(self, tasks_to_start: List[Tuple[str, Callable]]):
        """Start specified tasks."""
        for task_name, task_func in tasks_to_start:
            task_event = asyncio.Event()
            self.tasks[task_name] = (
                asyncio.create_task(task_func(task_event)),
                task_event,
            )
        logger.debug(f"Started {len(tasks_to_start)} tasks")

    async def _restart_tasks_for_broker_mode(self):
        """Restart tasks after becoming broker to prevent socket mismatch issues."""
        logger.debug("Restarting tasks for broker mode")

        # Stop tasks that use client sockets
        await self._stop_tasks(["broadcast", "announcer"])

        # Start tasks with new broker sockets
        await self._start_tasks(
            [
                ("broadcast", self._broadcast_presence),
                ("announcer", self._broker_announcer),
                ("relay", self._broker_message_relay),
            ]
        )

        logger.debug("Tasks restarted for broker mode")

    async def _deferred_client_restart(self):
        """Restart tasks as client in clean async context after stepdown."""
        try:
            # Wait for broker to fully release ports and stop process to complete
            await asyncio.sleep(1.0)

            # Reconnect as client
            cprint("🔄 Reconnecting as client...")
            self.socket_manager.connect_to_discovery_broker()

            # Use the common startup logic
            await self._start_common()
            cprint("✅ Client mode activated with fresh tasks")

        except Exception as e:
            logger.error(f"Failed to restart as client: {e}")
            cprint(f"❌ Failed to restart as client: {e}")

    async def _start_common(self):
        """Common startup logic shared between start() and client restart."""
        # Reset running state
        self.running = True
        self.shutting_down = False

        # Set custom exception handler to suppress known ZMQ callback issues during shutdown
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(_zmq_exception_handler(self))

        # Start background tasks with shutdown events
        await self._start_mode_appropriate_tasks()

    async def _handle_broker_stepdown(self, data: Dict):
        """Handle notification that the current broker is stepping down."""
        broker_priority = data.get("broker_priority", 0)

        if broker_priority >= self.current_broker_priority:
            logger.info("Current broker stepping down, evaluating takeover")
            self.current_broker_priority = -1
            self.current_broker_address = ""

            # Try to become broker if no higher priority services
            await asyncio.sleep(0.1)  # Brief delay to avoid conflicts
            if not self.is_discovery_broker:
                if self.socket_manager.setup_discovery_broker():
                    self.is_discovery_broker = True
                    logger.info(
                        f"Took over as discovery broker (priority={self.discovery_priority})"
                    )

    async def _wait_for_broker_announcement(self):
        """Wait for broker announcement with timeout."""
        max_wait = 0.5  # 500ms max wait
        start_time = time.time()

        cprint("⏳ Waiting for broker announcement...", mode=CONSOLE.VERBOSE)
        while time.time() - start_time < max_wait:
            if self.current_broker_priority != -1:
                cprint(
                    f"✅ Received broker announcement (priority={self.current_broker_priority})",
                    mode=CONSOLE.VERBOSE,
                )
                return
            await asyncio.sleep(0.01)  # 10ms intervals

        cprint("⚠️ No broker announcement received within timeout", mode=CONSOLE.VERBOSE)

    async def _request_takeover_if_higher_priority(self):
        """Request takeover if our priority is higher than current broker."""
        cprint(
            f"🔍 Checking takeover: our_priority={self.discovery_priority}, broker_priority={self.current_broker_priority}, is_broker={self.is_discovery_broker}",
            mode=CONSOLE.VERBOSE,
        )

        if self.is_discovery_broker:
            cprint("🏠 Already the broker, skipping takeover check", mode=CONSOLE.VERBOSE)
            return  # We're already the broker

        # Check if we have higher priority than current broker
        if (
            self.current_broker_priority == -1  # Haven't heard from broker yet
            or self.discovery_priority > self.current_broker_priority
        ):
            cprint(
                f"📤 Requesting takeover - our priority ({self.discovery_priority}) > current broker ({self.current_broker_priority})",
                mode=CONSOLE.VERBOSE,
            )

            takeover_request = {
                "cmd": "takeover_request",
                "node_id": self.node_id,
                "requester_priority": self.discovery_priority,
                "timestamp": time.time(),
            }

            cprint(f"📤 Sending takeover request: {takeover_request}", mode=CONSOLE.VERBOSE)
            success = await self.socket_manager.send_discovery_message(json.dumps(takeover_request))
            cprint(f"📤 Takeover request send result: {success}", mode=CONSOLE.VERBOSE)
        else:
            cprint(
                f"⏸️ No takeover needed - our priority ({self.discovery_priority}) <= current broker ({self.current_broker_priority})",
                mode=CONSOLE.VERBOSE,
            )

    async def _step_down_as_broker(self):
        """Step down from discovery broker role."""
        if not self.is_discovery_broker:
            return

        logger.info("Stepping down as discovery broker")

        # Set shutdown flags immediately to stop task operations
        self.running = False
        self.shutting_down = True

        # Send final stepdown message
        stepdown_msg = {
            "cmd": "broker_stepdown",
            "node_id": self.node_id,
            "broker_priority": self.discovery_priority,
            "timestamp": time.time(),
        }

        success = await self.socket_manager.send_discovery_message(json.dumps(stepdown_msg))
        if success:
            # Brief flush time for final message, then release ports immediately
            await asyncio.sleep(0.05)  # Minimal delay just to flush buffers

        # Stop all tasks immediately to prevent socket errors
        await self._stop_tasks()

        # Set broker status and close sockets
        self.is_discovery_broker = False
        self.current_broker_priority = -1
        self.socket_manager.close_discovery_sockets()

        logger.info("Broker stepdown completed")

    async def _broker_message_relay(self, task_shutdown_event: asyncio.Event):
        """Relay client messages when acting as broker (PULL → PUB forwarding)."""
        if not self.is_discovery_broker:
            cprint("❌ Relay task started but not broker, exiting", mode=CONSOLE.VERBOSE)
            return

        cprint("🏠 Starting broker message relay (PULL → PUB)", mode=CONSOLE.VERBOSE)
        logger.debug("Starting broker message relay (PULL → PUB)")

        try:
            while (
                not task_shutdown_event.is_set()
                and self.is_discovery_broker
                and not self.shutdown_event.is_set()
            ):
                try:
                    # Check for shutdown
                    if self.shutdown_event.is_set():
                        break

                    # Check socket validity before operations
                    if (
                        not self.socket_manager.discovery_broker_pull
                        or not self.socket_manager.discovery_broker_pub
                    ):
                        logger.debug("Broker sockets not available, stopping relay")
                        break

                    # Use non-blocking recv to allow shutdown checks
                    try:
                        message = await self.socket_manager.discovery_broker_pull.recv_string(
                            zmq.NOBLOCK
                        )
                        # Process control messages locally before relaying
                        try:
                            message_data = json.loads(message)
                            if "cmd" in message_data and message_data["cmd"] in [
                                "takeover_request",
                                "broker_stepdown",
                            ]:
                                cprint(
                                    f"🏠 Processing control message locally: {message_data['cmd']}",
                                    mode=CONSOLE.VERBOSE,
                                )
                                # Process control message but don't await to avoid recursive cancellation
                                asyncio.create_task(
                                    self._handle_discovery_control_message(message_data)
                                )
                                cprint(
                                    f"🏠 Control message processing scheduled", mode=CONSOLE.VERBOSE
                                )
                        except json.JSONDecodeError:
                            pass  # Not JSON, just relay as-is
                        except Exception as e:
                            logger.debug(f"Error processing control message: {e}")

                        # Broadcast to all subscribers (including monitor)
                        if (
                            self.socket_manager.discovery_broker_pub
                            and not self.socket_manager.discovery_broker_pub.closed
                        ):
                            try:
                                await asyncio.wait_for(
                                    self.socket_manager.discovery_broker_pub.send_string(message),  # type: ignore
                                    timeout=0.1,  # 100ms timeout for relays
                                )
                                # Check if we're still broker after processing (may have stepped down)
                                # status_icon = "🏠" if self.is_discovery_broker else "📡"
                                # print(f"{status_icon} Relayed message successfully")
                                logger.debug(f"Relayed message: {message[:100]}...")
                            except asyncio.TimeoutError:
                                cprint(
                                    "🏠 Relay send timeout (subscribers may be slow)",
                                    mode=CONSOLE.VERBOSE,
                                )
                                logger.debug("Relay send timeout (subscribers may be slow)")
                    except zmq.Again:
                        # No message available - continue to check shutdown
                        await asyncio.sleep(0.01)  # Brief sleep to prevent busy-waiting
                        continue
                    except asyncio.CancelledError:
                        # Task cancelled during recv operation - this is expected during shutdown
                        logger.debug("Relay recv cancelled during shutdown")
                        break
                    except zmq.ZMQError as e:
                        # Socket closed or other ZMQ error
                        logger.debug(f"ZMQ error in relay recv: {e}")
                        break

                except asyncio.CancelledError:
                    # Task cancelled in outer loop
                    break
                except Exception as e:
                    logger.debug(f"Broker relay error: {e}")
                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            pass  # Normal cancellation, suppress stack trace
        except Exception as e:
            if not self.shutdown_event.is_set():
                logger.error(f"Broker message relay error: {e}")

        # Close sockets when exiting to prevent ZMQ callback exceptions
        await self.socket_manager.close_discovery_broker()

    async def _boundary_monitor_wrapper(self, task_shutdown_event: asyncio.Event):
        """Wrapper for boundary monitoring that provides change callback."""

        async def boundary_change_callback():
            """Handle boundary changes by updating announcements and hierarchy."""
            # Propagate changes based on our role
            if self.is_discovery_broker:
                # We're the broker - update our own known_nodes entry with new boundaries
                self.hierarchy_manager.add_self_to_known_nodes(
                    address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
                    boundaries=self.boundary_manager.get_boundaries(),
                )
                # Rebuild hierarchy and announce to all nodes
                self.hierarchy_manager.rebuild_hierarchy_tree(is_broker=True)
                await self._send_broker_announcement()
                cprint("📡 Broker: Sent updated hierarchy with new boundaries")

                # Display updated hierarchy tree
                try:
                    hierarchy_data = await self.get_cached_hierarchy()
                    formatted_output = format_hierarchy_display_for_server(hierarchy_data)
                    cprint(formatted_output)
                except Exception as e:
                    logger.debug(f"Error displaying updated hierarchy: {e}")
            else:
                # We're a client - send our updated boundaries to the broker
                await self.send_announcement()
                cprint("📡 Client: Sent updated boundaries to broker")

        await self.boundary_manager.monitor_boundary_cache(
            task_shutdown_event=task_shutdown_event,
            shutdown_event=self.shutdown_event,
            boundary_change_callback=boundary_change_callback,
        )

    def get_hierarchy_tree(self, max_age_seconds: int = 10) -> Dict:
        """
        Get the current hierarchy tree, rebuilding if stale.

        Args:
            max_age_seconds: Maximum age before rebuilding (default 10s)

        Returns:
            Dictionary representing the current hierarchy tree
        """
        return self.hierarchy_manager.get_hierarchy_tree(max_age_seconds)

    def who_handles_path(self, target_path: str) -> Optional[Dict]:
        """
        Find which node should handle a given path.

        Args:
            target_path: Path to find the responsible node for

        Returns:
            Dictionary with node info that handles the path, or None
        """
        return self.hierarchy_manager.who_handles_path(target_path)

    async def get_cached_hierarchy(self, force_refresh: bool = False) -> Dict:
        """
        Get hierarchy tree using cache with smart expiration.

        Args:
            force_refresh: Force refresh from broker even if cache is valid

        Returns:
            Dictionary with hierarchy tree and metadata
        """
        return self.hierarchy_manager.get_cached_hierarchy(
            force_refresh=force_refresh, is_broker=self.is_discovery_broker
        )
