"""
Configuration management for P2P network.
"""

import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from ...core.config import YAMLConfigService
from .exceptions import ConfigurationError


class P2PConfig(BaseModel):
    """P2P network configuration."""

    # Network settings
    discovery_port: int = Field(default=10998, description="UDP port for discovery broadcasts")
    discovery_host: str = Field(
        default="127.0.0.1", description="Host for discovery service connection"
    )
    broadcast_interval: int = Field(default=1, description="Seconds between broadcasts")
    health_check_interval: int = Field(default=10, description="Seconds between health checks")
    node_timeout: int = Field(default=10, description="Seconds before considering a node dead")
    command_timeout: int = Field(
        default=300, description="Seconds before timing out command execution"
    )

    # Worker settings
    worker_linger_time: int = Field(
        default=300, description="Seconds workers stay alive after completing commands"
    )
    worker_max_total: int = Field(
        default=50, description="Maximum total workers across all boundaries per server"
    )
    worker_startup_timeout: int = Field(
        default=30, description="Seconds to wait for worker startup"
    )

    # Server settings
    bind_host: str = Field(default="0.0.0.0", description="Host to bind ZMQ server")
    port_range_start: int = Field(default=11000, description="Start of port range for ZMQ server")
    port_range_end: int = Field(default=13999, description="End of port range for ZMQ server")

    # Behavior settings
    force_registration: bool = Field(
        default=False, description="Force registration despite conflicts"
    )
    delegate_file_name: str = Field(
        default=".codeguard-delegate", description="Name of delegate marker file"
    )

    # Paths
    managed_paths: List[str] = Field(default_factory=list, description="Paths this node manages")

    # Boundary discovery settings
    boundary_cache_enabled: bool = Field(
        default=True, description="Enable boundary caching for quick startup"
    )
    boundary_cache_dir: str = Field(
        default="~/.codeguard/cache/boundaries",
        description="Directory to store boundary cache files",
    )
    boundary_watch_enabled: bool = Field(
        default=True, description="Enable real-time boundary file watching"
    )
    boundary_debounce_interval: int = Field(
        default=30, description="Seconds to debounce boundary change events"
    )
    boundary_watch_patterns: List[str] = Field(
        default_factory=lambda: ["**/ai-owner", "**/.ai-owner", "**/.git", "**/.hg", "**/.svn"],
        description="File patterns to watch for boundary changes",
    )
    quick_root_scan_interval: int = Field(
        default=30, description="Seconds between quick root directory scans"
    )
    full_background_scan_interval: int = Field(
        default=300, description="Seconds between full background boundary scans"
    )
    boundary_cache_max_age: int = Field(
        default=3600, description="Maximum age of boundary cache in seconds"
    )

    def validate_paths(self) -> None:
        """Validate that managed paths exist and are accessible."""
        for path_str in self.managed_paths:
            # Expand path for validation (I/O operation) - handles both ~username/ and ~ formats
            expanded_path = Path(path_str).expanduser().resolve()
            if not expanded_path.exists():
                raise ConfigurationError(
                    f"Managed path does not exist: {path_str} (expanded: {expanded_path})"
                )
            if not expanded_path.is_dir():
                raise ConfigurationError(
                    f"Managed path is not a directory: {path_str} (expanded: {expanded_path})"
                )
            if not os.access(expanded_path, os.R_OK):
                raise ConfigurationError(
                    f"No read access to managed path: {path_str} (expanded: {expanded_path})"
                )


def get_p2p_service() -> YAMLConfigService[P2PConfig]:
    """Get the configuration service for P2P."""
    return YAMLConfigService("p2p", P2PConfig, "p2p_defaults.yaml")
