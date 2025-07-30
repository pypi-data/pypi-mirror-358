"""
File watching system with polling fallback for cache invalidation.

This module provides cross-platform file watching capabilities with automatic
fallback to polling when file system events are not available or reliable.
"""

import asyncio
import fnmatch
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from ..interfaces import IFileSystemAccess
from ..security.roots import RootsSecurityManager
from .access import FileSystemAccess

# Required dependency
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    watchdog = True
except ImportError:
    import sys

    from ..exit_codes import WATCHDOG_MISSING

    print("Error: watchdog library is required for file watching")
    print("Install with: pip install watchdog>=3.0.0")
    print("Or: pip install -e .")
    sys.exit(WATCHDOG_MISSING)

logger = logging.getLogger(__name__)


@dataclass
class WatchHandle:
    """Handle for file watching operations."""

    path: Path
    callback: Callable[[Path], None]
    watch_id: str

    def __post_init__(self):
        if not self.watch_id:
            self.watch_id = str(uuid.uuid4())


@dataclass
class PollingHandle(WatchHandle):
    """Handle for polling-based file watching."""

    task: Optional[asyncio.Task] = None
    interval: float = 1.0


class FileWatcherBackend(ABC):
    """Abstract interface for file watching backends."""

    @abstractmethod
    async def watch_file(self, path: Path, callback: Callable[[Path], None]) -> WatchHandle:
        """Start watching a file for changes."""
        pass

    @abstractmethod
    async def watch_directory(
        self,
        path: Path,
        callback: Callable[[Path], None],
        recursive: bool = False,
        patterns: Optional[List[str]] = None,
    ) -> WatchHandle:
        """Start watching a directory for changes."""
        pass

    @abstractmethod
    async def stop_watching(self, handle: WatchHandle) -> bool:
        """Stop watching a file or directory."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get watching statistics."""
        pass


class WatchdogBackend(FileWatcherBackend):
    """File watching backend using the watchdog library."""

    def __init__(self):
        self.observer = None
        self.handlers = {}
        self._available = None

    def is_available(self) -> bool:
        """Check if watchdog is available."""
        if self._available is not None:
            return self._available

        if FileSystemEventHandler is None or Observer is None:
            logger.warning("Watchdog library not available, falling back to polling")
            self._available = False
            return False

        self._available = True
        return True

    async def watch_file(self, path: Path, callback: Callable[[Path], None]) -> WatchHandle:
        """Watch a single file for changes."""
        if not self.is_available():
            raise RuntimeError("Watchdog backend not available")

        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, target_path: Path, callback_fn: Callable[[Path], None]):
                self.target_path = target_path.resolve()
                self.callback_fn = callback_fn

            def on_modified(self, event):
                if not event.is_directory:
                    event_path = Path(event.src_path).resolve()
                    if event_path == self.target_path:
                        try:
                            self.callback_fn(self.target_path)
                        except Exception as e:
                            logger.error(f"File watch callback error: {e}")

            def on_moved(self, event):
                if not event.is_directory:
                    # Handle file moves/renames
                    dest_path = Path(event.dest_path).resolve()
                    if dest_path == self.target_path:
                        try:
                            self.callback_fn(self.target_path)
                        except Exception as e:
                            logger.error(f"File watch callback error: {e}")

        if self.observer is None:
            self.observer = Observer()
            self.observer.start()

        handler = FileChangeHandler(path, callback)
        watch = self.observer.schedule(handler, str(path.parent), recursive=False)

        handle = WatchHandle(path=path, callback=callback, watch_id=str(id(watch)))
        self.handlers[handle.watch_id] = (watch, handler)

        return handle

    async def watch_directory(
        self,
        path: Path,
        callback: Callable[[Path], None],
        recursive: bool = False,
        patterns: Optional[List[str]] = None,
    ) -> WatchHandle:
        """Watch a directory for changes."""
        if not self.is_available():
            raise RuntimeError("Watchdog backend not available")

        class DirectoryChangeHandler(FileSystemEventHandler):
            def __init__(
                self, callback_fn: Callable[[Path], None], patterns: Optional[List[str]] = None
            ):
                self.callback_fn = callback_fn
                self.patterns = patterns or ["*"]

            def _should_process(self, file_path: Path) -> bool:
                """Check if file matches any of the patterns."""
                filename = file_path.name
                return any(fnmatch.fnmatch(filename, pattern) for pattern in self.patterns)

            def on_modified(self, event):
                if not event.is_directory:
                    file_path = Path(event.src_path)
                    if self._should_process(file_path):
                        try:
                            self.callback_fn(file_path)
                        except Exception as e:
                            logger.error(f"Directory watch callback error: {e}")

            def on_created(self, event):
                if not event.is_directory:
                    file_path = Path(event.src_path)
                    if self._should_process(file_path):
                        try:
                            self.callback_fn(file_path)
                        except Exception as e:
                            logger.error(f"Directory watch callback error: {e}")

            def on_deleted(self, event):
                if not event.is_directory:
                    file_path = Path(event.src_path)
                    if self._should_process(file_path):
                        try:
                            self.callback_fn(file_path)
                        except Exception as e:
                            logger.error(f"Directory watch callback error: {e}")

        if self.observer is None:
            self.observer = Observer()
            self.observer.start()

        handler = DirectoryChangeHandler(callback, patterns)
        watch = self.observer.schedule(handler, str(path), recursive=recursive)

        handle = WatchHandle(path=path, callback=callback, watch_id=str(id(watch)))
        self.handlers[handle.watch_id] = (watch, handler)

        return handle

    async def stop_watching(self, handle: WatchHandle) -> bool:
        """Stop watching."""
        try:
            if handle.watch_id in self.handlers:
                watch, handler = self.handlers.pop(handle.watch_id)
                if self.observer:
                    self.observer.unschedule(watch)
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping watch: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get watching statistics."""
        return {
            "backend": "watchdog",
            "active_watches": len(self.handlers),
            "observer_running": self.observer is not None and self.observer.is_alive(),
        }

    def shutdown(self):
        """Shutdown the observer."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None


class PollingBackend(FileWatcherBackend):
    """Polling-based file watching backend."""

    def __init__(self, default_interval: float = 1.0, filesystem_access: IFileSystemAccess = None):
        if filesystem_access is None:
            raise ValueError("FileSystemAccess is required for PollingBackend")
        self.default_interval = default_interval
        self.file_mtimes: Dict[Path, float] = {}
        self.polling_tasks: Dict[str, PollingHandle] = {}
        self.filesystem_access = filesystem_access

    def is_available(self) -> bool:
        """Polling is always available."""
        return True

    async def watch_file(self, path: Path, callback: Callable[[Path], None]) -> WatchHandle:
        """Start polling a file for changes."""

        async def poll_file():
            while True:
                try:
                    if path.exists():
                        current_mtime = path.stat().st_mtime
                        if path in self.file_mtimes:
                            if current_mtime != self.file_mtimes[path]:
                                self.file_mtimes[path] = current_mtime
                                try:
                                    callback(path)
                                except Exception as e:
                                    logger.error(f"Polling callback error: {e}")
                        else:
                            self.file_mtimes[path] = current_mtime
                    else:
                        # File was deleted
                        if path in self.file_mtimes:
                            del self.file_mtimes[path]
                            try:
                                callback(path)  # Notify of deletion
                            except Exception as e:
                                logger.error(f"Polling callback error: {e}")

                except Exception as e:
                    logger.error(f"Polling error for {path}: {e}")

                await asyncio.sleep(self.default_interval)

        task = asyncio.create_task(poll_file())
        handle = PollingHandle(
            path=path, callback=callback, watch_id="", task=task, interval=self.default_interval
        )
        self.polling_tasks[handle.watch_id] = handle

        return handle

    async def watch_directory(
        self,
        path: Path,
        callback: Callable[[Path], None],
        recursive: bool = False,
        patterns: Optional[List[str]] = None,
    ) -> WatchHandle:
        """Start polling a directory for changes."""

        async def get_directory_files() -> Dict[Path, float]:
            """Get all files in directory with their mtimes."""
            files = {}
            try:
                # Use safe_glob for all directory scanning with security boundaries
                file_paths = await self.filesystem_access.safe_glob(
                    path, "*", recursive=recursive, respect_gitignore=True
                )

                for file_path in file_paths:
                    if file_path.is_file():
                        # Check patterns if specified
                        if patterns:
                            if not any(
                                fnmatch.fnmatch(file_path.name, pattern) for pattern in patterns
                            ):
                                continue

                        try:
                            files[file_path] = file_path.stat().st_mtime
                        except Exception as e:
                            logger.debug(f"Error getting mtime for {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error scanning directory {path}: {e}")

            return files

        # Initialize with current state
        previous_files = await get_directory_files()

        async def poll_directory():
            nonlocal previous_files

            while True:
                try:
                    current_files = await get_directory_files()

                    # Check for new or modified files
                    for file_path, mtime in current_files.items():
                        if file_path not in previous_files or previous_files[file_path] != mtime:
                            try:
                                callback(file_path)
                            except Exception as e:
                                logger.error(f"Directory polling callback error: {e}")

                    # Check for deleted files
                    for file_path in previous_files:
                        if file_path not in current_files:
                            try:
                                callback(file_path)
                            except Exception as e:
                                logger.error(f"Directory polling callback error: {e}")

                    previous_files = current_files

                except Exception as e:
                    logger.error(f"Directory polling error for {path}: {e}")

                await asyncio.sleep(self.default_interval)

        task = asyncio.create_task(poll_directory())
        handle = PollingHandle(
            path=path, callback=callback, watch_id="", task=task, interval=self.default_interval
        )
        self.polling_tasks[handle.watch_id] = handle

        return handle

    async def stop_watching(self, handle: WatchHandle) -> bool:
        """Stop polling."""
        try:
            if isinstance(handle, PollingHandle) and handle.watch_id in self.polling_tasks:
                polling_handle = self.polling_tasks.pop(handle.watch_id)
                if polling_handle.task and not polling_handle.task.done():
                    polling_handle.task.cancel()
                    try:
                        await polling_handle.task
                    except asyncio.CancelledError:
                        pass

                # Clean up mtime tracking
                if handle.path in self.file_mtimes:
                    del self.file_mtimes[handle.path]

                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping polling: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get polling statistics."""
        return {
            "backend": "polling",
            "active_polls": len(self.polling_tasks),
            "tracked_files": len(self.file_mtimes),
            "default_interval": self.default_interval,
        }


class FileWatcherWithFallback:
    """
    Cross-platform file watching with polling fallback.
    Supports individual file and directory watching with manual scan capabilities.
    """

    def __init__(
        self,
        fallback_interval: float = 1.0,
        prefer_watchdog: bool = True,
        filesystem_access: IFileSystemAccess = None,
    ):
        if filesystem_access is None:
            raise ValueError("FileSystemAccess is required for FileWatcherWithFallback")
        self.fallback_interval = fallback_interval
        self.prefer_watchdog = prefer_watchdog

        # Initialize backends
        self.watchdog_backend = WatchdogBackend()
        self.polling_backend = PollingBackend(fallback_interval, filesystem_access)

        # Choose primary backend
        if prefer_watchdog and self.watchdog_backend.is_available():
            self.primary_backend = self.watchdog_backend
            self.fallback_backend = self.polling_backend
            logger.info("Using watchdog for file watching with polling fallback")
        else:
            self.primary_backend = self.polling_backend
            self.fallback_backend = None
            logger.info("Using polling for file watching")

        self.active_watches: Dict[str, WatchHandle] = {}
        self.file_mtimes: Dict[Path, float] = {}

    async def watch_file(self, path: Path, callback: Callable[[Path], None]) -> WatchHandle:
        """Start watching a file for changes."""
        try:
            # Try primary backend first
            handle = await self.primary_backend.watch_file(path, callback)
            self.active_watches[handle.watch_id] = handle
            logger.debug(f"Started watching file {path} with {type(self.primary_backend).__name__}")
            return handle

        except Exception as e:
            logger.warning(f"Primary backend failed for {path}, trying fallback: {e}")

            if self.fallback_backend:
                try:
                    handle = await self.fallback_backend.watch_file(path, callback)
                    self.active_watches[handle.watch_id] = handle
                    logger.debug(
                        f"Started watching file {path} with fallback {type(self.fallback_backend).__name__}"
                    )
                    return handle
                except Exception as e2:
                    logger.error(f"Fallback backend also failed for {path}: {e2}")
                    raise
            else:
                raise

    async def watch_directory(
        self,
        path: Path,
        callback: Callable[[Path], None],
        recursive: bool = False,
        patterns: Optional[List[str]] = None,
    ) -> WatchHandle:
        """Start watching a directory for changes."""
        try:
            # Try primary backend first
            handle = await self.primary_backend.watch_directory(path, callback, recursive, patterns)
            self.active_watches[handle.watch_id] = handle
            logger.debug(
                f"Started watching directory {path} with {type(self.primary_backend).__name__}"
            )
            return handle

        except Exception as e:
            logger.warning(f"Primary backend failed for directory {path}, trying fallback: {e}")

            if self.fallback_backend:
                try:
                    handle = await self.fallback_backend.watch_directory(
                        path, callback, recursive, patterns
                    )
                    self.active_watches[handle.watch_id] = handle
                    logger.debug(
                        f"Started watching directory {path} with fallback {type(self.fallback_backend).__name__}"
                    )
                    return handle
                except Exception as e2:
                    logger.error(f"Fallback backend also failed for directory {path}: {e2}")
                    raise
            else:
                raise

    async def stop_watching(self, handle: WatchHandle) -> bool:
        """Stop watching a file or directory."""
        try:
            # Determine which backend is handling this watch
            backend = None
            if isinstance(handle, PollingHandle):
                backend = self.polling_backend
            else:
                backend = self.primary_backend

            success = await backend.stop_watching(handle)

            if handle.watch_id in self.active_watches:
                del self.active_watches[handle.watch_id]

            logger.debug(f"Stopped watching {handle.path}")
            return success

        except Exception as e:
            logger.error(f"Error stopping watch for {handle.path}: {e}")
            return False

    def force_scan(self, paths: List[Path]) -> Dict[Path, bool]:
        """Manual scan for cache invalidation when watcher/polling unavailable."""
        changes = {}

        try:
            for path in paths:
                try:
                    if path.exists():
                        current_mtime = path.stat().st_mtime
                        stored_mtime = self.file_mtimes.get(path)

                        if stored_mtime is None or current_mtime != stored_mtime:
                            changes[path] = True
                            self.file_mtimes[path] = current_mtime
                        else:
                            changes[path] = False
                    else:
                        # File no longer exists
                        if path in self.file_mtimes:
                            del self.file_mtimes[path]
                            changes[path] = True
                        else:
                            changes[path] = False

                except Exception as e:
                    logger.error(f"Force scan error for {path}: {e}")
                    changes[path] = True  # Assume changed on error

            return changes

        except Exception as e:
            logger.error(f"Force scan error: {e}")
            return {path: True for path in paths}

    def get_stats(self) -> Dict[str, Any]:
        """Get file watching statistics."""
        stats = {
            "active_watches": len(self.active_watches),
            "tracked_files": len(self.file_mtimes),
            "primary_backend": self.primary_backend.get_stats(),
        }

        if self.fallback_backend:
            stats["fallback_backend"] = self.fallback_backend.get_stats()

        return stats

    async def shutdown(self):
        """Shutdown all watching operations."""
        try:
            # Stop all active watches
            for handle in list(self.active_watches.values()):
                await self.stop_watching(handle)

            # Shutdown backends
            if hasattr(self.primary_backend, "shutdown"):
                self.primary_backend.shutdown()

            if self.fallback_backend and hasattr(self.fallback_backend, "shutdown"):
                self.fallback_backend.shutdown()

            logger.info("File watcher shutdown complete")

        except Exception as e:
            logger.error(f"Error during file watcher shutdown: {e}")


# Convenience functions for common use cases
async def watch_config_file(
    path: Path, cache_manager, cache_key: str, filesystem_access: IFileSystemAccess
) -> WatchHandle:
    """Watch a configuration file and invalidate cache on changes."""

    def on_config_change(changed_path: Path):
        logger.info(f"Configuration file changed: {changed_path}")
        cache_manager.invalidate(cache_key)

    watcher = FileWatcherWithFallback(filesystem_access=filesystem_access)
    return await watcher.watch_file(path, on_config_change)


async def watch_template_directory(
    path: Path, cache_manager, cache_pattern: str, filesystem_access: IFileSystemAccess
) -> WatchHandle:
    """Watch a template directory and invalidate matching cache entries on changes."""

    def on_template_change(changed_path: Path):
        logger.info(f"Template file changed: {changed_path}")
        # Invalidate all templates matching the pattern
        cache_manager.invalidate_pattern(cache_pattern)

    watcher = FileWatcherWithFallback(filesystem_access=filesystem_access)
    return await watcher.watch_directory(
        path, on_template_change, recursive=True, patterns=["*.md", "*.txt"]
    )


async def watch_filtering_files(
    path: Path, cache_manager, filesystem_access: IFileSystemAccess
) -> WatchHandle:
    """Watch for .gitignore and .ai-attributes changes."""

    def on_filtering_change(changed_path: Path):
        logger.info(f"Filtering file changed: {changed_path}")
        # Invalidate filtering cache entries
        cache_manager.invalidate_pattern("filtering:*")

    watcher = FileWatcherWithFallback(filesystem_access=filesystem_access)
    return await watcher.watch_directory(
        path, on_filtering_change, recursive=True, patterns=[".gitignore", ".ai-attributes"]
    )
