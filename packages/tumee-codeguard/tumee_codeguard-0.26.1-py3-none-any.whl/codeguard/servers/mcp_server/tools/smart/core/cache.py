"""
Cache management system for smart planning.

This module provides cache interfaces for smart planning operations
using the centralized cache system with appropriate data classification.
"""

import logging
import os
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

from ......core import get_cache_manager
from ......core.interfaces import CachePriority

DEFAULT_TTL_SECONDS = 7 * 24 * 60 * 60  # 1 week


class SmartPlanningCache:
    """
    Smart planning cache interface using the centralized cache system.

    This class provides the same interface as the old cache providers
    but routes everything through the centralized cache with proper
    data classification.
    """

    def __init__(self, cache_prefix: str = "smart_planning"):
        self.cache_prefix = cache_prefix
        self.cache = get_cache_manager()

    def _make_key(self, key: str) -> str:
        """Create cache key with smart planning prefix."""
        return f"{self.cache_prefix}:{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._make_key(key)
        return self.cache.get(cache_key)

    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL_SECONDS) -> None:
        """Set value in cache with TTL."""
        cache_key = self._make_key(key)

        # Determine if this is session-specific (local only) or shareable
        tags = {"smart_planning"}
        priority = CachePriority.MEDIUM

        if any(pattern in key for pattern in ["session:", "user:", "local:"]):
            # Session/user data should stay local
            tags.add("session_data")
            priority = CachePriority.HIGH
        elif any(pattern in key for pattern in ["shared:", "template:", "analysis:"]):
            # Shared data can go to Redis
            tags.add("shared_data")
        else:
            # Default to local only for security
            tags.add("session_data")

        self.cache.set(cache_key, value, ttl=ttl, tags=tags, priority=priority)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        cache_key = self._make_key(key)
        self.cache.invalidate(cache_key)

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        cache_key = self._make_key(key)
        return self.cache.get(cache_key) is not None

    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching pattern."""
        try:
            # Get all keys with our prefix from centralized cache
            all_keys = self.cache.list_keys(f"{self.cache_prefix}:*")

            # Remove prefix and filter by pattern
            prefix_len = len(self.cache_prefix) + 1
            stripped_keys = [
                k[prefix_len:] for k in all_keys if k.startswith(f"{self.cache_prefix}:")
            ]

            # Apply pattern filtering
            import fnmatch

            return [k for k in stripped_keys if fnmatch.fnmatch(k, pattern)]
        except Exception as e:
            logger.error(f"Failed to list keys with pattern {pattern}: {e}")
            return []

    def clear_all(self) -> int:
        """Clear all smart planning cache entries."""
        pattern = f"{self.cache_prefix}:*"
        return self.cache.invalidate_pattern(pattern)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        stats = self.cache.get_stats()

        # Add smart planning specific info
        stats["smart_planning"] = {
            "prefix": self.cache_prefix,
            "type": "centralized_cache",
            "data_classification": "local_sessions_redis_shared",
        }

        return stats


class DiskCacheProvider(SmartPlanningCache):
    """
    Compatibility class for disk cache provider.
    Routes to centralized cache system.
    """

    def __init__(
        self,
        cache_dir: str = "~/.codeguard/smart_planning_cache",
        size_limit: int = 1024 * 1024 * 1024,
    ):
        super().__init__()
        # Store these for compatibility but they're handled by centralized cache
        self.cache_dir = cache_dir
        self.size_limit = size_limit

        # Ensure the cache directory exists (create both ~/.codeguard and smart_planning_cache)
        try:
            Path(cache_dir).expanduser().mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create smart planning cache directory {cache_dir}: {e}")


class RedisCacheProvider(SmartPlanningCache):
    """
    Compatibility class for Redis cache provider.
    Routes to centralized cache system.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "smart_planning:",
    ):
        # Extract the prefix without the colon for our cache prefix
        cache_prefix = key_prefix.rstrip(":")
        super().__init__(cache_prefix)

        # Store these for compatibility
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.key_prefix = key_prefix


class InMemoryCacheProvider(SmartPlanningCache):
    """
    Compatibility class for in-memory cache provider.
    Routes to centralized cache system.
    """

    def __init__(self):
        super().__init__()


# Global cache instance for compatibility
_cache_provider: Optional[SmartPlanningCache] = None


def init_cache_from_env() -> Optional[SmartPlanningCache]:
    """
    Initialize cache provider from environment variables.
    Now uses the centralized cache system.
    """
    global _cache_provider

    cache_type = os.getenv("SMART_PLANNING_CACHE", "centralized").lower()

    try:
        if cache_type == "redis":
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            # Parse Redis URL for compatibility
            import urllib.parse

            parsed = urllib.parse.urlparse(redis_url)

            _cache_provider = RedisCacheProvider(
                host=parsed.hostname or "localhost",
                port=parsed.port or 6379,
                password=parsed.password,
                db=int(parsed.path[1:]) if parsed.path and len(parsed.path) > 1 else 0,
            )
        elif cache_type == "disk":
            cache_dir = os.getenv("SMART_PLANNING_CACHE_DIR", "~/.codeguard/smart_planning_cache")
            size_limit = int(os.getenv("SMART_PLANNING_CACHE_SIZE", str(1024 * 1024 * 1024)))

            _cache_provider = DiskCacheProvider(cache_dir=cache_dir, size_limit=size_limit)
        else:
            # Default to centralized cache
            _cache_provider = SmartPlanningCache()

        return _cache_provider

    except Exception as e:
        print(f"Warning: Failed to initialize smart planning cache: {e}")
        print("Smart planning will work with centralized cache system")
        _cache_provider = SmartPlanningCache()
        return _cache_provider


def get_cache() -> Optional[SmartPlanningCache]:
    """Get the current cache provider."""
    global _cache_provider
    if _cache_provider is None:
        _cache_provider = init_cache_from_env()
    return _cache_provider


def set_cache(provider: SmartPlanningCache) -> None:
    """Set the cache provider (for testing)."""
    global _cache_provider
    _cache_provider = provider


def ensure_cache_initialized() -> Optional[SmartPlanningCache]:
    """Ensure cache is initialized, initialize if needed."""
    return get_cache()


# Initialize cache on module import
init_cache_from_env()
