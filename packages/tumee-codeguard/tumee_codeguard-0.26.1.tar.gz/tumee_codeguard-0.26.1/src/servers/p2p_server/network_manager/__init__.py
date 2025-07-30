"""
Network Manager Module

This module contains the refactored hierarchical network manager split into specialized components.
"""

from .core import HierarchicalNetworkManager

# Export the main class for backward compatibility
__all__ = ["HierarchicalNetworkManager"]
