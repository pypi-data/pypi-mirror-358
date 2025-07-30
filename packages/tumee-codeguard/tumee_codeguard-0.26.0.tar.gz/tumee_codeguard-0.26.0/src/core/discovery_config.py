"""
Discovery configuration singleton - NO IMPORTS from other project modules allowed.

This module provides a thread-safe singleton for managing discovery parameters
like paths and max_depth to avoid passing them through every function signature.
"""

import threading
from pathlib import Path
from typing import List, Optional, Union


class DiscoveryConfig:
    """Thread-safe singleton for managing discovery configuration."""

    _instance: Optional["DiscoveryConfig"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "DiscoveryConfig":
        """Ensure only one instance exists (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the singleton (only once)."""
        if not getattr(self, "_initialized", False):
            self._max_depth: Optional[int] = None
            self._managed_paths: List[Path] = []
            self._config_lock = threading.Lock()
            self._initialized = True

    def set_max_depth(self, max_depth: Optional[int]) -> None:
        """Set the global max depth for discovery operations."""
        with self._config_lock:
            self._max_depth = max_depth

    def get_max_depth(self) -> Optional[int]:
        """Get the current max depth setting."""
        with self._config_lock:
            return self._max_depth

    def set_managed_paths(self, paths: List[Union[str, Path]]) -> None:
        """Set the list of managed paths."""
        with self._config_lock:
            self._managed_paths = [Path(p) for p in paths]

    def get_managed_paths(self) -> List[Path]:
        """Get the current list of managed paths."""
        with self._config_lock:
            return self._managed_paths.copy()

    def add_managed_path(self, path: Union[str, Path]) -> None:
        """Add a single managed path."""
        with self._config_lock:
            path_obj = Path(path)
            if path_obj not in self._managed_paths:
                self._managed_paths.append(path_obj)

    def clear_managed_paths(self) -> None:
        """Clear all managed paths."""
        with self._config_lock:
            self._managed_paths.clear()

    def update_from_cli(
        self, max_depth: Optional[int] = None, paths: Optional[List[Union[str, Path]]] = None
    ) -> None:
        """Update configuration from CLI arguments."""
        with self._config_lock:
            if max_depth is not None:
                self._max_depth = max_depth
            if paths is not None:
                self._managed_paths = [Path(p) for p in paths]


# Global instance for easy access
discovery_config = DiscoveryConfig()


def set_discovery_config_from_cli(
    max_depth: Optional[int] = None, paths: Optional[List[Union[str, Path]]] = None
) -> None:
    """Set discovery configuration from CLI arguments."""
    discovery_config.update_from_cli(max_depth=max_depth, paths=paths)


def get_discovery_max_depth() -> Optional[int]:
    """Get the global max depth setting."""
    return discovery_config.get_max_depth()


def get_discovery_managed_paths() -> List[Path]:
    """Get the global managed paths."""
    return discovery_config.get_managed_paths()
