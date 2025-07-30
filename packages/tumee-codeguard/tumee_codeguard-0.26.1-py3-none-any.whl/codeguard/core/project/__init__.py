"""
Project management utilities for CodeGuard.

This module provides core services for project boundary discovery,
repository detection, and AI-OWNER management.
"""

from .boundary_discovery import (
    BoundaryDiscoveryResult,
    BoundaryInfo,
    discover_managed_boundaries,
    get_boundary_display_info,
    get_project_hierarchy_display,
)

__all__ = [
    "BoundaryDiscoveryResult",
    "BoundaryInfo",
    "discover_managed_boundaries",
    "get_boundary_display_info",
    "get_project_hierarchy_display",
]
