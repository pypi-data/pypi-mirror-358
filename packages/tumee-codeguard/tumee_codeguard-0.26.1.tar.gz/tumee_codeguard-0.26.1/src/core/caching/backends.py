"""
Cache backend implementations for the centralized caching system.

This module provides concrete implementations of cache backends including
disk cache and Redis cache, extending the existing smart_planning_cache
interfaces for backward compatibility.
"""

import dataclasses
import fnmatch
import gzip
import importlib
import json
import logging
import os
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

# Dependencies
import diskcache
import lz4.frame
import pathspec

try:
    import redis
except ImportError:
    redis = None

from ..filesystem.watcher import FileWatcherWithFallback
from .centralized import (
    CACHE_POLICIES,
    CacheBackend,
    CacheEntry,
    CacheRoutingStrategy,
    CacheTier,
    CentralizedCacheManager,
)

logger = logging.getLogger(__name__)

# Module-level cache for class lookups
_CLASS_CACHE: Dict[str, Type] = {}
# Cache this ONCE at module level
_DEBUG_MODE = os.getenv("CODEGUARD_CACHE_DEBUG", "").lower() in ("1", "true", "yes")


def _get_class_from_name(class_path: str) -> Type:
    """Get class from full path with lazy import fallback."""
    debug_mode = _DEBUG_MODE

    if class_path in _CLASS_CACHE:
        if debug_mode:
            logger.debug(f"Cache hit for class: {class_path}")
        return _CLASS_CACHE[class_path]

    if debug_mode:
        logger.debug(f"Resolving class: {class_path}")

    # Normalize src.* paths to codeguard.* paths
    normalized_path = class_path
    if class_path.startswith("src."):
        normalized_path = "codeguard." + class_path[4:]
        if debug_mode:
            logger.debug(f"Normalized {class_path} to {normalized_path}")

    try:
        module_path, class_name = normalized_path.rsplit(".", 1)

        # Try to get from already loaded modules first
        module = sys.modules.get(module_path)
        if module is not None:
            try:
                cls = getattr(module, class_name)
                _CLASS_CACHE[class_path] = cls
                if debug_mode:
                    logger.debug(f"Found class in loaded modules: {normalized_path}")
                return cls
            except AttributeError:
                if debug_mode:
                    logger.debug(
                        f"Class {class_name} not found in loaded module {module_path}, falling back to import"
                    )

        # Fallback: import module if not loaded or class not found
        if debug_mode:
            logger.debug(f"Importing module: {module_path}")
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        _CLASS_CACHE[class_path] = cls
        if debug_mode:
            logger.debug(f"Successfully imported and cached class: {normalized_path}")
        return cls
    except Exception as e:
        logger.error(f"Failed to resolve class {class_path}: {e}")
        if debug_mode:
            logger.exception(f"Full traceback for class resolution failure: {class_path}")
        raise


class CodeGuardJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for CodeGuard objects."""

    def default(self, o):
        # Generic dataclass handling
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            # Normalize module path to handle src/ vs codeguard/ package structure
            module_name = o.__class__.__module__
            if module_name.startswith("src."):
                module_name = "codeguard." + module_name[4:]  # Replace 'src.' with 'codeguard.'

            return {
                "__type__": "dataclass",
                "__class__": f"{module_name}.{o.__class__.__qualname__}",
                "__data__": dataclasses.asdict(o),
            }

        # Handle PathSpec objects
        if isinstance(o, pathspec.PathSpec):
            return {
                "__type__": "PathSpec",
                "patterns": [getattr(pattern, "pattern", str(pattern)) for pattern in o.patterns],
            }

        # Handle Path objects
        if isinstance(o, Path):
            return {
                "__type__": "Path",
                "path": str(o),
            }

        # Handle sets
        if isinstance(o, set):
            return {
                "__type__": "set",
                "items": list(o),
            }

        # Let the base class handle other types
        return super().default(o)


def codeguard_json_decoder(dct):
    """Custom JSON decoder for CodeGuard objects."""
    debug_mode = _DEBUG_MODE

    if "__type__" in dct:
        obj_type = dct["__type__"]

        if debug_mode:
            logger.debug(f"Decoding object of type: {obj_type}")

        try:
            if obj_type == "dataclass":
                class_path = dct["__class__"]
                if debug_mode:
                    logger.debug(f"Reconstructing dataclass: {class_path}")
                cls = _get_class_from_name(class_path)

                # Validate that we have the expected data
                if "__data__" not in dct:
                    raise ValueError(f"Missing __data__ field for dataclass {class_path}")

                result = cls(**dct["__data__"])
                if debug_mode:
                    logger.debug(f"Successfully reconstructed dataclass: {class_path}")
                return result

            elif obj_type == "PathSpec":
                if debug_mode:
                    logger.debug(f"Reconstructing PathSpec with {len(dct['patterns'])} patterns")
                return pathspec.PathSpec.from_lines("gitwildmatch", dct["patterns"])

            elif obj_type == "Path":
                if debug_mode:
                    logger.debug(f"Reconstructing Path: {dct['path']}")
                return Path(dct["path"])

            elif obj_type == "set":
                if debug_mode:
                    logger.debug(f"Reconstructing set with {len(dct['items'])} items")
                return set(dct["items"])

            else:
                logger.warning(f"Unknown object type in cache: {obj_type}")

        except Exception as e:
            logger.error(f"Failed to decode object of type {obj_type}: {e}")
            if debug_mode:
                logger.exception(f"Full traceback for decoding failure: {obj_type}")
            # In debug mode, re-raise to see the full error
            if debug_mode:
                raise
            # In production, return the raw dict to avoid complete failure
            return dct

    return dct


class DiskCacheBackend(CacheBackend):
    """
    Disk-based cache backend using diskcache library.
    Extends the existing DiskCacheProvider functionality.
    """

    def __init__(
        self,
        cache_dir: str = ".codeguard/cache/metadata",
        size_limit: int = 1024 * 1024 * 1024,
        compression_type: str = "lz4",
    ):
        """
        Initialize disk cache.

        Args:
            cache_dir: Directory for cache files (default: .codeguard/cache/metadata)
            size_limit: Maximum cache size in bytes (default: 1GB)
            compression_type: Compression type ('none', 'lz4', 'gzip', default: 'lz4')
        """
        self.original_cache_dir = cache_dir
        self.cache_dir = Path(cache_dir)
        self.size_limit = size_limit
        self.compression_type = compression_type.lower() if compression_type else "none"
        self._cache: Optional[diskcache.Cache] = None
        self._init_cache()

    def _ensure_cache_directory(self):
        """Ensure cache directory exists, creating it if necessary. Try fallback to ~/.codeguard if CWD fails."""
        # First try the original path (usually relative to CWD)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured cache directory exists: {self.cache_dir}")
            return True
        except Exception as e:
            logger.debug(f"Failed to create cache directory {self.cache_dir}: {e}")

        # Fallback to home directory if original path failed
        fallback_dir = None
        try:
            fallback_dir = Path.home() / self.original_cache_dir
            fallback_dir.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"Cache directory creation failed at {self.cache_dir}, using fallback: {fallback_dir}"
            )
            self.cache_dir = fallback_dir
            return True
        except Exception as e:
            logger.error(f"Failed to create fallback cache directory {fallback_dir}: {e}")
            return False

    def _init_cache(self):
        """Initialize the diskcache instance."""
        if diskcache is None:
            logger.error("diskcache library required but not installed")
            raise ImportError("diskcache required for disk caching")

        try:
            # Ensure the full cache directory path exists
            if not self._ensure_cache_directory():
                raise RuntimeError(f"Could not create cache directory: {self.cache_dir}")

            self._cache = diskcache.Cache(
                str(self.cache_dir),
                size_limit=self.size_limit,
                eviction_policy="least-recently-used",
            )
            logger.debug(f"Initialized disk cache at: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize disk cache at {self.cache_dir}: {e}")
            raise

    def _serialize_entry(self, entry: CacheEntry) -> bytes:
        """Serialize cache entry to bytes with configurable compression."""
        try:
            # Convert to JSON-serializable dictionary
            entry_dict = entry.to_dict()
            json_str = json.dumps(
                entry_dict, cls=CodeGuardJSONEncoder, separators=(",", ":")
            )  # Compact JSON
            json_bytes = json_str.encode("utf-8")

            if self.compression_type == "gzip":
                return gzip.compress(json_bytes)
            elif self.compression_type == "lz4":
                return lz4.frame.compress(json_bytes)
            else:  # "none" or any other value
                return json_bytes
        except Exception as e:
            logger.error(f"Failed to serialize cache entry: {e}")
            raise

    def _deserialize_entry(self, data: bytes) -> CacheEntry:
        """Deserialize cache entry from bytes with auto-detection of compression format."""
        try:
            # Auto-detect compression format by checking magic headers
            if data.startswith(b"\x1f\x8b"):
                # gzip magic header
                json_bytes = gzip.decompress(data)
            elif data.startswith(b'\x04"M\x18'):
                # lz4 magic header
                json_bytes = lz4.frame.decompress(data)
            else:
                # Plain JSON data
                json_bytes = data

            json_str = json_bytes.decode("utf-8")
            entry_dict = json.loads(json_str, object_hook=codeguard_json_decoder)
            return CacheEntry.from_dict(entry_dict)
        except Exception as e:
            logger.error(f"Failed to deserialize cache entry: {e}")
            raise

    def repair_cache(self):
        """Repair cache after directory or filesystem issues."""
        logger.info(f"Repairing cache at: {self.cache_dir}")
        try:
            # Recreate directory structure if needed
            if not self._ensure_cache_directory():
                logger.error("Cannot create cache directory - may be read-only filesystem")
                return False

            # Reinitialize cache instance to recreate internal files
            if self._cache:
                try:
                    # Let diskcache recreate its internal structure
                    self._cache.clear()
                    return True
                except Exception:
                    # If clear fails, try full reinitialization
                    pass

            # Full reinitialization as fallback
            self._cache = None
            self._init_cache()
            return True

        except Exception as e:
            logger.error(f"Cache repair failed (read-only filesystem?): {e}")
            return False

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        debug_mode = _DEBUG_MODE

        try:
            if self._cache is None:
                return None

            data = self._cache.get(key)
            if data is None:
                return None

            # Deserialize the cache entry using JSON/gzip
            if isinstance(data, bytes):
                return self._deserialize_entry(data)

            # Handle legacy format - this should not happen after migration
            logger.warning(f"Found legacy cache format for key {key}, skipping")
            return None

        except (IOError, OSError, FileNotFoundError) as e:
            logger.debug(f"Cache directory issue detected, repairing: {e}")
            self.repair_cache()
            return None
        except Exception as e:
            logger.error(f"Disk cache get error for key {key}: {e}")
            if debug_mode:
                logger.exception(f"Full traceback for cache get failure: {key}")
                # In debug mode, re-raise to see what's breaking
                raise
            return None

    def set(self, key: str, entry: CacheEntry) -> bool:
        """Store cache entry."""
        try:
            if self._cache is None:
                return False

            # Serialize the entry using JSON/gzip
            serialized_data = self._serialize_entry(entry)

            # Set with TTL if specified
            if entry.metadata.ttl:
                self._cache.set(key, serialized_data, expire=entry.metadata.ttl)
            else:
                self._cache.set(key, serialized_data)

            return True

        except (IOError, OSError, FileNotFoundError) as e:
            logger.debug(f"Cache directory issue detected, repairing: {e}")
            if self.repair_cache():
                # Retry once after repair
                try:
                    if self._cache:
                        serialized_data = self._serialize_entry(entry)
                        if entry.metadata.ttl:
                            self._cache.set(key, serialized_data, expire=entry.metadata.ttl)
                        else:
                            self._cache.set(key, serialized_data)
                        return True
                except Exception:
                    pass
            return False
        except Exception as e:
            logger.error(f"Disk cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        try:
            if self._cache is None:
                return False

            if key in self._cache:
                del self._cache[key]
                return True
            return False

        except Exception as e:
            logger.error(f"Disk cache delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return self._cache is not None and key in self._cache
        except Exception as e:
            logger.error(f"Disk cache exists error for key {key}: {e}")
            return False

    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching pattern."""
        try:
            if self._cache is None:
                return []

            return [str(k) for k in self._cache.iterkeys() if fnmatch.fnmatch(str(k), pattern)]

        except Exception as e:
            logger.error(f"Disk cache list_keys error: {e}")
            return []

    def clear(self) -> int:
        """Clear all entries."""
        try:
            if self._cache is None:
                return 0

            count = len(self._cache)  # type: ignore[arg-type]
            self._cache.clear()
            return count

        except Exception as e:
            logger.error(f"Disk cache clear error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if self._cache is None:
                return {"type": "disk", "error": "cache not initialized"}

            return {
                "type": "disk",
                "entries": len(self._cache),  # type: ignore[arg-type]
                "cache_dir": str(self.cache_dir),
                "size_limit": self.size_limit,
                "disk_usage": self._cache.volume(),
                "cache_hits": getattr(self._cache, "cache_hits", 0),
                "cache_misses": getattr(self._cache, "cache_misses", 0),
            }

        except Exception as e:
            logger.error(f"Disk cache stats error: {e}")
            return {"type": "disk", "error": str(e)}


class RedisCacheBackend(CacheBackend):
    """
    Redis-based cache backend for distributed caching.
    Extends the existing RedisCacheProvider functionality.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "codeguard:",
        connection_pool_size: int = 10,
    ):
        """
        Initialize Redis cache.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            key_prefix: Prefix for all keys
            connection_pool_size: Size of connection pool
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.key_prefix = key_prefix
        self.connection_pool_size = connection_pool_size
        self._redis: Any = None
        self._connection_pool: Any = None
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis connection."""
        if redis is None:
            logger.error("redis library required but not installed")
            raise ImportError("redis required for Redis caching")

        try:
            # Create connection pool
            self._connection_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.connection_pool_size,
                decode_responses=False,  # We handle serialization
            )

            self._redis = redis.Redis(connection_pool=self._connection_pool)

            # Test connection
            self._redis.ping()
            logger.info(f"Redis cache initialized: {self.host}:{self.port}/{self.db}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        try:
            if not self._redis:
                return None

            full_key = self._make_key(key)
            data = self._redis.get(full_key)

            if data is None:
                return None

            # Deserialize the cache entry using JSON
            json_str = data.decode("utf-8")
            entry_dict = json.loads(json_str, object_hook=codeguard_json_decoder)
            entry_data = CacheEntry.from_dict(entry_dict)

            # Refresh TTL on access if specified
            if entry_data.metadata.ttl:
                self._redis.expire(full_key, entry_data.metadata.ttl)

            return entry_data

        except Exception as e:
            logger.error(f"Redis cache get error for key {key}: {e}")
            return None

    def set(self, key: str, entry: CacheEntry) -> bool:
        """Store cache entry."""
        try:
            if not self._redis:
                return False

            full_key = self._make_key(key)
            entry_dict = entry.to_dict()
            serialized = json.dumps(
                entry_dict, cls=CodeGuardJSONEncoder, separators=(",", ":")
            ).encode("utf-8")

            # Set with TTL if specified
            if entry.metadata.ttl:
                self._redis.setex(full_key, entry.metadata.ttl, serialized)
            else:
                self._redis.set(full_key, serialized)

            return True

        except Exception as e:
            logger.error(f"Redis cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        try:
            if not self._redis:
                return False

            full_key = self._make_key(key)
            result = self._redis.delete(full_key)
            return result > 0

        except Exception as e:
            logger.error(f"Redis cache delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if not self._redis:
                return False

            full_key = self._make_key(key)
            return bool(self._redis.exists(full_key))

        except Exception as e:
            logger.error(f"Redis cache exists error for key {key}: {e}")
            return False

    def list_keys(self, pattern: str = "*") -> List[str]:
        """List all keys matching pattern."""
        try:
            if not self._redis:
                return []

            full_pattern = self._make_key(pattern)
            keys = self._redis.keys(full_pattern)

            # Remove prefix from keys
            prefix_len = len(self.key_prefix)
            return [k.decode("utf-8")[prefix_len:] for k in keys]

        except Exception as e:
            logger.error(f"Redis cache list_keys error: {e}")
            return []

    def clear(self) -> int:
        """Clear all keys with our prefix."""
        try:
            if not self._redis:
                return 0

            pattern = self._make_key("*")
            keys = self._redis.keys(pattern)

            if keys:
                return self._redis.delete(*keys)
            return 0

        except Exception as e:
            logger.error(f"Redis cache clear error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if not self._redis:
                return {"type": "redis", "error": "redis not initialized"}

            info = self._redis.info()
            pattern = self._make_key("*")
            our_keys = len(self._redis.keys(pattern))

            return {
                "type": "redis",
                "our_keys": our_keys,
                "total_keys": info.get("db0", {}).get("keys", 0),
                "memory_usage": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "connection_pool_size": self.connection_pool_size,
            }

        except Exception as e:
            logger.error(f"Redis cache stats error: {e}")
            return {"type": "redis", "error": str(e)}


def create_cache_backends(config: Dict[str, Any]) -> Dict[CacheTier, CacheBackend]:
    """
    Factory function to create cache backends based on configuration.

    Args:
        config: Configuration dictionary with backend settings

    Returns:
        Dictionary mapping cache tiers to backend instances
    """
    backends = {}

    # Memory backend (always included)
    from .centralized import MemoryCacheBackend

    memory_config = config.get("memory", {})
    backends[CacheTier.MEMORY] = MemoryCacheBackend(
        max_size=memory_config.get("max_size", 1000),
        max_memory_mb=memory_config.get("max_memory_mb", 256),
    )

    # Disk backend
    if "disk" in config:
        disk_config = config["disk"]
        backends[CacheTier.DISK] = DiskCacheBackend(
            cache_dir=disk_config.get("cache_dir", ".codeguard/cache/metadata"),
            size_limit=disk_config.get("size_limit", 1024 * 1024 * 1024),  # 1GB
            compression_type=disk_config.get("compression_type", "lz4"),
        )

    # Redis backend
    if "redis" in config:
        redis_config = config["redis"]
        backends[CacheTier.REDIS] = RedisCacheBackend(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            db=redis_config.get("db", 0),
            password=redis_config.get("password"),
            key_prefix=redis_config.get("key_prefix", "codeguard:"),
            connection_pool_size=redis_config.get("connection_pool_size", 10),
        )

    return backends
