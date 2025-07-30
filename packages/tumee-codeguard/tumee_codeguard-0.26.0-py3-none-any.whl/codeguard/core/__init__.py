"""
Core functionality for CodeGuard.

This package contains the essential components for the CodeGuard system including
validation, ACL management, comparison engines, and centralized caching.
"""

# Caching components
from .caching.backends import (
    DiskCacheBackend,
    RedisCacheBackend,
    create_cache_backends,
)
from .caching.centralized import (
    CACHE_POLICIES,
    CacheEntry,
    CacheMetadata,
    CachePolicy,
    CachePriority,
    CacheRoutingStrategy,
    CacheTier,
    CentralizedCacheManager,
    InvalidationStrategy,
)

# Cache manager functions
from .caching.manager import get_cache_manager, reset_cache_manager, set_cache_manager
from .factories import create_cache_manager_from_env
from .filesystem.watcher import (
    FileWatcherWithFallback,
    PollingHandle,
    WatchHandle,
    watch_config_file,
    watch_filtering_files,
    watch_template_directory,
)
from .parsing.comparison_engine import ComparisonEngine

# Existing core functionality
from .validation.directory_guard import DirectoryGuard
from .validation.validator import CodeGuardValidator

__all__ = [
    # Existing core functionality
    "CodeGuardValidator",
    "ComparisonEngine",
    "DirectoryGuard",
    # Cache management
    "CentralizedCacheManager",
    "CacheEntry",
    "CacheMetadata",
    "CachePolicy",
    "CacheRoutingStrategy",
    "CacheTier",
    "InvalidationStrategy",
    "CachePriority",
    "CACHE_POLICIES",
    # Backends
    "DiskCacheBackend",
    "RedisCacheBackend",
    "create_cache_backends",
    "create_cache_manager_from_env",
    # File watching
    "FileWatcherWithFallback",
    "WatchHandle",
    "PollingHandle",
    "watch_config_file",
    "watch_template_directory",
    "watch_filtering_files",
    # Global instances
    "get_cache_manager",
    "set_cache_manager",
    "reset_cache_manager",
]
