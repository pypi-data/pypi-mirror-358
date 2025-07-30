"""
Topology Manager for P2P Network

Handles hierarchy management, role determination, and network reorganization.
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional

from ....core.filesystem.path_utils import expand_path_for_io
from ....utils.logging_config import get_logger
from ..config import P2PConfig
from ..exceptions import PathConflictError
from ..models import (
    NewParentNotification,
    NodeInfo,
    PathQueryResponse,
    RegistrationRequest,
)
from .health_monitor import HealthMonitor
from .interfaces import IBoundaryProvider, IHierarchyManager, IMessageHandler, ITopologyManager
from .socket_manager import SocketManager

logger = get_logger(__name__)


class TopologyManager(ITopologyManager):
    """Manages P2P network topology and hierarchy."""

    def __init__(
        self,
        config: P2PConfig,
        socket_manager: "SocketManager",
        health_monitor: "HealthMonitor",
        node_id: str,
        managed_paths: List[str],
        discovery_priority: int = 0,
    ):
        """Initialize topology manager."""
        self.config = config
        self.socket_manager = socket_manager
        self.health_monitor = health_monitor
        self.node_id = node_id
        self.managed_paths = managed_paths
        self.discovery_priority = discovery_priority

        # Will be set by core manager
        self.message_handler: Optional[IMessageHandler] = None
        self.boundary_provider: Optional[IBoundaryProvider] = None
        self.hierarchy_manager: Optional["IHierarchyManager"] = None

        # Hierarchy tracking
        self.parent: Optional[NodeInfo] = None
        self.children: Dict[str, NodeInfo] = {}  # child_path -> NodeInfo

    def set_message_handler(self, message_handler: IMessageHandler):
        """Set message handler reference."""
        self.message_handler = message_handler

    def set_boundary_provider(self, boundary_provider: IBoundaryProvider):
        """Set boundary provider reference."""
        self.boundary_provider = boundary_provider

    def set_hierarchy_manager(self, hierarchy_manager: "IHierarchyManager"):
        """Set hierarchy manager reference."""
        self.hierarchy_manager = hierarchy_manager

    def _get_cached_boundaries(self) -> Dict[str, List[Dict]]:
        """Get cached boundaries from boundary provider or return empty dict."""
        if self.boundary_provider:
            return self.boundary_provider.get_boundaries()
        # Fallback to empty boundaries if no provider is set
        return {path: [] for path in self.managed_paths}

    def register_child(self, request: RegistrationRequest):
        """Register a child node."""
        for path in request.paths:
            self.children[path] = NodeInfo(
                node_id=request.node_id,
                address=request.address,
                managed_paths=request.paths,
                boundaries=request.boundaries,
                timestamp=request.timestamp or time.time(),
            )
        logger.info(
            f"Child {request.node_id} registered for paths: {request.paths} with {len(request.boundaries)} boundary sets"
        )

    async def handle_new_parent(self, notification: NewParentNotification):
        """Handle new parent notification."""
        self.parent = NodeInfo(
            node_id=notification.parent_node_id,
            address=notification.parent_address,
            managed_paths=[notification.parent_path],
            boundaries={},
            timestamp=notification.timestamp or time.time(),
        )

        # Update health monitor
        self.health_monitor.set_parent(self.parent)

        # Register with new parent
        await self._register_with_parent(self.parent)

    async def process_topology_changes(self):
        """Process network topology changes reactively when new nodes are discovered."""
        try:
            # Check for conflicts first
            conflicts = self._check_for_conflicts()
            if conflicts:
                await self._handle_conflicts(conflicts)
                return

            # Determine our role for each managed path and apply changes if needed
            for path in self.managed_paths:
                role = self._determine_role_for_path(path)
                await self._apply_role(path, role)

        except Exception as e:
            logger.debug(f"Topology processing error: {e}")

    async def handle_path_query(self, path: str) -> Dict:
        """Handle a query about who owns a path."""

        # Find the root owner
        owner = self.find_owner(path)

        if not owner:
            return PathQueryResponse(error="No owner found").model_dump()

        result = PathQueryResponse(
            root_owner=owner.node_id,
            root_address=owner.address,
        )

        # If we're the owner, check for more specific handlers
        if owner.node_id == self.node_id:
            # Find which of our paths handles this
            for managed_path in self.managed_paths:
                if path.startswith(managed_path + "/") or path == managed_path:
                    result.root_path = managed_path
                    break

            # Check for more specific children
            most_specific = None
            longest_match = 0

            for child_path, child_info in self.children.items():
                if path.startswith(child_path + "/") or path == child_path:
                    if len(child_path) > longest_match:
                        most_specific = {
                            "node_id": child_info.node_id,
                            "address": child_info.address,
                            "path": child_path,
                        }
                        longest_match = len(child_path)

            if most_specific:
                result.specific_handler = most_specific

            # Check if we should start a delegate
            delegate = self._check_for_delegate(path)
            if delegate:
                result.should_start_delegate = delegate

        return result.model_dump()

    def _path_is_under(self, query_path: str, managed_path: str) -> bool:
        """Check if query_path is under managed_path (both should be normalized absolute paths)."""
        # Ensure both paths end with / for proper comparison (except for exact match)
        if query_path == managed_path:
            return True

        # Add trailing slash to managed path if not present
        managed_with_slash = managed_path.rstrip("/") + "/"
        return query_path.startswith(managed_with_slash)

    def find_owner(self, query_path: str) -> Optional[NodeInfo]:
        """Find the highest-level owner of a path."""

        # Normalize query path to absolute format for comparison
        normalized_query = expand_path_for_io(query_path)
        logger.debug(f"Finding owner for path: {query_path} (normalized: {normalized_query})")

        candidates = []

        # Add our own paths (only if priority > 0, priority 0 workers never claim ownership)
        if self.discovery_priority > 0:
            for managed_path in self.managed_paths:
                # Normalize managed path for comparison
                normalized_managed = expand_path_for_io(managed_path)
                logger.debug(
                    f"Checking self-managed path: {managed_path} (normalized: {normalized_managed})"
                )

                if self._path_is_under(normalized_query, normalized_managed):
                    logger.debug(
                        f"Found self-ownership: {normalized_query} under {normalized_managed}"
                    )
                    candidates.append(
                        (
                            managed_path,
                            NodeInfo(
                                node_id=self.node_id,
                                address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
                                managed_paths=self.managed_paths,
                                boundaries=self._get_cached_boundaries(),
                                timestamp=time.time(),
                            ),
                        )
                    )
        else:
            logger.debug(
                f"Priority 0 worker - skipping self-ownership check for {normalized_query}"
            )

        # Check for ownership based on priority:
        # - Priority > 0 (servers): Use own registry
        # - Priority 0 (workers): Use hierarchy cache from broker
        if self.discovery_priority > 0:
            # Servers check their own registry
            for registry_path, info in self.health_monitor.registry.items():
                # Normalize registry path for comparison
                normalized_registry = expand_path_for_io(registry_path)
                logger.debug(
                    f"Checking registry path: {registry_path} (normalized: {normalized_registry})"
                )

                if self._path_is_under(normalized_query, normalized_registry):
                    logger.debug(
                        f"Found registry ownership: {normalized_query} under {normalized_registry}"
                    )
                    candidates.append((registry_path, info))
        else:
            # Priority 0 workers check hierarchy cache from broker
            if self.hierarchy_manager:
                hierarchy_cache = self.hierarchy_manager.get_cached_hierarchy(is_broker=False)
                hierarchy_tree = hierarchy_cache.get("tree", {})
                logger.debug(
                    f"Priority 0 worker checking hierarchy cache with {len(hierarchy_tree)} paths"
                )

                for cache_path, cache_info in hierarchy_tree.items():
                    # Normalize cache path for comparison
                    normalized_cache = expand_path_for_io(cache_path)
                    logger.debug(
                        f"Checking cached path: {cache_path} (normalized: {normalized_cache})"
                    )

                    if self._path_is_under(normalized_query, normalized_cache):
                        logger.debug(
                            f"Found cached ownership: {normalized_query} under {normalized_cache}"
                        )
                        # Convert cache info to NodeInfo format
                        from ..models import NodeInfo

                        node_info = NodeInfo(
                            node_id=cache_info.get("node_id", ""),
                            address=cache_info.get("address", ""),
                            managed_paths=[cache_path],
                            boundaries={cache_path: cache_info.get("boundaries", [])},
                            timestamp=cache_info.get("last_seen", time.time()),
                        )
                        candidates.append((cache_path, node_info))

        if not candidates:
            return None

        # Return the highest level (shortest path)
        candidates.sort(key=lambda x: len(x[0]))
        return candidates[0][1]

    def _check_for_conflicts(self) -> List[Dict]:
        """Check if any of our paths conflict with existing registrations."""
        conflicts = []

        for our_path in self.managed_paths:
            if our_path in self.health_monitor.registry:
                existing = self.health_monitor.registry[our_path]
                conflicts.append(
                    {
                        "path": our_path,
                        "existing_node": existing.node_id,
                        "existing_address": existing.address,
                    }
                )

        return conflicts

    async def _handle_conflicts(self, conflicts: List[Dict]):
        """Handle path conflicts by informing user and exiting."""
        logger.error("Path conflict(s) detected!")

        for conflict in conflicts:
            logger.error(
                f"Path {conflict['path']} already managed by "
                f"{conflict['existing_node']} at {conflict['existing_address']}"
            )

        if self.config.force_registration:
            logger.warning("Force flag set, continuing despite conflicts!")
            return

        logger.error("Cannot register paths due to conflicts. Use --force to override.")
        raise PathConflictError(
            conflicts[0]["path"], conflicts[0]["existing_node"], conflicts[0]["existing_address"]
        )

    def _determine_role_for_path(self, our_path: str) -> Dict:
        """Determine if we're a root, child, or need to cause reorganization."""
        role = {"path": our_path, "type": "root", "parent": None, "new_children": []}

        # Check all known paths
        for known_path, info in self.health_monitor.registry.items():
            if known_path == our_path:
                continue

            if our_path.startswith(known_path + "/"):
                # We're under this agent
                if not role["parent"] or len(known_path) > len(role["parent"].managed_paths[0]):
                    role["type"] = "child"
                    role["parent"] = info

            elif known_path.startswith(our_path + "/"):
                # This agent should be our child
                role["type"] = "new_parent"
                role["new_children"].append(info)

        return role

    async def _apply_role(self, path: str, role: Dict):
        """Apply the determined role, triggering reorganization if needed."""
        logger.info(f"Path {path}: role = {role['type']}")

        if role["type"] == "child":
            await self._register_with_parent(role["parent"])

        elif role["type"] == "new_parent":
            # We're inserting ourselves in the middle
            for child_info in role["new_children"]:
                await self._notify_new_parent(child_info, path)

            # Register with our parent if we have one
            parent_role = self._determine_role_for_path(path)
            if parent_role["parent"]:
                await self._register_with_parent(parent_role["parent"])

        else:  # root
            logger.info(f"Node {self.node_id} is root for {path}")

    async def _register_with_parent(self, parent_info: NodeInfo):
        """Register ourselves as a child of the given parent."""
        logger.info(f"Registering with parent {parent_info.node_id}")

        self.parent = parent_info
        self.health_monitor.set_parent(parent_info)

        message = RegistrationRequest(
            node_id=self.node_id,
            address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
            paths=self.managed_paths,
        )

        if self.message_handler:
            await self.message_handler.send_to_node(parent_info.address, message.model_dump())

    async def _notify_new_parent(self, child_info: NodeInfo, our_path: str):
        """Notify a child that we're their new parent."""
        message = NewParentNotification(
            node_id=self.node_id,
            parent_node_id=self.node_id,
            parent_address=f"{self.socket_manager.get_local_ip()}:{self.socket_manager.port}",
            parent_path=our_path,
        )

        if self.message_handler:
            await self.message_handler.send_to_node(child_info.address, message.model_dump())

    def _check_for_delegate(self, query_path_str: str) -> Optional[str]:
        """Check if a path should have a delegate."""
        if query_path_str is None:
            return None

        query_path = Path(query_path_str)
        # Only check paths under our management
        managing_path = None
        for path in self.managed_paths:
            if str(query_path).startswith(path + "/") or str(query_path) == path:
                managing_path = Path(path)
                break

        if not managing_path:
            return None

        # Walk from query path up to our managed path
        current = query_path
        while current >= managing_path:
            delegate_file = current / self.config.delegate_file_name
            if delegate_file.exists():
                # Check if we already have a delegate for this
                if str(current) not in self.children:
                    return str(current)

            if current == managing_path:
                break
            current = current.parent

        return None

    def get_topology_info(self) -> Dict:
        """Get current topology information."""
        return {
            "node_id": self.node_id,
            "managed_paths": self.managed_paths,
            "parent": self.parent.node_id if self.parent else None,
            "children_count": len(self.children),
            "children": {path: info.node_id for path, info in self.children.items()},
        }
