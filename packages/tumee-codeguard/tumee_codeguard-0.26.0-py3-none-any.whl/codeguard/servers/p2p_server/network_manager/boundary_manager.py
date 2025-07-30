"""
Boundary Manager for P2P Network

Handles boundary discovery, caching, and monitoring functionality.
Extracted from DiscoveryManager to isolate boundary management concerns.
"""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ....core.console_shared import CONSOLE, cprint
from ....core.filesystem.path_utils import expand_path_for_io, normalize_path_for_storage
from ....core.interfaces import ICacheManager, IFileSystemAccess
from ....core.project.boundary_discovery import discover_managed_boundaries
from ....utils.logging_config import get_logger
from ..config import P2PConfig

logger = get_logger(__name__)


class BoundaryManager:
    """Manages boundary discovery, caching, and monitoring for managed paths."""

    def __init__(
        self,
        config: P2PConfig,
        managed_paths: List[str],
        filesystem_access: Optional[IFileSystemAccess] = None,
        cache_manager: Optional[ICacheManager] = None,
    ):
        """Initialize boundary manager."""
        self.config = config
        self.managed_paths = managed_paths
        self.filesystem_access = filesystem_access
        self.cache_manager = cache_manager

        # Boundary storage: root_path -> boundary objects
        self.boundaries: Dict[str, List[Dict]] = {}

    async def discover_boundaries(self) -> Dict[str, List[Dict]]:
        """Discover boundaries for all managed paths using injected filesystem access."""
        # Monitors don't have managed paths, so skip boundary discovery
        if not self.managed_paths:
            logger.debug("No managed paths - skipping boundary discovery (likely a monitor)")
            return {}

        if not self.filesystem_access:
            raise RuntimeError(
                "filesystem_access is required for boundary discovery but was not provided. "
                "This is a critical bug in the P2P server initialization."
            )

        try:
            # Try to load boundaries from cache first if cache manager is available
            if self.cache_manager and self.config.boundary_cache_enabled:
                cached_boundaries = await self._load_boundaries_from_cache()
                if cached_boundaries:
                    self.boundaries = cached_boundaries
                    cprint(
                        f"🚀 Loaded boundaries from cache for {len(self.boundaries)} paths",
                        mode=CONSOLE.VERBOSE,
                    )
                    return self.boundaries

            # Discover boundaries for each managed path
            for root_path in self.managed_paths:
                try:
                    cprint(
                        f"🔍 DISCOVERY: Starting boundary discovery for {root_path}",
                        mode=CONSOLE.VERBOSE,
                    )
                    discovery_result = await discover_managed_boundaries(
                        root_path, self.filesystem_access
                    )

                    # Convert boundary objects to dictionaries for serialization
                    boundaries_list = []

                    def add_boundaries_with_normalization(boundaries, boundary_type_icon):
                        """Helper to add boundaries with path normalization and logging."""
                        for boundary in boundaries:
                            boundary_dict = boundary.to_dict()
                            # Normalize path to ~username/ format for network transmission
                            boundary_dict["path"] = normalize_path_for_storage(
                                boundary_dict["path"]
                            )
                            boundaries_list.append(boundary_dict)
                            cprint(
                                f"  {boundary_type_icon} {boundary_dict['path']}",
                                mode=CONSOLE.VERBOSE,
                            )

                    # Add AI-OWNER boundaries
                    add_boundaries_with_normalization(
                        discovery_result.ai_owners_to_launch, "✅ AI-OWNER:"
                    )

                    # Add child repository boundaries
                    add_boundaries_with_normalization(
                        discovery_result.child_repositories, "📁 Repository:"
                    )

                    self.boundaries[root_path] = boundaries_list
                    cprint(
                        f"🔍 DISCOVERY: Found {len(boundaries_list)} boundaries for {root_path}",
                        mode=CONSOLE.VERBOSE,
                    )
                    logger.debug(f"Discovered {len(boundaries_list)} boundaries for {root_path}")

                except Exception as e:
                    cprint(f"❌ DISCOVERY ERROR for {root_path}: {e}")
                    logger.debug(f"Error discovering boundaries for {root_path}: {e}")
                    self.boundaries[root_path] = []

        except Exception as e:
            cprint(f"❌ DISCOVERY GENERAL ERROR: {e}")
            logger.debug(f"Error in boundary discovery: {e}")
            # Initialize empty boundaries for all paths
            for root_path in self.managed_paths:
                self.boundaries[root_path] = []

        # Save discovered boundaries to cache if cache manager is available
        if self.cache_manager and self.config.boundary_cache_enabled:
            await self._save_boundaries_to_cache()

        return self.boundaries

    def get_boundaries(self) -> Dict[str, List[Dict]]:
        """Get discovered boundaries keyed by managed path."""
        return self.boundaries.copy()

    def _get_cache_key(self, root_path: str) -> str:
        """Generate a consistent cache key for a root path."""
        # Use the expanded absolute path to ensure consistency
        expanded_path = expand_path_for_io(root_path)
        path_hash = hashlib.sha256(expanded_path.encode()).hexdigest()[:16]
        return f"boundaries:path:{path_hash}:{root_path}"

    async def _load_boundaries_from_cache(self) -> Optional[Dict[str, List[Dict]]]:
        """Load boundaries from cache."""
        if not self.cache_manager:
            return None

        try:
            boundaries = {}
            for root_path in self.managed_paths:
                cache_key = self._get_cache_key(root_path)
                cached_data = self.cache_manager.get(cache_key)
                if cached_data is not None:
                    boundaries[root_path] = cached_data
                    logger.debug(f"Cache hit for boundaries: {cache_key}")
                else:
                    logger.debug(f"Cache miss for boundaries: {cache_key}")
                    return None  # If any path is missing, do full discovery

            return boundaries

        except Exception as e:
            logger.debug(f"Error loading boundaries from cache: {e}")
            return None

    async def _save_boundaries_to_cache(self) -> None:
        """Save boundaries to cache with file dependencies."""
        if not self.cache_manager:
            return

        try:
            for root_path, boundary_list in self.boundaries.items():
                cache_key = self._get_cache_key(root_path)

                # Collect actual boundary file paths as dependencies
                file_dependencies = []
                for boundary in boundary_list:
                    boundary_path = boundary.get("path", "")
                    if boundary_path:
                        boundary_path_obj = Path(boundary_path).expanduser()
                        if boundary_path_obj.exists():
                            file_dependencies.append(boundary_path_obj)

                # Cache the boundary data with actual file dependencies
                self.cache_manager.set(
                    key=cache_key,
                    value=boundary_list,
                    file_dependencies=file_dependencies,
                    tags={"boundaries", f"path:{root_path}"},
                )

                logger.debug(
                    f"Cached boundaries for {cache_key} with {len(file_dependencies)} file dependencies"
                )

        except Exception as e:
            logger.error(f"Error saving boundaries to cache: {e}")

    def invalidate_boundary_cache(self) -> None:
        """Invalidate boundary cache for this node."""
        if not self.cache_manager:
            return

        try:
            # Invalidate all boundary cache entries for this path
            for root_path in self.managed_paths:
                cache_key = self._get_cache_key(root_path)
                self.cache_manager.invalidate(cache_key)
                logger.debug(f"Invalidated boundary cache: {cache_key}")

        except Exception as e:
            logger.error(f"Error invalidating boundary cache: {e}")

    async def monitor_boundary_cache(
        self,
        task_shutdown_event: asyncio.Event,
        shutdown_event: asyncio.Event,
        boundary_change_callback: Optional[Callable] = None,
    ) -> None:
        """Monitor boundary cache for invalidation and trigger rediscovery."""
        if not self.cache_manager or not self.config.boundary_cache_enabled:
            logger.debug("Boundary monitoring disabled - no cache manager or cache disabled")
            return

        logger.debug("Starting boundary cache monitoring")

        try:
            # Track last known cache state
            last_boundary_check = time.time()

            while not task_shutdown_event.is_set() and not shutdown_event.is_set():
                try:
                    current_time = time.time()

                    # Check every 30 seconds (configurable via boundary_debounce_interval)
                    if current_time - last_boundary_check >= self.config.boundary_debounce_interval:
                        boundaries_changed = await self._check_boundary_cache_validity()

                        if boundaries_changed:
                            cprint("🔄 Boundary cache invalidated - rediscovering boundaries")

                            # Rediscover boundaries
                            await self.discover_boundaries()

                            # Notify callback if provided
                            if boundary_change_callback:
                                await boundary_change_callback()

                        last_boundary_check = current_time

                    # Check shutdown every second
                    await asyncio.sleep(1.0)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.debug(f"Boundary monitor error: {e}")
                    await asyncio.sleep(1.0)

        except asyncio.CancelledError:
            logger.debug("Boundary monitor task cancelled")
        except Exception as e:
            logger.error(f"Boundary monitor setup error: {e}")

    async def _check_boundary_cache_validity(self) -> bool:
        """Check if boundary cache is still valid. Returns True if boundaries changed."""
        if not self.cache_manager:
            return False

        try:
            # Check if any of our boundary cache entries are missing (invalidated)
            for root_path in self.managed_paths:
                cache_key = self._get_cache_key(root_path)
                cached_data = self.cache_manager.get(cache_key)
                if cached_data is None:
                    logger.debug(f"Boundary cache invalidated for {cache_key}")
                    return True

            return False

        except Exception as e:
            logger.debug(f"Error checking boundary cache validity: {e}")
            return True  # Assume changed on error
