"""
Cache factory for creating cache manager instances.

This module provides centralized cache creation logic to avoid circular imports
between caching and other layers.
"""

import argparse
import logging
import os
import urllib.parse
from typing import Dict

from ..caching.centralized import (
    CACHE_POLICIES,
    CacheRoutingStrategy,
    CentralizedCacheManager,
)
from ..filesystem.watcher import FileWatcherWithFallback
from .filesystem import create_filesystem_access_from_args

logger = logging.getLogger(__name__)


def create_cache_manager_from_env():
    """
    Create a cache manager from environment variables.

    Environment variables:
    - CODEGUARD_CACHE_BACKEND: Comma-separated list of backends (memory,disk,redis)
    - CODEGUARD_CACHE_DIR: Directory for disk cache
    - CODEGUARD_CACHE_MEMORY_LIMIT: Memory limit in MB
    - CODEGUARD_CACHE_DISK_LIMIT: Disk limit in bytes
    - CODEGUARD_CACHE_COMPRESS: Compression type for disk cache (none/lz4/gzip, default: lz4)
    - CODEGUARD_REDIS_URL: Redis connection URL
    """
    # Import here to avoid circular dependency
    from ..caching.backends import create_cache_backends

    # Parse backend configuration
    backend_list = os.getenv("CODEGUARD_CACHE_BACKEND", "memory,disk").split(",")
    backend_list = [b.strip().lower() for b in backend_list]

    config = {}

    # Memory configuration
    if "memory" in backend_list:
        config["memory"] = {"max_memory_mb": int(os.getenv("CODEGUARD_CACHE_MEMORY_LIMIT", "256"))}

    # Disk configuration
    if "disk" in backend_list:
        config["disk"] = {
            "cache_dir": os.getenv("CODEGUARD_CACHE_DIR", ".codeguard/cache/metadata"),
            "size_limit": int(os.getenv("CODEGUARD_CACHE_DISK_LIMIT", str(1024 * 1024 * 1024))),
            "compression_type": os.getenv("CODEGUARD_CACHE_COMPRESS", "lz4").lower(),
        }

    # Redis configuration
    if "redis" in backend_list:
        redis_url = os.getenv("CODEGUARD_REDIS_URL", "redis://localhost:6379/0")

        # Parse Redis URL
        parsed = urllib.parse.urlparse(redis_url)

        config["redis"] = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "password": parsed.password,
            "db": int(parsed.path[1:]) if parsed.path and len(parsed.path) > 1 else 0,
        }

    # Create backends
    backends = create_cache_backends(config)

    # Create file watcher with filesystem access
    filesystem_access = create_filesystem_access_from_args(argparse.Namespace())

    file_watcher = FileWatcherWithFallback(
        fallback_interval=float(os.getenv("CODEGUARD_CACHE_POLL_INTERVAL", "1.0")),
        filesystem_access=filesystem_access,
    )

    # Create cache manager
    cache_manager = CentralizedCacheManager(
        backends=backends,
        routing_strategy=CacheRoutingStrategy(),
        cache_policies=CACHE_POLICIES,
        file_watcher=file_watcher,
    )

    logger.info(f"Created cache manager with backends: {list(backends.keys())}")
    return cache_manager
