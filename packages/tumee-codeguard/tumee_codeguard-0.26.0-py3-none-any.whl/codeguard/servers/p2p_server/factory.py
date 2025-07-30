"""
Network Manager Factory

Factory implementation for creating network manager instances without circular imports.
Follows dependency inversion principle by depending only on interfaces.
"""

from typing import Any, List

from ...core.interfaces import IFileSystemAccess, INetworkManager, INetworkManagerFactory
from .models import NodeMode
from .network_manager import HierarchicalNetworkManager


class NetworkManagerFactory(INetworkManagerFactory):
    """Factory for creating network manager instances."""

    def create_network_manager(
        self,
        config: Any,
        managed_paths: List[str],
        shutdown_event: Any,
        filesystem_access: IFileSystemAccess,
    ) -> INetworkManager:
        """Create a network manager instance for workers (priority 0)."""
        # Workers have priority 0 as they come and go quickly
        return HierarchicalNetworkManager(
            config,
            managed_paths,
            shutdown_event,
            discovery_priority=0,
            filesystem_access=filesystem_access,
            node_mode=NodeMode.WORKER,  # Factory creates worker nodes
        )
