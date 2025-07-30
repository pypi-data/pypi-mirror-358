"""
Integration helpers for migrating existing caches to the centralized system.

This module provides utilities to gradually migrate the existing 8 cache
implementations to use the centralized cache manager while maintaining
backward compatibility.
"""

import asyncio
import inspect
import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ..interfaces import IFileSystemAccess, ISecurityManager
from .centralized import CachePriority, InvalidationStrategy
from .manager import get_cache_manager

logger = logging.getLogger(__name__)


def cached_file_read(
    cache_key_template: str,
    file_path_param: str = "file_path",
    ttl: Optional[int] = None,
    priority: CachePriority = CachePriority.MEDIUM,
    invalidation_strategy: InvalidationStrategy = InvalidationStrategy.MTIME,
    tags: Optional[List[str]] = None,
):
    """
    Decorator to cache file reading operations.

    Args:
        cache_key_template: Template for cache key with {file_path} placeholder
        file_path_param: Name of the parameter containing the file path
        ttl: Time to live in seconds
        priority: Cache priority level
        invalidation_strategy: How to invalidate the cache
        tags: Tags for bulk invalidation

    Example:
        @cached_file_read("templates:user_prompt:{file_path}", ttl=300)
        def read_user_template(file_path: Path) -> str:
            return file_path.read_text()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Get file path from arguments
            if file_path_param in kwargs:
                file_path = kwargs[file_path_param]
            else:
                # Try to get from positional args based on function signature
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                if file_path_param in param_names:
                    param_index = param_names.index(file_path_param)
                    if param_index < len(args):
                        file_path = args[param_index]
                    else:
                        raise ValueError(f"Could not find {file_path_param} in function arguments")
                else:
                    raise ValueError(f"Parameter {file_path_param} not found in function signature")

            # Convert to Path if needed
            if not isinstance(file_path, Path):
                file_path = Path(file_path)

            # Generate cache key
            cache_key = cache_key_template.format(file_path=str(file_path))

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call the original function
            try:
                result = func(*args, **kwargs)

                # Cache the result
                cache.set(
                    cache_key,
                    result,
                    ttl=ttl,
                    file_dependencies=[file_path],
                    tags=set(tags) if tags else None,
                    priority=priority,
                )

                return result

            except Exception as e:
                logger.error(f"Error in cached file read for {file_path}: {e}")
                raise

        return wrapper

    return decorator


def cached_directory_scan(
    cache_key_template: str,
    directory_param: str = "directory",
    ttl: int = 300,
    watch_patterns: Optional[List[str]] = None,
):
    """
    Decorator to cache directory scanning operations.

    Args:
        cache_key_template: Template for cache key
        directory_param: Name of the parameter containing the directory path
        ttl: Time to live in seconds
        watch_patterns: File patterns to watch for changes
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Get directory path from arguments
            if directory_param in kwargs:
                directory = kwargs[directory_param]
            else:
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                if directory_param in param_names:
                    param_index = param_names.index(directory_param)
                    if param_index < len(args):
                        directory = args[param_index]
                    else:
                        raise ValueError(f"Could not find {directory_param} in function arguments")
                else:
                    raise ValueError(f"Parameter {directory_param} not found in function signature")

            # Convert to Path if needed
            if not isinstance(directory, Path):
                directory = Path(directory)

            # Generate cache key
            cache_key = cache_key_template.format(directory=str(directory))

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call the original function
            try:
                result = func(*args, **kwargs)

                # Get file dependencies if watch patterns specified
                file_dependencies = []
                if watch_patterns:
                    for pattern in watch_patterns:
                        file_dependencies.extend(directory.glob(pattern))

                # Cache the result
                cache.set(
                    cache_key,
                    result,
                    ttl=ttl,
                    file_dependencies=file_dependencies,
                    tags={"directory_scan", str(directory)},
                    priority=CachePriority.MEDIUM,
                )

                return result

            except Exception as e:
                logger.error(f"Error in cached directory scan for {directory}: {e}")
                raise

        return wrapper

    return decorator


class CacheableMixin:
    """
    Mixin class to add caching capabilities to existing classes.

    Example:
        class ThemeManager(CacheableMixin):
            def load_themes(self):
                return self._cached_call(
                    "themes:load_all",
                    self._load_themes_impl,
                    ttl=3600,
                    file_dependencies=[Path("themes.json")]
                )
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = get_cache_manager()

    def _cached_call(
        self,
        cache_key: str,
        func: Callable,
        *args,
        ttl: Optional[int] = None,
        file_dependencies: Optional[List[Path]] = None,
        tags: Optional[List[str]] = None,
        priority: CachePriority = CachePriority.MEDIUM,
        **kwargs,
    ) -> Any:
        """
        Execute a function with caching.

        Args:
            cache_key: Key for caching the result
            func: Function to call if cache miss
            ttl: Time to live for cache entry
            file_dependencies: Files to watch for invalidation
            tags: Tags for bulk invalidation
            priority: Cache priority
            *args, **kwargs: Arguments to pass to func
        """
        # Try cache first
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Cache miss - call function
        try:
            result = func(*args, **kwargs)

            # Cache the result
            self._cache.set(
                cache_key,
                result,
                ttl=ttl,
                file_dependencies=file_dependencies,
                tags=set(tags) if tags else None,
                priority=priority,
            )

            return result

        except Exception as e:
            logger.error(f"Error in cached call for {cache_key}: {e}")
            raise

    def _invalidate_cache(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        return self._cache.invalidate_pattern(pattern)

    def _invalidate_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries with specified tags."""
        return self._cache.invalidate_tags(set(tags))


class FileSystemCacheHelper:
    """
    Helper class for filesystem-based caching operations.
    Provides common patterns for file and directory caching.
    """

    def __init__(self, cache_manager=None, filesystem_access: Optional[IFileSystemAccess] = None):
        if filesystem_access is None:
            raise ValueError("Filesystem access is required for FileSystemCacheHelper")
        self.cache = cache_manager or get_cache_manager()
        self.filesystem_access = filesystem_access

    def cached_file_content(
        self, file_path: Path, cache_prefix: str = "content:file", encoding: str = "utf-8"
    ) -> str:
        """
        Get file content with caching.

        Args:
            file_path: Path to the file
            cache_prefix: Prefix for cache key
            encoding: File encoding
        """
        cache_key = f"{cache_prefix}:{file_path}"

        # Try cache first
        cached_content = self.cache.get(cache_key)
        if cached_content is not None:
            return cached_content

        # Read file
        try:
            content = file_path.read_text(encoding=encoding)

            # Cache with file dependency
            self.cache.set(
                cache_key,
                content,
                file_dependencies=[file_path],
                priority=CachePriority.LOW,
                tags={"file_content"},
            )

            return content

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    def cached_file_mtime(self, file_path: Path, cache_prefix: str = "mtime") -> float:
        """Get file modification time with caching."""
        cache_key = f"{cache_prefix}:{file_path}"

        cached_mtime = self.cache.get(cache_key)
        if cached_mtime is not None:
            return cached_mtime

        try:
            mtime = file_path.stat().st_mtime

            # Cache for short duration since mtime is used for invalidation
            self.cache.set(
                cache_key, mtime, ttl=60, priority=CachePriority.HIGH, tags={"mtime"}  # 1 minute
            )

            return mtime

        except Exception as e:
            logger.error(f"Error getting mtime for {file_path}: {e}")
            raise

    async def cached_directory_listing(
        self,
        directory: Path,
        pattern: str = "*",
        recursive: bool = False,
        cache_prefix: str = "listing",
    ) -> List[Path]:
        """Get directory listing with caching."""
        cache_key = f"{cache_prefix}:{directory}:{pattern}:{recursive}"

        cached_listing = self.cache.get(cache_key)
        if cached_listing is not None:
            return cached_listing

        try:
            # Use safe_glob for all directory operations
            files = await self.filesystem_access.safe_glob(directory, pattern, recursive=recursive)

            # Cache with directory as dependency
            self.cache.set(
                cache_key,
                files,
                ttl=300,  # 5 minutes
                file_dependencies=[directory],
                priority=CachePriority.MEDIUM,
                tags={"directory_listing", str(directory)},
            )

            return files

        except Exception as e:
            logger.error(f"Error listing directory {directory}: {e}")
            raise

    def invalidate_file_caches(self, file_path: Path) -> int:
        """Invalidate all caches related to a specific file."""
        return self.cache.invalidate_pattern(f"*:{file_path}")

    def invalidate_directory_caches(self, directory: Path) -> int:
        """Invalidate all caches related to a specific directory."""
        return self.cache.invalidate_tags({str(directory), "directory_listing"})


# Migration helpers for existing cache implementations
class LegacyCacheAdapter:
    """
    Adapter to make existing cache implementations use the centralized cache.
    Provides backward compatibility for gradual migration.
    """

    def __init__(self, cache_prefix: str, cache_manager=None):
        self.cache_prefix = cache_prefix
        self.cache = cache_manager or get_cache_manager()

    def get(self, key: str) -> Any:
        """Get value from cache (legacy interface)."""
        full_key = f"{self.cache_prefix}:{key}"
        return self.cache.get(full_key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache (legacy interface)."""
        full_key = f"{self.cache_prefix}:{key}"
        self.cache.set(full_key, value, ttl=ttl)

    def delete(self, key: str) -> None:
        """Delete value from cache (legacy interface)."""
        full_key = f"{self.cache_prefix}:{key}"
        self.cache.invalidate(full_key)

    def clear(self) -> None:
        """Clear all values with this prefix."""
        pattern = f"{self.cache_prefix}:*"
        self.cache.invalidate_pattern(pattern)


# Async utilities for file watching integration
async def setup_cache_file_watching():
    """Set up file watching for cache invalidation."""
    from ..filesystem.watcher import FileWatcherWithFallback

    cache = get_cache_manager()
    watcher = FileWatcherWithFallback()

    try:
        # Watch common configuration directories
        config_dirs = [
            Path.home() / ".codeguard",
            Path(".codeguard"),
            Path("src/resources/themes"),
            Path("src/servers/llm_proxy/templates"),
        ]

        for config_dir in config_dirs:
            if config_dir.exists():

                def make_invalidation_callback(pattern: str):
                    def callback(changed_path: Path):
                        logger.info(f"File changed: {changed_path}, invalidating {pattern}")
                        cache.invalidate_pattern(pattern)

                    return callback

                # Set up watching based on directory type
                if "themes" in str(config_dir):
                    await watcher.watch_directory(
                        config_dir,
                        make_invalidation_callback("themes:*"),
                        recursive=True,
                        patterns=["*.json", "*.yaml", "*.yml"],
                    )
                elif "templates" in str(config_dir):
                    await watcher.watch_directory(
                        config_dir,
                        make_invalidation_callback("templates:*"),
                        recursive=True,
                        patterns=["*.md", "*.txt"],
                    )
                elif ".codeguard" in str(config_dir):
                    await watcher.watch_directory(
                        config_dir,
                        make_invalidation_callback("config:*"),
                        recursive=False,
                        patterns=["*.json", "*.yaml", "*.yml"],
                    )

        logger.info("Cache file watching setup complete")

    except Exception as e:
        logger.error(f"Error setting up cache file watching: {e}")


def migrate_existing_cache(old_cache_instance, new_cache_prefix: str):
    """
    Helper to migrate data from existing cache to centralized cache.

    Args:
        old_cache_instance: Instance of existing cache
        new_cache_prefix: Prefix for keys in centralized cache
    """
    cache = get_cache_manager()
    migrated_count = 0

    try:
        # Try to extract data from old cache
        if hasattr(old_cache_instance, "keys"):
            keys = old_cache_instance.keys()
        elif hasattr(old_cache_instance, "_cache") and hasattr(old_cache_instance._cache, "keys"):
            keys = old_cache_instance._cache.keys()
        else:
            logger.warning(f"Cannot extract keys from cache instance: {type(old_cache_instance)}")
            return 0

        for key in keys:
            try:
                value = old_cache_instance.get(key)
                if value is not None:
                    new_key = f"{new_cache_prefix}:{key}"
                    cache.set(new_key, value, ttl=3600)  # Default 1 hour TTL
                    migrated_count += 1
            except Exception as e:
                logger.warning(f"Error migrating cache entry {key}: {e}")

        logger.info(f"Migrated {migrated_count} cache entries to centralized cache")
        return migrated_count

    except Exception as e:
        logger.error(f"Error during cache migration: {e}")
        return 0
