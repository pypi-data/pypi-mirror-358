"""
Cache integration for the CodeGuard context scanner.

This module provides integration with the existing CentralizedCacheManager,
adding context-specific cache policies and ensuring security compliance.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.caching.centralized import (
    CachePolicy,
    CachePriority,
    CacheTier,
    InvalidationStrategy,
)
from ..core.infrastructure.filtering import create_filter
from ..core.interfaces import (
    ICacheManager,
    IContextCacheManager,
    IFileSystemAccess,
    ISecurityManager,
)
from .models import CACHE_KEY_PATTERNS, DEFAULT_THRESHOLDS, make_cache_key

logger = logging.getLogger(__name__)


# Context-specific cache policies
CONTEXT_CACHE_POLICIES = {
    "context:breadth:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.MTIME,
        ttl=DEFAULT_THRESHOLDS["cache_ttl_seconds"],
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=60,  # Check every minute
        priority=CachePriority.HIGH,
    ),
    "context:module:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.FILE_WATCH,
        ttl=None,  # Invalidate based on file changes only
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=30,  # More frequent for module changes
        priority=CachePriority.CRITICAL,
    ),
    "context:project:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.FILE_WATCH,
        ttl=None,  # Invalidate based on file changes only
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=60,  # Check every minute
        priority=CachePriority.MEDIUM,
    ),
    "context:metadata:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.FILE_WATCH,
        ttl=None,  # Invalidate based on file changes only
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=60,  # Check every minute
        priority=CachePriority.HIGH,
    ),
    "context:deps:*": CachePolicy(
        cache_tiers=[CacheTier.MEMORY, CacheTier.DISK],
        invalidation_strategy=InvalidationStrategy.FILE_WATCH,
        ttl=None,  # Invalidate based on file changes only
        file_watching=True,
        polling_fallback=True,
        force_scan_interval=60,  # Check every minute
        priority=CachePriority.HIGH,
    ),
}


class ContextCacheManager:
    """
    Cache manager specifically for context scanner operations.

    Provides security-aware caching that integrates with the existing
    CentralizedCacheManager while adding context-specific functionality.
    """

    def __init__(self, cache_manager, filesystem_access: IFileSystemAccess):
        """
        Initialize context cache manager.

        Args:
            cache_manager: Existing CentralizedCacheManager instance
            filesystem_access: IFileSystemAccess for file operations
        """
        self.cache_manager = cache_manager
        self.filesystem_access = filesystem_access
        self.security_manager = filesystem_access.security_manager

        # Initialize filtering for gitignore support
        self.filter_engine = create_filter(
            respect_gitignore=True,
            use_ai_attributes=True,
            default_include=False,
        )

        # Register our cache policies
        self._register_context_policies()

    def _register_context_policies(self):
        """Register context-specific cache policies."""
        for pattern, policy in CONTEXT_CACHE_POLICIES.items():
            self.cache_manager.cache_policies[pattern] = policy
            logger.debug(f"Registered context cache policy: {pattern}")

    def _validate_path(self, path: str) -> Path:
        """Validate path is within security boundaries."""
        try:
            return self.security_manager.safe_resolve(path)
        except Exception as e:
            logger.error(f"Path validation failed for {path}: {e}")
            raise

    def get_module_context(self, module_path: str) -> Optional[Dict[str, Any]]:
        """Get cached module context."""
        try:
            # Validate path first
            validated_path = self._validate_path(module_path)
            relative_path = validated_path.relative_to(self.security_manager.get_allowed_roots()[0])

            cache_key = make_cache_key("module", path=str(relative_path))
            return self.cache_manager.get(cache_key)

        except Exception as e:
            logger.error(f"Failed to get module context for {module_path}: {e}")
            return None

    async def set_module_context(
        self,
        module_path: str,
        context_data: Dict[str, Any],
        file_dependencies: Optional[List[Path]] = None,
    ) -> bool:
        """Cache module context with file dependencies using security-validated enumeration."""
        try:
            # Validate path first
            validated_path = self._validate_path(module_path)
            relative_path = validated_path.relative_to(self.security_manager.get_allowed_roots()[0])

            cache_key = make_cache_key("module", path=str(relative_path))

            # Set up file dependencies if provided
            deps = file_dependencies or []
            if validated_path.is_dir():
                # Use filtered enumeration with gitignore support
                try:
                    # Get all files first using safe_glob
                    all_files = await self.filesystem_access.safe_glob(
                        validated_path, "*", recursive=True
                    )
                    all_files = [p for p in all_files if p.is_file()]

                    # Filter using the hierarchical filter with gitignore support
                    filtered_files = await self.filter_engine.filter_file_list(
                        all_files, validated_path
                    )

                    # Add security validation
                    for file_path, _reason in filtered_files:
                        if self.security_manager.is_path_allowed(file_path):
                            deps.append(file_path)
                except Exception as e:
                    logger.warning(f"Could not enumerate files in {validated_path}: {e}")

            return self.cache_manager.set(
                cache_key, context_data, file_dependencies=deps, tags={"context", "module"}
            )

        except Exception as e:
            logger.error(f"Failed to set module context for {module_path}: {e}")
            return False

    def get_breadth_summary(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cached breadth-first summary."""
        try:
            validated_path = self._validate_path(path)
            relative_path = validated_path.relative_to(self.security_manager.get_allowed_roots()[0])

            cache_key = make_cache_key("breadth", path=str(relative_path))
            return self.cache_manager.get(cache_key)

        except Exception as e:
            logger.error(f"Failed to get breadth summary for {path}: {e}")
            return None

    def set_breadth_summary(
        self,
        path: str,
        summary_data: Dict[str, Any],
        file_dependencies: Optional[List[Path]] = None,
    ) -> bool:
        """Cache breadth-first summary."""
        try:
            validated_path = self._validate_path(path)
            relative_path = validated_path.relative_to(self.security_manager.get_allowed_roots()[0])

            cache_key = make_cache_key("breadth", path=str(relative_path))

            return self.cache_manager.set(
                cache_key,
                summary_data,
                file_dependencies=file_dependencies or [],
                tags={"context", "breadth"},
            )

        except Exception as e:
            logger.error(f"Failed to set breadth summary for {path}: {e}")
            return False

    def get_project_summary(self, key: str = "overview") -> Optional[Dict[str, Any]]:
        """Get cached project-wide summary."""
        cache_key = make_cache_key("project", key=key)
        return self.cache_manager.get(cache_key)

    def set_project_summary(self, data: Dict[str, Any], key: str = "overview") -> bool:
        """Cache project-wide summary."""
        cache_key = make_cache_key("project", key=key)
        return self.cache_manager.set(cache_key, data, tags={"context", "project"})

    def get_module_metadata(self, module_path: str) -> Optional[Dict[str, Any]]:
        """Get cached module metadata."""
        try:
            validated_path = self._validate_path(module_path)
            relative_path = validated_path.relative_to(self.security_manager.get_allowed_roots()[0])

            cache_key = make_cache_key("metadata", path=str(relative_path))
            return self.cache_manager.get(cache_key)

        except Exception as e:
            logger.error(f"Failed to get module metadata for {module_path}: {e}")
            return None

    def set_module_metadata(self, module_path: str, metadata: Dict[str, Any]) -> bool:
        """Cache module metadata."""
        try:
            validated_path = self._validate_path(module_path)
            relative_path = validated_path.relative_to(self.security_manager.get_allowed_roots()[0])

            cache_key = make_cache_key("metadata", path=str(relative_path))

            return self.cache_manager.set(cache_key, metadata, tags={"context", "metadata"})

        except Exception as e:
            logger.error(f"Failed to set module metadata for {module_path}: {e}")
            return False

    def invalidate_module(self, module_path: str) -> bool:
        """Invalidate all cached data for a module."""
        try:
            validated_path = self._validate_path(module_path)
            relative_path = validated_path.relative_to(self.security_manager.get_allowed_roots()[0])

            path_str = str(relative_path)

            # Invalidate all cache types for this module
            keys_to_invalidate = [
                make_cache_key("module", path=path_str),
                make_cache_key("breadth", path=path_str),
                make_cache_key("metadata", path=path_str),
                make_cache_key("deps", path=path_str),
            ]

            success = True
            for key in keys_to_invalidate:
                if not self.cache_manager.invalidate(key):
                    success = False

            return success

        except Exception as e:
            logger.error(f"Failed to invalidate module {module_path}: {e}")
            return False

    def invalidate_project(self) -> bool:
        """Invalidate all project-level cached data."""
        # Clear ALL context-related cache patterns, not just project-level
        invalidated_count = 0
        patterns = [
            "context:project:*",
            "context:module:*",
            "context:breadth:*",
            "context:metadata:*",
            "context:dependencies:*",
            "templates:*",  # Also clear template caches that might be stale
        ]

        for pattern in patterns:
            invalidated_count += self.cache_manager.invalidate_pattern(pattern)

        logger.info(f"Invalidated {invalidated_count} cache entries across all context patterns")
        return invalidated_count > 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for context operations."""
        stats = self.cache_manager.get_stats()

        # Add context-specific stats
        context_keys = self.cache_manager.list_keys("context:*")
        stats["context"] = {
            "total_keys": len(context_keys),
            "module_keys": len([k for k in context_keys if k.startswith("context:module:")]),
            "breadth_keys": len([k for k in context_keys if k.startswith("context:breadth:")]),
            "project_keys": len([k for k in context_keys if k.startswith("context:project:")]),
            "metadata_keys": len([k for k in context_keys if k.startswith("context:metadata:")]),
        }

        return stats


def create_context_cache_manager(
    cache_manager, filesystem_access: IFileSystemAccess
) -> ContextCacheManager:
    """
    Factory function to create a context cache manager.

    Args:
        cache_manager: Existing CentralizedCacheManager
        filesystem_access: IFileSystemAccess for file operations

    Returns:
        ContextCacheManager instance
    """
    return ContextCacheManager(cache_manager, filesystem_access)
