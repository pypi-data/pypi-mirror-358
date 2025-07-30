"""
VCS-agnostic temporal filesystem access.

This module provides a temporal filesystem access layer that works with any VCS
through the temporal provider interface, implementing the standard IFileSystemAccess
interface for seamless integration with existing filesystem operations.
"""

from pathlib import Path
from typing import AsyncGenerator, List, Optional, Union

from ...interfaces import IFileSystemAccess, ISecurityManager
from ...language.config import is_ai_ownership_file, is_system_exclude_directory
from ...types import SecurityError
from ..async_path import AsyncPath
from .interfaces import ITemporalProvider


class TemporalFileSystemAccess:
    """
    VCS-agnostic temporal filesystem access implementing IFileSystemAccess.

    This class provides filesystem operations at a specific point in time
    (commit/revision) by delegating to a temporal provider while maintaining
    all security boundaries and AI ownership checks.
    """

    def __init__(
        self, commit_ref: str, provider: ITemporalProvider, security_manager: ISecurityManager
    ):
        """
        Initialize temporal filesystem access.

        Args:
            commit_ref: VCS-specific commit reference or "latest"
            provider: Temporal provider for VCS operations
            security_manager: Security manager for boundary enforcement
        """
        self.commit_ref = commit_ref
        self.provider = provider
        self.security_manager = security_manager

    # Async methods for filesystem operations

    async def safe_file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists at commit within security boundaries."""
        try:
            validated_path = self.security_manager.validate_file_access(file_path)
            return await self.provider.file_exists_at_commit(self.commit_ref, validated_path)
        except SecurityError:
            return False

    async def safe_directory_exists(self, directory_path: Union[str, Path]) -> bool:
        """Check if directory exists at commit within security boundaries."""
        try:
            validated_path = self.security_manager.validate_directory_access(directory_path)
            return await self.provider.directory_exists_at_commit(self.commit_ref, validated_path)
        except SecurityError:
            return False

    async def safe_list_directory(self, directory_path: Union[str, Path]) -> List[Path]:
        """
        List directory contents at commit within security boundaries.

        This method applies the same filtering logic as the native filesystem
        access but operates on the historical state of the repository.
        """
        validated_path = self.security_manager.validate_directory_access(directory_path)

        try:
            items = await self.provider.list_directory_at_commit(self.commit_ref, validated_path)

            # Apply filtering for historical directory listing
            filtered_items = []
            for item in items:
                # Check security boundaries
                if not self.security_manager.is_path_allowed(item):
                    continue

                # Check system exclusions
                if item.is_dir() and is_system_exclude_directory(item):
                    continue

                filtered_items.append(item)

            return filtered_items

        except (OSError, FileNotFoundError) as e:
            raise OSError(f"Cannot list temporal directory {validated_path}: {e}")

    async def safe_read_file(self, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read file content at commit within security boundaries."""
        validated_path = self.security_manager.validate_file_access(file_path)

        try:
            return await self.provider.read_file_at_commit(self.commit_ref, validated_path)
        except (OSError, FileNotFoundError) as e:
            raise OSError(f"Cannot read temporal file {validated_path}: {e}")

    async def safe_glob(
        self,
        directory_path: Union[str, Path],
        pattern: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        respect_gitignore: bool = False,
        respect_ai_boundaries: bool = True,
        include_files: bool = True,
    ) -> List[Path]:
        """
        Glob files at commit within security boundaries.

        Note: For temporal access, gitignore is implicitly respected since we're
        reading from VCS history. The respect_gitignore parameter is ignored.
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

    async def safe_glob_yield(
        self,
        directory_path: Union[str, Path],
        pattern: str,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        respect_gitignore: bool = False,
        respect_ai_boundaries: bool = True,
        include_files: bool = True,
    ) -> AsyncGenerator[Path, None]:
        """
        Glob files at commit within security boundaries, yielding results.

        This implementation performs recursive directory traversal at the
        historical commit state, applying pattern matching and filtering.
        """
        validated_path = self.security_manager.validate_directory_access(directory_path)

        if recursive:
            async for result in self._recursive_glob_yield(
                validated_path, pattern, max_depth, respect_ai_boundaries, include_files
            ):
                yield result
        else:
            # Non-recursive case
            try:
                items = await self.provider.list_directory_at_commit(
                    self.commit_ref, validated_path
                )
                for item in items:
                    if item.match(pattern):
                        # Apply filtering
                        if not include_files and await self._is_file_at_commit(item):
                            continue

                        # Check AI boundaries if requested
                        if respect_ai_boundaries and await self._check_ai_ownership_at_commit(item):
                            continue

                        yield item
            except (OSError, FileNotFoundError):
                # Directory doesn't exist at this commit
                pass

    async def safe_traverse_upward(
        self, start_path: Union[str, Path]
    ) -> AsyncGenerator[Path, None]:
        """
        Traverse upward through directory tree at commit within security boundaries.
        """
        validated_start = self.security_manager.validate_directory_access(start_path)
        boundary = self.security_manager.get_traversal_boundary(validated_start)

        if boundary is None:
            raise SecurityError(f"Cannot determine traversal boundary for {validated_start}")

        current_dir = validated_start

        while True:
            # Check if directory existed at this commit
            if await self.provider.directory_exists_at_commit(self.commit_ref, current_dir):
                yield current_dir

            # Stop if we've reached the boundary
            if current_dir == boundary:
                break

            # Move up to parent directory
            parent = current_dir.parent
            if parent == current_dir:  # Reached filesystem root
                break

            if not self.security_manager.is_path_allowed(parent):
                break

            current_dir = parent

    async def walk_directory(
        self, directory_path: Union[str, Path], include_files: bool = True
    ) -> AsyncGenerator[Path, None]:
        """
        Recursively walk directory tree at commit within security boundaries.
        """
        validated_path = self.security_manager.validate_directory_access(directory_path)

        async for item in self._walk_recursive(validated_path, include_files):
            yield item

    # Utility methods

    def get_traversal_boundary(self, path: Union[str, Path]) -> Optional[Path]:
        """Get the security boundary for upward traversal from a path."""
        return self.security_manager.get_traversal_boundary(path)

    def validate_file_access(self, file_path: Union[str, Path]) -> Path:
        """Validate file access and return resolved path."""
        return self.security_manager.validate_file_access(file_path)

    def validate_directory_access(self, directory_path: Union[str, Path]) -> Path:
        """Validate directory access and return resolved path."""
        return self.security_manager.validate_directory_access(directory_path)

    def is_path_allowed(self, path: Union[str, Path]) -> bool:
        """Check if a path is within allowed security boundaries."""
        return self.security_manager.is_path_allowed(path)

    def get_allowed_roots(self) -> List[Path]:
        """Get list of allowed root directories."""
        return self.security_manager.get_allowed_roots()

    # Private helper methods

    async def _recursive_glob_yield(
        self,
        base_path: Path,
        pattern: str,
        max_depth: Optional[int],
        respect_ai_boundaries: bool,
        include_files: bool,
    ) -> AsyncGenerator[Path, None]:
        """Perform recursive globbing at commit respecting boundaries."""
        current_level = [base_path]
        current_depth = 0

        while current_level and (max_depth is None or current_depth <= max_depth):
            next_level = []

            for directory in current_level:
                if not self.security_manager.is_path_allowed(directory):
                    continue

                try:
                    # Check AI ownership if requested
                    if respect_ai_boundaries and await self._check_ai_ownership_at_commit(
                        directory
                    ):
                        # Only yield AI ownership files, don't traverse deeper
                        if include_files and await self._is_ai_ownership_file_at_commit(directory):
                            yield directory
                        continue

                    # Get directory contents at commit
                    items = await self.provider.list_directory_at_commit(self.commit_ref, directory)

                    for item in items:
                        # Apply pattern matching
                        if item.match(pattern):
                            # Check system exclusions
                            if await self._is_directory_at_commit(
                                item
                            ) and is_system_exclude_directory(item):
                                continue

                            # Filter by file type if needed
                            if not include_files and await self._is_file_at_commit(item):
                                continue

                            yield item

                        # Add directories to next level for traversal
                        if await self._is_directory_at_commit(item):
                            if await self._should_traverse_directory_at_commit(item):
                                next_level.append(item)

                except (OSError, FileNotFoundError):
                    # Skip directories we can't access
                    continue

            current_level = next_level
            current_depth += 1

    async def _walk_recursive(self, path: Path, include_files: bool) -> AsyncGenerator[Path, None]:
        """Iteratively walk directory tree at commit using a stack."""
        stack = [path]

        while stack:
            current_path = stack.pop()

            if not self.security_manager.is_path_allowed(current_path):
                continue

            try:
                items = await self.provider.list_directory_at_commit(self.commit_ref, current_path)

                for item in items:
                    if await self._is_file_at_commit(item) and include_files:
                        yield item
                    elif await self._is_directory_at_commit(item):
                        yield item
                        # Add to stack for further processing
                        stack.append(item)
            except (OSError, FileNotFoundError):
                # Skip directories we can't access
                continue

    async def _is_file_at_commit(self, path: Path) -> bool:
        """Check if path was a file at commit."""
        return await self.provider.file_exists_at_commit(self.commit_ref, path)

    async def _is_directory_at_commit(self, path: Path) -> bool:
        """Check if path was a directory at commit."""
        return await self.provider.directory_exists_at_commit(self.commit_ref, path)

    async def _is_ai_ownership_file_at_commit(self, path: Path) -> bool:
        """Check if path was an AI ownership file at commit."""
        if self.commit_ref == "latest":
            return is_ai_ownership_file(path) is not None
        else:
            # For historical commits, check if it looks like an AI ownership file
            return path.name.startswith(".ai-") or "ai-owner" in path.name.lower()

    async def _check_ai_ownership_at_commit(self, path: Path) -> bool:
        """Check AI ownership boundaries at commit."""
        if self.commit_ref == "latest":
            return is_ai_ownership_file(path) is not None
        else:
            # For historical commits, we need to check historical .ai-attributes
            # This is a simplified check - could be enhanced to read historical .ai-attributes
            return await self._is_ai_ownership_file_at_commit(path)

    async def _should_traverse_directory_at_commit(self, directory: Path) -> bool:
        """Determine if we should traverse into a directory at commit."""
        # Check system exclusions
        if is_system_exclude_directory(directory):
            return False

        # Check security boundaries
        if not self.security_manager.is_path_allowed(directory):
            return False

        return True

    def _filter_gitignore(
        self, paths: List[Path], base_path: Path, gitignore_cache: Optional[dict] = None
    ) -> List[Path]:
        """
        Filter paths based on .gitignore patterns at commit.

        For temporal access, gitignore filtering is simplified since we're reading
        from VCS history - files that are in the commit were not gitignored at that time.
        However, we still provide this method for compatibility with the IFileSystemAccess interface.

        Args:
            paths: List of paths to filter
            base_path: Base directory to search for .gitignore files
            gitignore_cache: Optional cache for gitignore patterns (unused in temporal access)

        Returns:
            Filtered list of paths (for temporal access, typically returns all paths)
        """
        # For temporal access, files in the commit history were already not gitignored
        # when they were committed, so we typically don't need additional filtering.
        # However, we implement this for interface compatibility.

        if self.commit_ref == "working":
            # For working directory, we could implement full gitignore filtering
            # but for now, we'll return all paths since temporal access is primarily
            # used for historical states
            return paths
        else:
            # For historical commits, files were already filtered by git
            # when they were committed, so we return all paths
            return paths
