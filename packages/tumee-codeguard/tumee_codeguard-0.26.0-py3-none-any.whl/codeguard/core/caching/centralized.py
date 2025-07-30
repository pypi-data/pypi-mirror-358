"""
Centralized file caching system for CodeGuard.

This module provides a unified caching interface that consolidates all file reading
operations across the codebase with intelligent invalidation, tiered storage,
and data classification to ensure appropriate cache tier usage.
"""

import asyncio
import fnmatch
import hashlib
import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from ...utils.hash_calculator import HashCalculator
from ..interfaces import (
    CachePolicy,
    CachePriority,
    CacheTier,
    ICacheManager,
    InvalidationStrategy,
)

logger = logging.getLogger(__name__)


@dataclass
class CacheMetadata:
    """Metadata for cache entries."""

    key: str
    ttl: Optional[int] = None
    file_dependencies: List[Path] = field(default_factory=list)
    invalidation_strategy: InvalidationStrategy = InvalidationStrategy.TTL
    tags: Set[str] = field(default_factory=set)
    priority: CachePriority = CachePriority.MEDIUM
    version: str = "v1"
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    size_bytes: int = 0
    # Temporal support for VCS-based caching
    commit_ref: Optional[str] = None  # VCS commit reference (None = latest/current)
    # File tracking data for incremental invalidation
    file_mtimes: Dict[str, float] = field(default_factory=dict)
    file_hashes: Dict[str, str] = field(
        default_factory=dict
    )  # Whole-file hashes for cache validation
    content_hashes: Dict[str, str] = field(
        default_factory=dict
    )  # Guard section hashes (separate purpose)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "key": self.key,
            "ttl": self.ttl,
            "file_dependencies": [str(p) for p in self.file_dependencies],
            "invalidation_strategy": self.invalidation_strategy.value,
            "tags": list(self.tags),
            "priority": self.priority.value,
            "version": self.version,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "size_bytes": self.size_bytes,
            "commit_ref": self.commit_ref,
            "file_mtimes": self.file_mtimes,
            "file_hashes": self.file_hashes,
            "content_hashes": self.content_hashes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheMetadata":
        """Create from dictionary."""
        return cls(
            key=data["key"],
            ttl=data.get("ttl"),
            file_dependencies=[Path(p) for p in data.get("file_dependencies", [])],
            invalidation_strategy=InvalidationStrategy(data.get("invalidation_strategy", "ttl")),
            tags=set(data.get("tags", [])),
            priority=CachePriority(data.get("priority", 2)),
            version=data.get("version", "v1"),
            created_at=data.get("created_at", time.time()),
            last_accessed=data.get("last_accessed", time.time()),
            access_count=data.get("access_count", 0),
            size_bytes=data.get("size_bytes", 0),
            commit_ref=data.get("commit_ref"),
            file_mtimes=data.get("file_mtimes", {}),
            file_hashes=data.get("file_hashes", {}),
            content_hashes=data.get("content_hashes", {}),
        )


@dataclass
class CacheEntry:
    """Cache entry with value and metadata."""

    value: Any
    metadata: CacheMetadata

    def touch(self) -> None:
        """Update access time and count."""
        self.metadata.last_accessed = time.time()
        self.metadata.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "value": self.value,
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        return cls(
            value=data["value"],
            metadata=CacheMetadata.from_dict(data["metadata"]),
        )


class CacheRoutingStrategy:
    """Determines which cache tiers to use for different data types."""

    # Data that should never leave the local machine
    LOCAL_ONLY_PATTERNS = [
        "filtering:*",  # .ai-attributes, .gitignore
        "config:project:*",  # Project-specific configs
        "config:user:*",  # User-specific configs
        "filesystem:*",  # File metadata
        "workspace:*",  # Workspace analysis
        "content:*",  # Project file content
    ]

    # Data that can be shared across instances via Redis
    REDIS_ELIGIBLE_PATTERNS = [
        "templates:system_prompt:*",
        "themes:*",
        "config:global:*",
        "resources:shared:*",
        "analysis:shared:*",
    ]

    def get_eligible_tiers(self, cache_key: str) -> List[CacheTier]:
        """Returns which cache tiers are appropriate for the given key."""
        if any(fnmatch.fnmatch(cache_key, pattern) for pattern in self.LOCAL_ONLY_PATTERNS):
            return [CacheTier.MEMORY, CacheTier.DISK]
        elif any(fnmatch.fnmatch(cache_key, pattern) for pattern in self.REDIS_ELIGIBLE_PATTERNS):
            return [CacheTier.MEMORY, CacheTier.DISK, CacheTier.REDIS]
        else:
            # Default: local only for security
            return [CacheTier.MEMORY, CacheTier.DISK]

    def is_redis_eligible(self, cache_key: str) -> bool:
        """Check if data can be stored in Redis."""
        return CacheTier.REDIS in self.get_eligible_tiers(cache_key)


# Cache policies for different data types
CACHE_POLICIES: Dict[str, CachePolicy] = {
    "filtering:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.MTIME,
        ttl=None,  # Immediate invalidation
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=5,  # Scan every 5 seconds as backup
        priority=CachePriority.HIGH,
    ),
    "templates:system_prompt:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK, CacheTier.REDIS],
        invalidation_strategy=InvalidationStrategy.HYBRID,
        ttl=300,
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=60,
        priority=CachePriority.HIGH,
    ),
    "config:project:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.FILE_WATCH,
        ttl=None,
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=1,  # Very frequent for config changes
        priority=CachePriority.CRITICAL,
    ),
    "themes:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK, CacheTier.REDIS],
        invalidation_strategy=InvalidationStrategy.FILE_WATCH,
        ttl=None,
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=60,
        priority=CachePriority.MEDIUM,
    ),
    "resources:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK, CacheTier.REDIS],
        invalidation_strategy=InvalidationStrategy.CONTENT_HASH,
        ttl=3600,
        file_watching=False,  # Resources change infrequently
        polling_fallback=False,
        force_scan_interval=None,
        priority=CachePriority.LOW,
    ),
    "workspace:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.TTL,
        ttl=300,  # 5 minutes
        file_watching=False,
        polling_fallback=False,
        force_scan_interval=None,
        priority=CachePriority.MEDIUM,
    ),
    "content:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.TTL,
        ttl=600,  # 10 minutes
        file_watching=False,
        polling_fallback=False,
        force_scan_interval=None,
        priority=CachePriority.LOW,
    ),
    "smart_planning:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],  # Local only by default
        invalidation_strategy=InvalidationStrategy.TTL,
        ttl=3600,  # 1 hour for smart planning data
        file_watching=False,
        polling_fallback=False,
        force_scan_interval=None,
        priority=CachePriority.MEDIUM,
    ),
    "boundaries:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.HYBRID,
        ttl=3600,  # 1 hour
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=300,  # 5 minutes
        priority=CachePriority.HIGH,
    ),
}


class CacheBackend(ABC):
    """Abstract interface for cache storage backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        pass

    @abstractmethod
    def set(self, key: str, entry: CacheEntry) -> bool:
        """Store cache entry. Returns True if successful."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete cache entry. Returns True if successful."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching pattern."""
        pass

    @abstractmethod
    def clear(self) -> int:
        """Clear all entries. Returns number of entries cleared."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with LRU eviction."""

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 256):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._current_memory = 0

    def get(self, key: str) -> Optional[CacheEntry]:
        if key in self._cache:
            entry = self._cache[key]
            entry.touch()
            # Move to end of access order (most recently used)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return entry
        return None

    def set(self, key: str, entry: CacheEntry) -> bool:
        try:
            # Remove existing entry if present
            if key in self._cache:
                old_entry = self._cache[key]
                self._current_memory -= old_entry.metadata.size_bytes
                self._access_order.remove(key)

            # Check memory limits and evict if necessary
            self._evict_if_needed(entry.metadata.size_bytes)

            # Add new entry
            self._cache[key] = entry
            self._access_order.append(key)
            self._current_memory += entry.metadata.size_bytes

            return True
        except Exception as e:
            logger.error(f"Failed to set cache entry {key}: {e}")
            return False

    def _evict_if_needed(self, new_size: int) -> None:
        """Evict least recently used entries if needed."""
        while (
            len(self._cache) >= self.max_size
            or self._current_memory + new_size > self.max_memory_bytes
        ):
            if not self._access_order:
                break

            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                entry = self._cache.pop(lru_key)
                self._current_memory -= entry.metadata.size_bytes

    def delete(self, key: str) -> bool:
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_memory -= entry.metadata.size_bytes
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False

    def exists(self, key: str) -> bool:
        return key in self._cache

    def list_keys(self, pattern: str = "*") -> List[str]:
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]

    def clear(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        self._access_order.clear()
        self._current_memory = 0
        return count

    def get_stats(self) -> Dict[str, Any]:
        return {
            "type": "memory",
            "entries": len(self._cache),
            "max_size": self.max_size,
            "memory_usage_bytes": self._current_memory,
            "max_memory_bytes": self.max_memory_bytes,
            "memory_usage_percent": (self._current_memory / self.max_memory_bytes) * 100,
        }


class CacheMetrics:
    """Cache performance metrics collection."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.invalidations = 0
        self.errors = 0
        self.start_time = time.time()

    def record_hit(self):
        self.hits += 1

    def record_miss(self):
        self.misses += 1

    def record_set(self):
        self.sets += 1

    def record_delete(self):
        self.deletes += 1

    def record_invalidation(self):
        self.invalidations += 1

    def record_error(self):
        self.errors += 1

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0

    def get_stats(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.get_hit_rate(),
            "sets": self.sets,
            "deletes": self.deletes,
            "invalidations": self.invalidations,
            "errors": self.errors,
            "uptime_seconds": uptime,
        }


class CentralizedCacheManager(ICacheManager):
    """
    Central cache coordinator with tiered backends and data classification.

    Features:
    - Tiered caching with data classification (L1: memory, L2: disk, L3: Redis)
    - File watching with polling fallback
    - Multiple invalidation strategies
    - Cache warming and preloading
    - Performance metrics and monitoring
    """

    def __init__(
        self,
        backends: Dict[CacheTier, CacheBackend],
        routing_strategy: Optional[CacheRoutingStrategy] = None,
        cache_policies: Optional[Dict[str, CachePolicy]] = None,
        file_watcher: Optional[Any] = None,
    ):
        self.backends = backends
        self.routing_strategy = routing_strategy or CacheRoutingStrategy()
        self.cache_policies = cache_policies or CACHE_POLICIES
        self.metrics = CacheMetrics()
        self.file_watcher = file_watcher
        self._file_watchers: Dict[Path, Any] = {}  # Will be FileWatcher handles
        self._policy_cache: Dict[str, CachePolicy] = {}
        self._file_watching_enabled = False

    def get_policy(self, cache_key: str) -> CachePolicy:
        """Get cache policy for a given key."""
        if cache_key in self._policy_cache:
            return self._policy_cache[cache_key]

        # Find matching policy pattern
        for pattern, policy in self.cache_policies.items():
            if fnmatch.fnmatch(cache_key, pattern):
                self._policy_cache[cache_key] = policy
                return policy

        # Default policy for unmatched keys
        default_policy = CachePolicy(
            cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
            invalidation_strategy=InvalidationStrategy.TTL,
            ttl=300,
        )
        self._policy_cache[cache_key] = default_policy
        return default_policy

    def get(self, key: str, invalidation_check: bool = True) -> Optional[Any]:
        """Get value from cache with optional invalidation check."""
        try:
            policy = self.get_policy(key)
            eligible_tiers = self.routing_strategy.get_eligible_tiers(key)

            # Try each tier in order (L1 -> L2 -> L3)
            for tier in policy.cache_tiers:
                if tier not in eligible_tiers:
                    continue

                if tier not in self.backends:
                    continue

                backend = self.backends[tier]
                entry = backend.get(key)

                if entry is not None:
                    # Check if entry is still valid
                    if invalidation_check and not self._is_entry_valid(entry, policy):
                        # Invalid entry, remove from all tiers
                        self.invalidate(key)
                        self.metrics.record_invalidation()
                        continue

                    # Valid hit - populate higher tiers if needed
                    self._populate_higher_tiers(
                        key, entry, tier, policy.cache_tiers, eligible_tiers
                    )

                    self.metrics.record_hit()
                    return entry.value

            self.metrics.record_miss()
            return None

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.metrics.record_error()
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        file_dependencies: Optional[List[Path]] = None,
        tags: Optional[Set[str]] = None,
        priority: Optional[CachePriority] = None,
    ) -> bool:
        """Set value in cache with metadata."""
        try:
            policy = self.get_policy(key)
            eligible_tiers = self.routing_strategy.get_eligible_tiers(key)

            # Create cache entry
            metadata = CacheMetadata(
                key=key,
                ttl=ttl or policy.ttl,
                file_dependencies=file_dependencies or [],
                invalidation_strategy=policy.invalidation_strategy,
                tags=tags or set(),
                priority=priority or policy.priority,
            )

            # Populate file_mtimes if file dependencies exist and mtime tracking is needed
            if file_dependencies and policy.invalidation_strategy in [
                InvalidationStrategy.MTIME,
                InvalidationStrategy.HYBRID,
            ]:
                for file_path in file_dependencies:
                    try:
                        if file_path.exists():
                            metadata.file_mtimes[str(file_path)] = file_path.stat().st_mtime
                    except (OSError, AttributeError):
                        # If we can't get mtime, don't include this file in mtime tracking
                        pass

            # Estimate size (rough approximation)
            try:
                metadata.size_bytes = sys.getsizeof(value)
            except:
                metadata.size_bytes = 1024  # Default estimate

            entry = CacheEntry(value=value, metadata=metadata)

            # Store in all eligible tiers
            success = False
            for tier in policy.cache_tiers:
                if tier not in eligible_tiers:
                    continue

                if tier not in self.backends:
                    continue

                backend = self.backends[tier]
                if backend.set(key, entry):
                    success = True

            # Set up file watching if needed and enabled
            if policy.file_watching and file_dependencies and self.is_file_watching_enabled():
                self._setup_file_watching(key, file_dependencies)

            if success:
                self.metrics.record_set()

            return success

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.metrics.record_error()
            return False

    def invalidate(self, key: str) -> bool:
        """Invalidate cache entry from all tiers."""
        try:
            # Clean up file watchers for this cache key before deletion
            self._cleanup_file_watchers_for_key(key)

            success = False
            for backend in self.backends.values():
                if backend.delete(key):
                    success = True

            if success:
                self.metrics.record_delete()

            return success

        except Exception as e:
            logger.error(f"Cache invalidate error for key {key}: {e}")
            self.metrics.record_error()
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache entries matching pattern."""
        count = 0
        try:
            for backend in self.backends.values():
                keys = backend.list_keys(pattern)
                for key in keys:
                    if backend.delete(key):
                        count += 1

            self.metrics.invalidations += count
            return count

        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            self.metrics.record_error()
            return 0

    def invalidate_tags(self, tags: Set[str]) -> int:
        """Invalidate all cache entries with any of the given tags."""
        count = 0
        try:
            for backend in self.backends.values():
                keys = backend.list_keys()
                for key in keys:
                    entry = backend.get(key)
                    if entry and entry.metadata.tags.intersection(tags):
                        if backend.delete(key):
                            count += 1

            self.metrics.invalidations += count
            return count

        except Exception as e:
            logger.error(f"Cache invalidate tags error for {tags}: {e}")
            self.metrics.record_error()
            return 0

    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching pattern across all backends."""
        all_keys = set()
        try:
            for backend in self.backends.values():
                keys = backend.list_keys(pattern)
                all_keys.update(keys)
            return list(all_keys)
        except Exception as e:
            logger.error(f"Cache list_keys error for pattern {pattern}: {e}")
            return []

    def force_scan_files(self, paths: List[Path]) -> Dict[Path, bool]:
        """Manual scan for cache invalidation when watcher/polling unavailable."""
        changes = {}
        try:
            for path in paths:
                try:
                    current_mtime = path.stat().st_mtime if path.exists() else None

                    # Find cache entries that depend on this file
                    affected_keys = []
                    for backend in self.backends.values():
                        keys = backend.list_keys()
                        for key in keys:
                            entry = backend.get(key)
                            if entry and path in entry.metadata.file_dependencies:
                                affected_keys.append(key)

                    # Check if file has changed by comparing with cached mtime
                    file_changed = False
                    for key in affected_keys:
                        # This is simplified - in practice we'd store mtime in metadata
                        entry = self.backends[CacheTier.MEMORY].get(key)
                        if entry:
                            # Invalidate entries for changed files
                            self.invalidate(key)
                            file_changed = True

                    changes[path] = file_changed

                except Exception as e:
                    logger.error(f"Force scan error for {path}: {e}")
                    changes[path] = True  # Assume changed on error

            return changes

        except Exception as e:
            logger.error(f"Force scan error: {e}")
            return {path: True for path in paths}

    def warm_cache(self, keys: List[str]) -> int:
        """Warm cache by preloading specified keys."""
        # This would be implemented with actual data loading logic
        # For now, just a placeholder
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {"metrics": self.metrics.get_stats(), "backends": {}}

        for tier, backend in self.backends.items():
            try:
                stats["backends"][tier.value] = backend.get_stats()
            except Exception as e:
                logger.error(f"Failed to get stats for {tier}: {e}")
                stats["backends"][tier.value] = {"error": str(e)}

        return stats

    def start_file_watching(self) -> None:
        """Start file watching for cache invalidation."""
        if not self.file_watcher:
            logger.warning("No file watcher available to start")
            return

        self._file_watching_enabled = True
        logger.info("Starting file watching for cache manager")

        # Start watching all files that are currently being tracked in cache entries
        for backend in self.backends.values():
            keys = backend.list_keys()
            for key in keys:
                entry = backend.get(key)
                if entry and entry.metadata.file_dependencies:
                    try:
                        self._setup_file_watching(key, entry.metadata.file_dependencies)
                    except Exception as e:
                        logger.warning(f"Failed to start watching for cache key {key}: {e}")

    def stop_file_watching(self) -> None:
        """Stop file watching for cache invalidation."""
        self._file_watching_enabled = False

        # Clean up all existing file watchers
        files_to_cleanup = list(self._file_watchers.keys())
        for file_path in files_to_cleanup:
            try:
                handle = self._file_watchers.pop(file_path, None)
                if handle:
                    handle.stop()
                logger.debug(f"Stopped file watcher for {file_path}")
            except Exception as e:
                logger.warning(f"Error stopping file watcher for {file_path}: {e}")

        logger.info("File watching stopped for cache manager")

    def is_file_watching_enabled(self) -> bool:
        """Check if file watching is currently enabled."""
        return self._file_watching_enabled

    def _is_entry_valid(self, entry: CacheEntry, policy: CachePolicy) -> bool:
        """Check if cache entry is still valid based on policy."""
        now = time.time()

        # Check TTL if applicable
        if entry.metadata.ttl is not None:
            if now - entry.metadata.created_at > entry.metadata.ttl:
                return False

        # Check file dependencies if applicable
        if (
            policy.invalidation_strategy
            in [InvalidationStrategy.MTIME, InvalidationStrategy.HYBRID]
            and entry.metadata.file_dependencies
        ):
            for file_path in entry.metadata.file_dependencies:
                try:
                    file_path_str = str(file_path)
                    if file_path.exists():
                        current_mtime = file_path.stat().st_mtime
                        stored_mtime = entry.metadata.file_mtimes.get(file_path_str)

                        if stored_mtime is None:
                            # No stored mtime - cache entry is invalid
                            logger.debug(f"Cache invalid: no stored mtime for {file_path}")
                            return False

                        if abs(current_mtime - stored_mtime) > 0.001:  # Allow for float precision
                            # File has been modified
                            logger.debug(
                                f"Cache invalid: {file_path} mtime changed from {stored_mtime} to {current_mtime}"
                            )
                            return False
                    else:
                        # File no longer exists
                        logger.debug(f"Cache invalid: {file_path} no longer exists")
                        return False
                except Exception as e:
                    # Error accessing file
                    logger.debug(f"Cache invalid: error accessing {file_path}: {e}")
                    return False

        # Whole-file content validation when mtime changed but we want to double-check
        if (
            policy.invalidation_strategy
            in [InvalidationStrategy.CONTENT_HASH, InvalidationStrategy.HYBRID]
            and entry.metadata.file_dependencies
        ):
            hash_calculator = HashCalculator()
            for file_path in entry.metadata.file_dependencies:
                try:
                    file_path_str = str(file_path)
                    if not file_path.exists():
                        logger.debug(f"Cache invalid: {file_path} no longer exists")
                        return False

                    current_mtime = file_path.stat().st_mtime
                    stored_mtime = entry.metadata.file_mtimes.get(file_path_str)

                    if stored_mtime is None:
                        logger.debug(f"Cache invalid: no stored mtime for {file_path}")
                        return False

                    # Fast path: if mtime unchanged, content definitely unchanged
                    if abs(current_mtime - stored_mtime) <= 0.001:
                        continue  # Skip expensive hash calculation

                    # Expensive path: mtime changed, check if whole file content actually changed
                    stored_hash = entry.metadata.file_hashes.get(file_path_str)
                    if stored_hash is None:
                        logger.debug(f"Cache invalid: no stored file hash for {file_path}")
                        return False

                    # &? TODO: Needs to be async
                    current_content = file_path.read_text(encoding="utf-8", errors="ignore")
                    print(f"DEBUG: Hashing content of {file_path} for cache validation")
                    current_hash = hash_calculator.calculate_hash(current_content)

                    if current_hash != stored_hash:
                        # File content actually changed
                        logger.debug(f"Cache invalid: {file_path} file content changed")
                        return False
                    # else: mtime changed but file content same (e.g., touch, build regeneration)

                except Exception as e:
                    # Error reading/hashing file
                    logger.debug(f"Cache invalid: error processing file hash for {file_path}: {e}")
                    return False

        return True

    def _populate_higher_tiers(
        self,
        key: str,
        entry: CacheEntry,
        found_tier: CacheTier,
        policy_tiers: List[CacheTier],
        eligible_tiers: List[CacheTier],
    ) -> None:
        """Populate higher cache tiers with found entry."""
        try:
            found_index = policy_tiers.index(found_tier)

            # Populate all higher tiers (lower indices)
            for i in range(found_index):
                tier = policy_tiers[i]
                if tier in eligible_tiers and tier in self.backends:
                    self.backends[tier].set(key, entry)

        except (ValueError, Exception) as e:
            logger.debug(f"Failed to populate higher tiers for {key}: {e}")

    def _setup_file_watching(self, cache_key: str, file_dependencies: List[Path]) -> None:
        """Set up file watching for cache invalidation."""
        if not self.file_watcher:
            logger.debug(f"No file watcher available for {cache_key}")
            return

        for file_path in file_dependencies:
            if file_path in self._file_watchers:
                continue  # Already watching this file

            try:
                # Create invalidation callback for this cache key
                def invalidate_callback(path: Path) -> None:
                    logger.debug(f"File {path} changed, invalidating cache key: {cache_key}")
                    # Invalidate from all cache tiers
                    for backend in self.backends.values():
                        backend.delete(cache_key)

                # Set up file watching (this is async, but we'll handle it)
                import asyncio

                if self.file_watcher and asyncio.iscoroutinefunction(self.file_watcher.watch_file):
                    # For async file watchers, set up watching in background
                    watcher = self.file_watcher  # Capture for type narrowing

                    async def setup_async_watching():
                        try:
                            handle = await watcher.watch_file(file_path, invalidate_callback)
                            self._file_watchers[file_path] = handle
                            logger.debug(
                                f"Set up async file watching for {cache_key} on {file_path}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to set up async file watching for {file_path}: {e}"
                            )

                    # Schedule the async setup
                    try:
                        loop = asyncio.get_event_loop()
                        loop.create_task(setup_async_watching())
                    except RuntimeError:
                        # No event loop running, skip async watching
                        logger.debug(
                            f"No event loop available for async file watching: {cache_key}"
                        )
                else:
                    # For sync file watchers
                    handle = self.file_watcher.watch_file(file_path, invalidate_callback)
                    self._file_watchers[file_path] = handle
                    logger.debug(f"Set up sync file watching for {cache_key} on {file_path}")

            except Exception as e:
                logger.warning(f"Failed to set up file watching for {file_path}: {e}")

    def _cleanup_file_watchers_for_key(self, cache_key: str) -> None:
        """Clean up file watchers associated with a cache key."""
        if not self.file_watcher:
            return

        # Find all file paths that were being watched for this cache key
        # Note: We need to track which files belong to which cache keys
        # For now, we'll clean up watchers that are no longer needed by any cache entry

        # Get all remaining cache entries to see what files are still needed
        active_files = set()
        try:
            for backend in self.backends.values():
                keys = backend.list_keys()
                for key in keys:
                    if key == cache_key:
                        continue  # Skip the key being deleted
                    entry = backend.get(key)
                    if entry and entry.metadata.file_dependencies:
                        active_files.update(str(p) for p in entry.metadata.file_dependencies)
        except Exception as e:
            logger.debug(f"Error checking active files for watcher cleanup: {e}")
            return

        # Clean up watchers for files that are no longer watched by any cache entry
        files_to_cleanup = []
        for file_path in list(self._file_watchers.keys()):
            if str(file_path) not in active_files:
                files_to_cleanup.append(file_path)

        for file_path in files_to_cleanup:
            try:
                handle = self._file_watchers.pop(file_path, None)
                if handle:
                    # Stop the watcher
                    if hasattr(handle, "stop"):
                        handle.stop()
                    elif hasattr(handle, "task") and not handle.task.done():
                        handle.task.cancel()
                    logger.debug(f"Cleaned up file watcher for {file_path}")
            except Exception as e:
                logger.warning(f"Error cleaning up file watcher for {file_path}: {e}")
