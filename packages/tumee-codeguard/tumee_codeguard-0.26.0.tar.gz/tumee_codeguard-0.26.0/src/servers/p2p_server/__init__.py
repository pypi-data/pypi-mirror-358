"""
P2P Network Manager for CodeGuard

This module implements a hierarchical peer-to-peer network where CodeGuard instances can:
- Dynamically discover their place in a file system hierarchy
- Reorganize when new parent/child nodes join
- Query for path ownership (always returns highest-level owner)
- Support delegated paths and on-demand child spawning
- Prevent conflicts when multiple instances try to manage the same path

The P2P system integrates seamlessly with CodeGuard's existing architecture,
using the same logging, error handling, and configuration patterns.
"""

from .config import P2PConfig
from .exceptions import NetworkError, P2PError, PathConflictError
from .models import (
    DiscoveryAnnouncement,
    NodeInfo,
    P2PMessage,
    PathQuery,
    RegistrationRequest,
)
from .network_manager import HierarchicalNetworkManager

__all__ = [
    "HierarchicalNetworkManager",
    "P2PConfig",
    "P2PError",
    "PathConflictError",
    "NetworkError",
    "P2PMessage",
    "NodeInfo",
    "PathQuery",
    "RegistrationRequest",
    "DiscoveryAnnouncement",
]
