"""
Protocol Interfaces for P2P Network Manager Components

These interfaces break circular dependencies between network manager components
by defining contracts without requiring direct imports of concrete classes.
"""

from typing import Dict, List, Optional, Protocol

from ..models import NewParentNotification, NodeInfo, RegistrationRequest


class IMessageHandler(Protocol):
    """Interface for MessageHandler functionality needed by other components."""

    async def send_to_node(self, address: str, message: Dict) -> Optional[Dict]:
        """Send a message to a specific node and wait for response."""
        ...

    def set_topology_manager(self, topology_manager: "ITopologyManager") -> None:
        """Set topology manager reference."""
        ...

    def set_ai_ownership_manager(self, ai_ownership_manager) -> None:
        """Set AI ownership manager reference."""
        ...


class ITopologyManager(Protocol):
    """Interface for TopologyManager functionality needed by other components."""

    def register_child(self, request: RegistrationRequest) -> None:
        """Register a child node."""
        ...

    async def handle_new_parent(self, notification: NewParentNotification) -> None:
        """Handle new parent notification."""
        ...

    async def handle_path_query(self, path: str) -> Dict:
        """Handle a query about who owns a path."""
        ...

    def find_owner(self, query_path: str) -> Optional[NodeInfo]:
        """Find the highest-level owner of a path."""
        ...

    def set_message_handler(self, message_handler: "IMessageHandler") -> None:
        """Set message handler reference."""
        ...

    parent: Optional[NodeInfo]
    children: Dict[str, NodeInfo]


class IBoundaryProvider(Protocol):
    """Interface for boundary discovery functionality needed by other components."""

    def get_boundaries(self) -> Dict[str, List[Dict]]:
        """Get discovered boundaries keyed by managed path."""
        ...


class IBoundaryManager(Protocol):
    """Interface for boundary management functionality."""

    async def discover_boundaries(self) -> Dict[str, List[Dict]]:
        """Discover boundaries for all managed paths."""
        ...

    def get_boundaries(self) -> Dict[str, List[Dict]]:
        """Get discovered boundaries keyed by managed path."""
        ...

    def invalidate_boundary_cache(self) -> None:
        """Invalidate boundary cache for this node."""
        ...

    async def monitor_boundary_cache(
        self,
        task_shutdown_event,
        shutdown_event,
        boundary_change_callback=None,
    ) -> None:
        """Monitor boundary cache for invalidation and trigger rediscovery."""
        ...


class IHierarchyManager(Protocol):
    """Interface for hierarchy management functionality."""

    def add_known_node(self, node_id: str, node_data: Dict) -> bool:
        """Add or update a known node. Returns True if new node."""
        ...

    def get_known_nodes(self) -> Dict[str, Dict]:
        """Get all known nodes."""
        ...

    def check_for_departed_nodes(self, node_timeout: float) -> List[str]:
        """Check for departed nodes and return list of departed node IDs."""
        ...

    def rebuild_hierarchy_tree(self, is_broker: bool = True) -> None:
        """Rebuild the hierarchy tree from current known nodes."""
        ...

    def get_hierarchy_tree(self, max_age_seconds: int = 10) -> Dict:
        """Get the current hierarchy tree, rebuilding if stale."""
        ...

    def who_handles_path(self, target_path: str) -> Optional[Dict]:
        """Find which node should handle a given path."""
        ...

    def is_top_of_hierarchy(self, path: str) -> bool:
        """Check if this node is at the top of the hierarchy for the given path."""
        ...

    def get_hierarchy_state(self) -> Dict:
        """Get complete hierarchy state for transfer to new broker."""
        ...

    def add_self_to_known_nodes(self, address: str, boundaries: Dict) -> None:
        """Add ourselves to the known_nodes registry."""
        ...

    def inherit_hierarchy_state(
        self, hierarchy_state: Dict, address: str, boundaries: Dict
    ) -> None:
        """Inherit hierarchy state from previous broker."""
        ...

    def finalize_broker_takeover(
        self, address: str, boundaries: Dict, is_broker: bool = True
    ) -> None:
        """Finalize broker takeover by inserting ourselves into hierarchy tree."""
        ...

    def get_cached_hierarchy(self, force_refresh: bool = False, is_broker: bool = False) -> Dict:
        """Get hierarchy tree using cache with smart expiration."""
        ...

    def update_hierarchy_cache_from_broker(self, hierarchy_data: Dict) -> None:
        """Update hierarchy cache from broker announcement."""
        ...

    def set_node_id(self, node_id: str) -> None:
        """Set the node ID for this hierarchy manager."""
        ...
