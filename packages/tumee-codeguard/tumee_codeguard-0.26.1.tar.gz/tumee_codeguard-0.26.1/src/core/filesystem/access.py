"""
Shared filesystem access layer with MCP roots security enforcement.

This module provides a centralized filesystem access service that enforces
security boundaries for all filesystem operations across CodeGuard components.
"""

import hashlib
import platform
from functools import lru_cache
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Set, Tuple, Union

import pathspec

from ..interfaces import IFileSystemAccess, ISecurityManager
from ..language.config import is_ai_ownership_file, is_system_exclude_directory
from ..types import SecurityError
from .async_path import AsyncPath


@lru_cache(maxsize=256)
def _compile_gitignore_pathspec_cached(
    patterns_hash: str, patterns_tuple: Tuple[str, ...]
) -> Optional[pathspec.PathSpec]:
    """Cached PathSpec compilation for gitignore patterns.

    Args:
        patterns_hash: Hash of the patterns for cache key
        patterns_tuple: Tuple of gitignore patterns (tuples are hashable)

    Returns:
        Compiled PathSpec object or None if no patterns
    """
    if not patterns_tuple:
        return None
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns_tuple)


def _get_gitignore_patterns_hash(patterns: List[str]) -> str:
    """Get hash of gitignore patterns for caching."""
    content = "\n".join(sorted(patterns))  # Sort for consistent hashing
    return hashlib.sha1(content.encode("utf-8")).hexdigest()


def get_home_level_excludes() -> Set[str]:
    """
    Get a set of directory names that should be excluded when found
    directly in the user's home directory.

    Returns a set of folder names (not paths) to exclude.
    """
    system = platform.system().lower()

    # OS-specific excludes (visible directories only)
    if system == "darwin":  # macOS
        os_excludes = {
            "Library",
            "Pictures",
            "Music",
            "Movies",
            "Downloads",
            "Desktop",
            "Documents",
            "Public",
            "Applications",
        }
    elif system == "windows":
        os_excludes = {
            "AppData",
            "Application Data",
            "Local Settings",
            "My Documents",
            "My Pictures",
            "My Music",
            "My Videos",
            "Downloads",
            "Desktop",
            "OneDrive",
            "iCloudDrive",
            "Dropbox",
            "NTUSER.DAT",
            "ntuser.dat.LOG1",
            "ntuser.dat.LOG2",
            "UsrClass.dat",
        }
    else:  # Linux and other Unix-like systems
        os_excludes = {
            "snap",
            "Downloads",
            "Desktop",
            "Documents",
            "Pictures",
            "Music",
            "Videos",
            "Public",
            "Templates",
        }

    return os_excludes


def should_exclude_from_home(item_path: Path, user_home: Path) -> bool:
    """
    Check if a directory should be excluded when scanning the user's home directory.

    Args:
        item_path: Path to the item being checked
        user_home: Path to the user's home directory

    Returns:
        True if the item should be excluded, False otherwise
    """
    # Only apply home-level excludes if we're directly in the home directory
    if item_path.parent != user_home:
        return False

    folder_name = item_path.name

    # Exclude any directory starting with a dot (hidden directories)
    if folder_name.startswith("."):
        return True

    # Exclude OS-specific directories
    return folder_name in get_home_level_excludes()


class FileSystemAccess(IFileSystemAccess):
    """
    Centralized filesystem access service with MCP roots security enforcement.

    This class provides secure filesystem operations that respect the configured
    root boundaries. All CodeGuard components should use this class instead of
    direct filesystem access to ensure security compliance.
    """

    def __init__(self, security_manager: ISecurityManager):
        """
        Initialize filesystem access with security manager.

        Args:
            security_manager: ISecurityManager for boundary enforcement
        """
        self.security_manager = security_manager

    # Async methods for filesystem operations
    async def safe_file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists within security boundaries."""
        try:
            validated_path = self.security_manager.validate_file_access(file_path)
            async_path = AsyncPath(validated_path)
            return await async_path.exists() and await async_path.is_file()
        except SecurityError:
            return False

    async def safe_directory_exists(self, directory_path: Union[str, Path]) -> bool:
        """Check if directory exists within security boundaries."""
        try:
            validated_path = self.security_manager.validate_directory_access(directory_path)
            async_path = AsyncPath(validated_path)
            return await async_path.exists() and await async_path.is_dir()
        except SecurityError:
            return False

    def get_traversal_boundary(self, path: Union[str, Path]) -> Optional[Path]:
        """
        Get the security boundary for upward traversal from a path.

        Args:
            path: Path to get boundary for

        Returns:
            Path representing the boundary, or None if path not allowed
        """
        return self.security_manager.get_traversal_boundary(path)

    def validate_file_access(self, file_path: Union[str, Path]) -> Path:
        """
        Validate file access and return resolved path.

        Args:
            file_path: File path to validate

        Returns:
            Validated and resolved Path object

        Raises:
            SecurityError: If file access is not allowed
        """
        return self.security_manager.validate_file_access(file_path)

    def validate_directory_access(self, directory_path: Union[str, Path]) -> Path:
        """
        Validate directory access and return resolved path.

        Args:
            directory_path: Directory path to validate

        Returns:
            Validated and resolved Path object

        Raises:
            SecurityError: If directory access is not allowed
        """
        return self.security_manager.validate_directory_access(directory_path)

    def is_path_allowed(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is within allowed security boundaries.

        Args:
            path: Path to check

        Returns:
            True if path is allowed, False otherwise
        """
        return self.security_manager.is_path_allowed(path)

    def get_allowed_roots(self) -> List[Path]:
        """
        Get list of allowed root directories.

        Returns:
            List of allowed root Path objects
        """
        return self.security_manager.get_allowed_roots()

    # Async methods for async/await operations

    async def safe_read_file(self, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        Async version of safe_read_file.

        Args:
            file_path: Path to file to read
            encoding: File encoding (default: utf-8)

        Returns:
            File contents as string

        Raises:
            SecurityError: If file access is not allowed
            OSError: If file cannot be read
        """
        validated_path = self.security_manager.validate_file_access(file_path)
        async_path = AsyncPath(validated_path)

        try:
            return await async_path.read_text(encoding=encoding)
        except (OSError, PermissionError) as e:
            raise OSError(f"Cannot read file {validated_path}: {e}")

    async def safe_list_directory(self, directory_path: Union[str, Path]) -> List[Path]:
        """
        Async version of safe_list_directory.

        Args:
            directory_path: Directory to list

        Returns:
            List of Path objects for directory contents

        Raises:
            SecurityError: If directory access is not allowed
            OSError: If directory cannot be read
        """
        validated_path = self.security_manager.validate_directory_access(directory_path)
        async_path = AsyncPath(validated_path)

        try:
            items = []
            async for item in async_path.iterdir():
                items.append(Path(item))
            return items
        except (OSError, PermissionError) as e:
            raise OSError(f"Cannot read directory {validated_path}: {e}")

    async def safe_glob_yield(
        self,
        directory_path: Union[str, Path],
        pattern: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        respect_gitignore: bool = True,
        respect_ai_boundaries: bool = True,
        include_files: bool = True,
    ) -> AsyncGenerator[Path, None]:
        """
        Enhanced async version of safe_glob with additional filtering options, yielding results.

        Args:
            directory_path: Directory to search in
            pattern: Glob pattern to match
            recursive: Whether to search recursively
            max_depth: Maximum depth to search (None for unlimited)
            respect_gitignore: Whether to respect .gitignore patterns
            respect_ai_boundaries: Whether to respect .ai-attributes boundaries (default: True)
            include_files: Whether to include files in results (default: True)

        Yields:
            Path objects for each matching file/directory

        Raises:
            SecurityError: If directory access is not allowed
        """
        validated_path = self.security_manager.validate_directory_access(directory_path)

        # Create temporary gitignore cache for this glob operation
        gitignore_cache = {} if respect_gitignore else None

        if recursive:
            async for result in self._safe_recursive_glob_yield(
                validated_path,
                pattern,
                max_depth,
                respect_gitignore,
                gitignore_cache,
                respect_ai_boundaries,
                include_files,
            ):
                yield result
        else:
            # Handle non-recursive case by yielding filtered results
            async_path = AsyncPath(validated_path)
            results = []
            async for item in async_path.glob(pattern):
                results.append(Path(item))

            # Apply filtering for non-recursive case and yield results
            for file_path in results:
                # Filter by file type if include_files is False
                if not include_files and file_path.is_file():
                    continue

                # Apply gitignore filtering
                if respect_gitignore and self._is_git_filtered(
                    file_path, validated_path, respect_gitignore, gitignore_cache
                ):
                    continue

                yield file_path

    async def safe_glob(
        self,
        directory_path: Union[str, Path],
        pattern: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        respect_gitignore: bool = True,
        respect_ai_boundaries: bool = True,
        include_files: bool = True,
    ) -> List[Path]:
        """
        Enhanced async version of safe_glob with additional filtering options.

        Args:
            directory_path: Directory to search in
            pattern: Glob pattern to match
            recursive: Whether to search recursively
            max_depth: Maximum depth to search (None for unlimited)
            respect_gitignore: Whether to respect .gitignore patterns
            respect_ai_boundaries: Whether to respect .ai-attributes boundaries (default: True)
            include_files: Whether to include files in results (default: True)

        Returns:
            List of matching Path objects

        Raises:
            SecurityError: If directory access is not allowed
        """
        results = []
        async for path in self.safe_glob_yield(
            directory_path,
            pattern,
            recursive,
            max_depth,
            respect_gitignore,
            respect_ai_boundaries,
            include_files,
        ):
            results.append(path)
        return results

    async def _safe_recursive_glob_yield(
        self,
        base_path: Path,
        pattern: str,
        max_depth: Optional[int],
        respect_gitignore: bool,
        gitignore_cache: Optional[dict],
        respect_ai_boundaries: bool,
        include_files: bool,
    ) -> AsyncGenerator[Path, None]:
        """
        Perform recursive globbing level by level to respect boundaries, yielding results.

        Args:
            base_path: Base directory to start from
            pattern: Glob pattern to match
            max_depth: Maximum depth to traverse (None for unlimited)
            respect_gitignore: Whether to respect .gitignore patterns
            gitignore_cache: Cache for gitignore patterns
            respect_ai_boundaries: Whether to respect AI ownership boundaries
            include_files: Whether to include files in results

        Yields:
            Path objects for each matching file/directory
        """
        current_level = [base_path]
        current_depth = 0
        user_home = Path.home()  # Cache home path for efficiency

        while current_level and (max_depth is None or current_depth <= max_depth):
            next_level = []

            for directory in current_level:
                # Check if we can access this directory
                if not self.security_manager.is_path_allowed(directory):
                    continue

                try:
                    # Only apply AI boundary logic if respect_ai_boundaries is True
                    if (
                        respect_ai_boundaries
                        and is_ai_ownership_file(directory)
                        and not self._is_git_filtered(
                            directory, base_path, respect_gitignore, gitignore_cache
                        )
                    ):
                        if include_files:
                            # Yield only ai-owner file, no other module contents
                            ai_results = self._handle_ai_ownership_directory(
                                directory, pattern, ai_only=True
                            )
                            for result in ai_results:
                                yield result
                        else:
                            # Yield the directory itself but don't traverse into it
                            yield directory
                        continue  # Don't traverse deeper in either case

                    # Get all items in current directory
                    async_dir = AsyncPath(directory)
                    items = []
                    async for item in async_dir.iterdir():
                        items.append(Path(item))

                    for item in items:
                        # Apply pattern matching
                        if item.match(pattern):
                            # Check system exclusions first (highest priority)
                            if item.is_dir() and is_system_exclude_directory(item):
                                continue  # Skip system directories completely

                            # Check home directory exclusions (for user home folder only)
                            if item.is_dir() and should_exclude_from_home(item, user_home):
                                continue  # Skip home-level excluded directories

                            # Filter by file type if include_files is False
                            if not include_files and item.is_file():
                                continue

                            # Check if this file should be included (not gitignored)
                            if not respect_gitignore or not self._is_git_filtered(
                                item, item.parent, respect_gitignore, gitignore_cache
                            ):
                                yield item

                        # If it's a directory, add to next level for traversal
                        if item.is_dir():
                            # Check if we should traverse into this directory
                            if self._should_traverse_directory(
                                item, respect_gitignore, base_path, gitignore_cache
                            ):
                                next_level.append(item)

                except (OSError, PermissionError):
                    # Skip directories we can't access
                    continue

            current_level = next_level
            current_depth += 1

    def _handle_ai_ownership_directory(
        self, directory: Path, pattern: str, ai_only: bool = False
    ) -> List[Path]:
        """
        Handle AI ownership directory - return module contents and/or ai-owner file.

        Args:
            directory: AI ownership directory
            pattern: Glob pattern to match
            ai_only: If True, return only ai-owner files; if False, return all matching files

        Returns:
            List of matching files including ai-owner file
        """
        results = []

        try:
            for item in directory.iterdir():
                # Check if this is an ai-owner file using the proper function
                if is_ai_ownership_file(item):
                    results.append(item)
                # Include other files that match the pattern only if not ai_only
                elif not ai_only and item.match(pattern):
                    results.append(item)
        except (OSError, PermissionError):
            pass

        return results

    def _should_traverse_directory(
        self,
        directory: Path,
        respect_gitignore: bool,
        base_path: Path,
        gitignore_cache: Optional[dict],
    ) -> bool:
        """
        Determine if we should traverse into a directory based on filtering rules.

        Args:
            directory: Directory to check
            respect_gitignore: Whether to respect .gitignore patterns
            base_path: Base path for relative calculations

        Returns:
            True if directory should be traversed
        """
        # Check system exclusions first (highest priority)
        if is_system_exclude_directory(directory):
            return False

        # Basic security check
        if not self.security_manager.is_path_allowed(directory):
            return False

        # Check gitignore if requested
        if respect_gitignore:
            # If directory would be filtered by gitignore, don't traverse it
            filtered = self._filter_gitignore([directory], base_path, gitignore_cache)
            if not filtered:
                return False

        return True

    def _is_git_filtered(
        self, path: Path, base_path: Path, respect_gitignore: bool, gitignore_cache: Optional[dict]
    ) -> bool:
        """
        Check if a path would be filtered by gitignore.

        Args:
            path: Path to check
            base_path: Base path for gitignore lookup
            respect_gitignore: Whether gitignore filtering is enabled

        Returns:
            True if path would be filtered out
        """
        if not respect_gitignore:
            return False

        filtered = self._filter_gitignore([path], base_path, gitignore_cache)
        return len(filtered) == 0

    def _filter_gitignore(
        self, paths: List[Path], base_path: Path, gitignore_cache: Optional[dict] = None
    ) -> List[Path]:
        """
        Filter paths based on .gitignore patterns.

        Args:
            paths: List of paths to filter
            base_path: Base directory to search for .gitignore files

        Returns:
            Filtered list of paths
        """
        gitignore_patterns = []

        # Look for .gitignore files up the directory tree
        current_path = base_path
        while current_path != current_path.parent:
            gitignore_file = current_path / ".gitignore"
            if gitignore_file.exists() and gitignore_file.is_file():
                gitignore_file_str = str(gitignore_file)

                # Check cache first
                if gitignore_cache is not None and gitignore_file_str in gitignore_cache:
                    cached_patterns = gitignore_cache[gitignore_file_str]
                    if cached_patterns is not None:  # None means file was unreadable
                        gitignore_patterns.extend(cached_patterns)
                else:
                    # Read and cache the file
                    try:
                        with open(gitignore_file, "r", encoding="utf-8") as f:
                            file_patterns = f.read().splitlines()
                            gitignore_patterns.extend(file_patterns)
                            # Cache the patterns if caching is enabled
                            if gitignore_cache is not None:
                                gitignore_cache[gitignore_file_str] = file_patterns
                    except (OSError, UnicodeDecodeError):
                        # Cache that this file is unreadable
                        if gitignore_cache is not None:
                            gitignore_cache[gitignore_file_str] = None
            current_path = current_path.parent

        if not gitignore_patterns:
            return paths

        # Create pathspec from patterns using LRU cache
        patterns_hash = _get_gitignore_patterns_hash(gitignore_patterns)
        spec = _compile_gitignore_pathspec_cached(patterns_hash, tuple(gitignore_patterns))
        if spec is None:
            return paths

        # Filter paths
        filtered_paths = []
        for path in paths:
            try:
                relative_path = path.relative_to(base_path)
                if not spec.match_file(str(relative_path)):
                    filtered_paths.append(path)
            except ValueError:
                # Skip paths that can't be made relative
                filtered_paths.append(path)

        return filtered_paths

    async def safe_traverse_upward(
        self, start_path: Union[str, Path]
    ) -> AsyncGenerator[Path, None]:
        """
        Async generator version of safe_traverse_upward.

        Args:
            start_path: Starting path for upward traversal

        Yields:
            Path objects for each directory in the upward traversal

        Raises:
            SecurityError: If start_path is not within allowed boundaries
        """
        # Validate starting path
        validated_start = self.security_manager.validate_directory_access(start_path)

        # Get the traversal boundary (root boundary for this path)
        boundary = self.security_manager.get_traversal_boundary(validated_start)
        if boundary is None:
            raise SecurityError(f"Cannot determine traversal boundary for {validated_start}")

        current_dir = validated_start

        while True:
            yield current_dir

            # Stop if we've reached the boundary
            if current_dir == boundary:
                break

            # Move up to parent directory
            parent = current_dir.parent

            # Stop if we've reached filesystem root (safety check)
            if parent == current_dir:
                break

            # Validate we can access the parent directory
            try:
                # Check that parent is still within our security boundaries
                if not self.security_manager.is_path_allowed(parent):
                    break

                # Try to access parent directory (async)
                async_parent = AsyncPath(parent)
                if await async_parent.exists():
                    current_dir = parent
                else:
                    break
            except (OSError, PermissionError):
                # Can't access parent directory, stop traversal
                break

    async def walk_directory(
        self, directory_path: Union[str, Path], include_files: bool = True
    ) -> AsyncGenerator[Path, None]:
        """
        Async generator that recursively walks through a directory tree.

        Args:
            directory_path: Root directory to walk through
            include_files: Whether to include files in the results (default: True)

        Yields:
            Path objects for each file and/or directory found in the directory tree

        Raises:
            SecurityError: If directory access is not allowed
        """
        validated_path = self.security_manager.validate_directory_access(directory_path)

        async def walk_recursive(path: Path):
            try:
                async_path = AsyncPath(path)
                items = []
                async for item in async_path.iterdir():
                    items.append(Path(item))
                for item in items:
                    if item.is_file() and include_files:
                        yield item
                    elif item.is_dir() and self.security_manager.is_path_allowed(item):
                        # Always yield directories
                        yield item
                        # Recurse into subdirectories
                        async for subitem in walk_recursive(item):
                            yield subitem
            except (OSError, PermissionError):
                # Skip directories we can't access
                pass

        async for item in walk_recursive(validated_path):
            yield item
