"""
Hierarchy Manager for P2P Network

Handles node hierarchy management, known nodes tracking, and hierarchy tree building.
Extracted from DiscoveryManager to isolate hierarchy management concerns.
"""

import time
from typing import Dict, List, Optional

from ....core.console_shared import CONSOLE, cprint
from ....core.filesystem.path_utils import expand_path_for_io
from ....utils.logging_config import get_logger
from ..models import NodeMode

logger = get_logger(__name__)


class HierarchyManager:
    """Manages node hierarchy, known nodes tracking, and hierarchy tree building."""

    def __init__(
        self, node_id: str, managed_paths: List[str], discovery_priority: int, node_mode=None
    ):
        """Initialize hierarchy manager."""
        self.node_id = node_id
        self.managed_paths = managed_paths
        self.discovery_priority = discovery_priority
        self.is_worker = node_mode == NodeMode.WORKER if node_mode else False
        self.is_monitor = node_mode == NodeMode.MONITOR if node_mode else False

        # Node tracking for join/leave detection
        self._known_nodes: Dict[str, Dict] = (
            {}
        )  # node_id -> {last_seen, address, managed_path, boundaries, info}

        # Hierarchy state management (for broker)
        self._hierarchy_tree: Dict = {}  # Built from _known_nodes boundaries
        self._hierarchy_last_updated: float = 0
        self._hierarchy_version: int = 0  # Incremented on changes for cache invalidation

        # Hierarchy cache (for all node types - monitors, workers, servers)
        self._hierarchy_cache = {"tree": {}, "version": 0, "last_updated": 0, "expires_at": 0}
        self.HIERARCHY_CACHE_TTL = 4  # 4 seconds cache TTL

        # Track last printed hierarchy version to avoid spam
        self._last_printed_hierarchy_version = -1

    def add_known_node(self, node_id: str, node_data: Dict) -> bool:
        """
        Add or update a known node.

        Args:
            node_id: The node identifier
            node_data: Node information dictionary

        Returns:
            True if this is a new node, False if updating existing
        """
        is_new_node = node_id not in self._known_nodes
        current_time = time.time()

        # Update complete node information
        self._known_nodes[node_id] = {
            "last_seen": current_time,
            "address": node_data.get("address", "Unknown"),
            "managed_paths": node_data.get("managed_paths", []),
            "boundaries": node_data.get("boundaries", {}),
            "discovery_priority": node_data.get("discovery_priority", 0),
            "info": node_data,
        }

        if is_new_node and self.is_monitor:
            cprint(f"📡 New node joined: {node_id}")

        return is_new_node

    def get_known_nodes(self) -> Dict[str, Dict]:
        """Get all known nodes."""
        return self._known_nodes.copy()

    def check_for_departed_nodes(self, node_timeout: float) -> List[str]:
        """
        Check for nodes that haven't been seen recently and mark them as departed.

        Args:
            node_timeout: Timeout in seconds for considering a node departed

        Returns:
            List of departed node IDs
        """
        current_time = time.time()
        departed_nodes = []

        for node_id, node_data in list(self._known_nodes.items()):
            last_seen = node_data.get("last_seen", 0)
            if current_time - last_seen > node_timeout:
                departed_nodes.append(node_id)
                del self._known_nodes[node_id]

        # Announce departed nodes
        for node_id in departed_nodes:
            if self.is_monitor:
                cprint(f"📡 Node left: {node_id} (timeout after {node_timeout}s)")

        return departed_nodes

    def rebuild_hierarchy_tree(self, is_broker: bool = True) -> None:
        """Rebuild the hierarchy tree from current _known_nodes data."""
        if not is_broker:
            return  # Only broker maintains hierarchy

        current_time = time.time()
        self._hierarchy_tree = {}

        cprint(f"🔧 REBUILDING HIERARCHY: Found {len(self._known_nodes)} known nodes")
        for node_id, node_data in self._known_nodes.items():
            cprint(
                f"  🧪 - {node_id}: priority={node_data.get('discovery_priority', 0)}, paths={node_data.get('managed_paths', [])}"
            )

        # Build hierarchy from all known nodes except priority 0 (temporary workers)
        for node_id, node_data in self._known_nodes.items():
            discovery_priority = node_data.get("discovery_priority", 0)

            # Only exclude priority 0 nodes (temporary workers)
            if discovery_priority <= 0:
                cprint(f"  ❌ Excluding {node_id} (priority={discovery_priority})")
                continue

            managed_paths = node_data.get("managed_paths", [])
            boundaries = node_data.get("boundaries", {})

            cprint(f"  🧪 Including {node_id}: managed_paths={managed_paths}")

            # Add each managed path as a root node
            for managed_path in managed_paths:
                if managed_path:
                    cprint(f"    🧪 📁 Adding path: {managed_path}")
                    # Get boundaries for this specific managed path
                    path_boundaries = boundaries.get(managed_path, [])

                    self._hierarchy_tree[managed_path] = {
                        "node_id": node_id,
                        "address": node_data.get("address", ""),
                        "managed_path": managed_path,
                        "boundaries": path_boundaries,
                        "discovery_priority": discovery_priority,
                        "has_manager": True,
                        "last_seen": node_data.get("last_seen", current_time),
                    }

        self._hierarchy_last_updated = current_time
        self._hierarchy_version += 1

        # Count total boundaries across all nodes
        total_boundaries = 0
        for path, node_info in self._hierarchy_tree.items():
            boundaries = node_info.get("boundaries", [])
            total_boundaries += len(boundaries)

        cprint(
            f"✅ HIERARCHY BUILT: {len(self._hierarchy_tree)} paths {total_boundaries} boundaries v{self._hierarchy_version}",
            mode=CONSOLE.VERBOSE,
        )
        for path, node_info in self._hierarchy_tree.items():
            cprint(
                f"  📁 {path} -> {node_info['node_id']} (priority={node_info['discovery_priority']})",
                mode=CONSOLE.VERBOSE,
            )

    def get_hierarchy_tree(self, max_age_seconds: int = 10) -> Dict:
        """
        Get the current hierarchy tree, rebuilding if stale.

        Args:
            max_age_seconds: Maximum age before rebuilding (default 10s)

        Returns:
            Dictionary representing the current hierarchy tree
        """
        current_time = time.time()

        # Rebuild if stale or empty
        if (
            current_time - self._hierarchy_last_updated
        ) > max_age_seconds or not self._hierarchy_tree:
            self.rebuild_hierarchy_tree()

        return {
            "tree": self._hierarchy_tree,
            "version": self._hierarchy_version,
            "last_updated": self._hierarchy_last_updated,
        }

    def who_handles_path(self, target_path: str) -> Optional[Dict]:
        """
        Find which node should handle a given path.

        Args:
            target_path: Path to find the responsible node for

        Returns:
            Dictionary with node info that handles the path, or None
        """
        best_match = None
        best_match_length = 0

        # Check all nodes in the hierarchy
        for managed_path, node_info in self._hierarchy_tree.items():
            # Check if target path is within this node's managed path
            if target_path.startswith(managed_path + "/") or target_path == managed_path:
                if len(managed_path) > best_match_length:
                    best_match = node_info
                    best_match_length = len(managed_path)

            # Also check boundaries within this node for more specific matches
            boundaries = node_info.get("boundaries", [])
            for boundary in boundaries:
                boundary_path = boundary.get("path", "")
                if boundary.get("has_manager", False):  # Only consider running managers
                    if target_path.startswith(boundary_path + "/") or target_path == boundary_path:
                        if len(boundary_path) > best_match_length:
                            best_match = {
                                "node_id": f"{node_info['node_id']}_boundary",
                                "managed_path": boundary_path,
                                "address": node_info["address"],
                                "boundary_info": boundary,
                            }
                            best_match_length = len(boundary_path)

        return best_match

    def get_hierarchy_state(self) -> Dict:
        """Get complete hierarchy state for transfer to new broker."""
        return {
            "known_nodes": self._known_nodes,
            "hierarchy_tree": self._hierarchy_tree,
            "hierarchy_version": self._hierarchy_version,
            "hierarchy_last_updated": self._hierarchy_last_updated,
        }

    def add_self_to_known_nodes(self, address: str, boundaries: Dict) -> None:
        """Add ourselves to the known_nodes registry with current timestamp."""
        current_time = time.time()
        cprint(
            f"🔧 SERVER ADDING SELF: node_id={self.node_id}, managed_paths={self.managed_paths}, priority={self.discovery_priority}"
        )
        self._known_nodes[self.node_id] = {
            "last_seen": current_time,
            "address": address,
            "managed_paths": self.managed_paths,
            "boundaries": boundaries,
            "discovery_priority": self.discovery_priority,
            "info": {
                "node_id": self.node_id,
                "address": address,
                "managed_paths": self.managed_paths,
                "boundaries": boundaries,
                "discovery_priority": self.discovery_priority,
            },
        }

    def inherit_hierarchy_state(
        self, hierarchy_state: Dict, address: str, boundaries: Dict
    ) -> None:
        """Inherit hierarchy state from previous broker."""
        self._known_nodes = hierarchy_state.get("known_nodes", {})
        self._hierarchy_tree = hierarchy_state.get("hierarchy_tree", {})
        self._hierarchy_version = hierarchy_state.get("hierarchy_version", 0)
        self._hierarchy_last_updated = hierarchy_state.get("hierarchy_last_updated", time.time())

        # Add/update ourselves in the inherited known_nodes with current timestamp
        self.add_self_to_known_nodes(address, boundaries)

        # Don't rebuild hierarchy yet - wait until we're actually the broker

        logger.info(
            f"Inherited hierarchy state with {len(self._known_nodes)} nodes, version {self._hierarchy_version}"
        )

    def finalize_broker_takeover(
        self, address: str, boundaries: Dict, is_broker: bool = True
    ) -> None:
        """Finalize broker takeover by inserting ourselves into the hierarchy tree."""
        if not is_broker:
            return  # Only broker maintains hierarchy

        cprint(f"🔧 FINALIZING BROKER TAKEOVER: {self.node_id} with paths {self.managed_paths}")

        current_time = time.time()

        # Add each of our managed paths to the hierarchy tree
        for managed_path in self.managed_paths:
            if managed_path:
                cprint(f"    📁 Adding our path: {managed_path}")
                # Get boundaries for this specific managed path
                path_boundaries = boundaries.get(managed_path, [])

                self._hierarchy_tree[managed_path] = {
                    "node_id": self.node_id,
                    "address": address,
                    "managed_path": managed_path,
                    "boundaries": path_boundaries,
                    "discovery_priority": self.discovery_priority,
                    "has_manager": True,
                    "last_seen": current_time,
                }

        self._hierarchy_last_updated = current_time
        self._hierarchy_version += 1

        cprint(
            f"✅ BROKER TAKEOVER FINALIZED: {len(self._hierarchy_tree)} paths in tree, version {self._hierarchy_version}"
        )

    def get_cached_hierarchy(self, force_refresh: bool = False, is_broker: bool = False) -> Dict:
        """
        Get hierarchy tree using cache with smart expiration.

        Args:
            force_refresh: Force refresh from broker even if cache is valid
            is_broker: Whether this node is the broker

        Returns:
            Dictionary with hierarchy tree and metadata
        """
        current_time = time.time()

        # Check if cache is valid and not forcing refresh
        expires_at = self._hierarchy_cache.get("expires_at", 0)
        if not force_refresh and current_time < expires_at and self._hierarchy_cache["tree"]:
            return self._hierarchy_cache

        # Cache expired or force refresh
        if not is_broker:
            # Clients should re-announce themselves to request fresh hierarchy
            # This will trigger a targeted broker announcement from the broker
            logger.debug("Hierarchy cache expired - clients should re-announce to refresh")
            # Return stale cache for now - client can re-announce if needed

        # If we are the broker, use our own data
        else:
            broker_hierarchy = self.get_hierarchy_tree()
            self._hierarchy_cache = {
                "tree": broker_hierarchy["tree"],
                "version": broker_hierarchy["version"],
                "last_updated": broker_hierarchy["last_updated"],
                "expires_at": current_time + self.HIERARCHY_CACHE_TTL,
            }

        return self._hierarchy_cache

    def update_hierarchy_cache_from_broker(self, hierarchy_data: Dict) -> None:
        """Update hierarchy cache from broker announcement."""
        current_time = time.time()
        if hierarchy_data:  # Only update if hierarchy data is present
            hierarchy_tree = hierarchy_data.get("hierarchy_tree", {})
            hierarchy_version = hierarchy_data.get("hierarchy_version", 0)
            hierarchy_last_updated = hierarchy_data.get("hierarchy_last_updated", current_time)

            self._hierarchy_cache = {
                "tree": hierarchy_tree,
                "version": hierarchy_version,
                "last_updated": hierarchy_last_updated,
                "expires_at": current_time + self.HIERARCHY_CACHE_TTL,
            }

            # Only print debug message when version changes
            if hierarchy_version != self._last_printed_hierarchy_version:
                # Count total boundaries
                total_boundaries = 0
                for path, node_info in hierarchy_tree.items():
                    boundaries = node_info.get("boundaries", [])
                    total_boundaries += len(boundaries)

                cprint(
                    f"📥 MONITOR RECEIVED HIERARCHY: {len(hierarchy_tree)} paths {total_boundaries} boundaries v{hierarchy_version}",
                    mode=CONSOLE.VERBOSE,
                )
                for path, node_info in hierarchy_tree.items():
                    cprint(
                        f"  📁 {path} -> {node_info.get('node_id', 'unknown')}",
                        mode=CONSOLE.VERBOSE,
                    )
                self._last_printed_hierarchy_version = hierarchy_version

            logger.debug(
                f"Updated hierarchy cache from broker announcement (version {hierarchy_version})"
            )
        else:
            print(f"🔍 DEBUG: No hierarchy data provided to update_hierarchy_cache_from_broker")

    async def wait_for_hierarchy(
        self, timeout_seconds: float = 4.0, poll_interval: float = 0.1
    ) -> bool:
        """
        Wait for hierarchy cache to be populated from broker.

        Args:
            timeout_seconds: Maximum time to wait (default 4 seconds)
            poll_interval: How often to check (default 100ms)

        Returns:
            True if hierarchy received, False if timeout
        """
        import asyncio

        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            # Check if hierarchy cache has any paths
            hierarchy_tree = self._hierarchy_cache.get("tree", {})
            if len(hierarchy_tree) > 0:
                logger.debug(
                    f"Hierarchy received with {len(hierarchy_tree)} paths after {time.time() - start_time:.2f}s"
                )
                return True

            # Wait before next check
            await asyncio.sleep(poll_interval)

        logger.debug(f"Timeout waiting for hierarchy after {timeout_seconds}s")
        return False

    def is_top_of_hierarchy(self, path: str) -> bool:
        """Check if this node is at the top of the hierarchy for the given path."""
        try:
            # Normalize the input path
            normalized_path = str(expand_path_for_io(path))

            # Get current hierarchy
            hierarchy = self.get_cached_hierarchy()
            if not hierarchy or not hierarchy.get("tree"):
                # No hierarchy info available - workers default to False, servers default to True
                return not self.is_worker

            # Check if any node in hierarchy manages a parent path of our target
            for hierarchy_path, node_info in hierarchy["tree"].items():
                hierarchy_normalized = str(expand_path_for_io(hierarchy_path))

                # If there's a parent path in hierarchy that we don't manage
                if normalized_path.startswith(
                    hierarchy_normalized + "/"
                ) and hierarchy_normalized not in [
                    str(expand_path_for_io(mp)) for mp in self.managed_paths
                ]:
                    logger.debug(
                        f"Path {normalized_path} is under hierarchy root {hierarchy_normalized}"
                    )
                    return False

            # Check if we manage this path or a parent of it
            for managed_path in self.managed_paths:
                managed_normalized = str(expand_path_for_io(managed_path))
                if normalized_path.startswith(managed_normalized) or managed_normalized.startswith(
                    normalized_path
                ):
                    logger.debug(f"We manage path hierarchy for {normalized_path}")
                    return True

            logger.debug(f"Path {normalized_path} not in our managed hierarchy")
            return False

        except Exception as e:
            logger.warning(f"Error checking hierarchy position for {path}: {e}")
            return True  # Default to allowing worker spawning if we can't determine

    def set_node_id(self, node_id: str) -> None:
        """Set the node ID for this hierarchy manager."""
        self.node_id = node_id
