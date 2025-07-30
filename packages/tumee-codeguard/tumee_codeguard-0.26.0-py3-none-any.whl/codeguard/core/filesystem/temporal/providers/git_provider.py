"""
Git-specific temporal provider implementation.

This module implements the ITemporalProvider interface for Git repositories,
leveraging the existing GitIntegration class for VCS operations.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Union

from .....vcs.git_integration import GitError, GitIntegration
from ...async_path import AsyncPath
from ..interfaces import ITemporalProvider


class GitTemporalProvider:
    """
    Git implementation of the temporal provider interface.

    This provider uses the existing GitIntegration class to provide
    temporal filesystem operations for Git repositories.
    """

    def __init__(self, repo_path: Optional[Union[str, Path]] = None):
        """
        Initialize Git temporal provider.

        Args:
            repo_path: Path to Git repository root. If None, uses current directory.
        """
        self.git_integration = GitIntegration(repo_path)
        self._repo_root = self.git_integration.repo_path

    async def resolve_reference(self, reference: str) -> str:
        """
        Convert human-readable reference to Git commit SHA with git- prefix.

        Args:
            reference: Human reference like "3 days ago", "v1.2.0", "working", etc.

        Returns:
            Git commit SHA prefixed with "git-" or "working" for current references
        """
        # Handle current/working references
        if reference.lower() in ("current", "latest", "head", "working", ""):
            return "working"

        # Handle direct commit SHA (already resolved)
        if self._is_commit_sha(reference):
            return f"git-{reference[:8]}"  # Short SHA with git prefix

        # Handle relative time references
        if self._is_relative_time(reference):
            timestamp = self._parse_relative_time(reference)
            commit_sha = await self._timestamp_to_commit(timestamp)
            return f"git-{commit_sha[:8]}" if commit_sha else "working"

        # Handle Git tags and branches
        try:
            commit_sha = await self._resolve_git_reference(reference)
            return f"git-{commit_sha[:8]}" if commit_sha else "working"
        except GitError:
            # If reference can't be resolved, treat as working
            return "working"

    async def read_file_at_commit(self, commit_ref: str, file_path: Path) -> str:
        """
        Read file content at specific Git commit.

        Args:
            commit_ref: Git commit SHA or "latest"
            file_path: Path to file to read

        Returns:
            File content as string
        """
        if commit_ref == "working":
            # Read current file from filesystem using async pattern
            try:
                async_path = AsyncPath(file_path)
                return await async_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as e:
                raise OSError(f"Cannot read current file {file_path}: {e}")
        elif commit_ref.startswith("git-"):
            # Extract actual commit SHA from git-{sha} format
            actual_commit = commit_ref[4:]  # Remove "git-" prefix

            # Read historical file using git show
            try:
                return await self.git_integration.get_file_content(file_path, actual_commit)
            except GitError as e:
                if "does not exist" in str(e):
                    raise FileNotFoundError(f"File {file_path} not found at commit {commit_ref}")
                raise OSError(f"Git error reading {file_path} at {commit_ref}: {e}")
        else:
            raise ValueError(
                f"Invalid commit reference for Git provider: {commit_ref}. Expected 'working' or 'git-{{sha}}'."
            )

    async def list_directory_at_commit(self, commit_ref: str, dir_path: Path) -> List[Path]:
        """
        List directory contents at specific Git commit.

        Args:
            commit_ref: Git commit SHA or "latest"
            dir_path: Path to directory to list

        Returns:
            List of Path objects for directory contents
        """
        if commit_ref == "working":
            # List current directory from filesystem using async pattern
            try:
                async_dir = AsyncPath(dir_path)
                if not await async_dir.is_dir():
                    raise FileNotFoundError(f"Directory {dir_path} does not exist")

                items = []
                async for item in async_dir.iterdir():
                    items.append(Path(item))
                return items
            except OSError as e:
                raise OSError(f"Cannot list current directory {dir_path}: {e}")
        elif commit_ref.startswith("git-"):
            # Extract actual commit SHA from git-{sha} format
            actual_commit = commit_ref[4:]  # Remove "git-" prefix

            # List historical directory using git ls-tree
            try:
                rel_path = dir_path.relative_to(self._repo_root)
                output = await self.git_integration._run_git_command(
                    ["ls-tree", "--name-only", actual_commit, str(rel_path)]
                )

                # Convert relative paths back to absolute paths
                items = []
                for line in output.strip().splitlines():
                    if line.strip():
                        item_path = self._repo_root / line.strip()
                        items.append(item_path)

                return items
            except GitError as e:
                if "Not a valid object name" in str(e) or "does not exist" in str(e):
                    raise FileNotFoundError(
                        f"Directory {dir_path} not found at commit {commit_ref}"
                    )
                raise OSError(f"Git error listing {dir_path} at {commit_ref}: {e}")
        else:
            raise ValueError(
                f"Invalid commit reference for Git provider: {commit_ref}. Expected 'working' or 'git-{{sha}}'."
            )

    async def file_exists_at_commit(self, commit_ref: str, file_path: Path) -> bool:
        """
        Check if file existed at specific Git commit.

        Args:
            commit_ref: Git commit SHA or "latest"
            file_path: Path to file to check

        Returns:
            True if file existed at that commit
        """
        if commit_ref == "working":
            async_path = AsyncPath(file_path)
            return await async_path.is_file()
        elif commit_ref.startswith("git-"):
            try:
                await self.read_file_at_commit(commit_ref, file_path)
                return True
            except (FileNotFoundError, OSError):
                return False
        else:
            raise ValueError(
                f"Invalid commit reference for Git provider: {commit_ref}. Expected 'working' or 'git-{{sha}}'."
            )

    async def directory_exists_at_commit(self, commit_ref: str, dir_path: Path) -> bool:
        """
        Check if directory existed at specific Git commit.

        Args:
            commit_ref: Git commit SHA or "latest"
            dir_path: Path to directory to check

        Returns:
            True if directory existed at that commit
        """
        if commit_ref == "working":
            async_path = AsyncPath(dir_path)
            return await async_path.is_dir()
        elif commit_ref.startswith("git-"):
            try:
                await self.list_directory_at_commit(commit_ref, dir_path)
                return True
            except (FileNotFoundError, OSError):
                return False
        else:
            raise ValueError(
                f"Invalid commit reference for Git provider: {commit_ref}. Expected 'working' or 'git-{{sha}}'."
            )

    def get_vcs_type(self) -> str:
        """Get the VCS type for this provider."""
        return "git"

    def get_repo_root(self) -> Path:
        """Get the Git repository root path."""
        return self._repo_root

    # Private helper methods

    def _is_commit_sha(self, reference: str) -> bool:
        """Check if reference looks like a Git commit SHA."""
        return bool(re.match(r"^[0-9a-f]{7,40}$", reference.lower()))

    def _is_relative_time(self, reference: str) -> bool:
        """Check if reference is a relative time expression."""
        patterns = [
            r"^\d+\s*(d|day|days)\s*ago$",
            r"^\d+\s*(h|hour|hours)\s*ago$",
            r"^\d+\s*(m|minute|minutes)\s*ago$",
            r"^\d+\s*(w|week|weeks)\s*ago$",
            r"^(yesterday|today)$",
            r"^\d+[dhw]$",  # Short form: 3d, 2h, 1w
        ]
        reference_lower = reference.lower()
        return any(re.match(pattern, reference_lower) for pattern in patterns)

    def _parse_relative_time(self, reference: str) -> datetime:
        """Parse relative time reference to datetime."""
        reference_lower = reference.lower()
        now = datetime.now()

        # Handle special cases
        if reference_lower == "yesterday":
            return now - timedelta(days=1)
        elif reference_lower == "today":
            return now

        # Handle numeric patterns
        if match := re.match(r"^(\d+)\s*(d|day|days)\s*ago$", reference_lower):
            days = int(match.group(1))
            return now - timedelta(days=days)
        elif match := re.match(r"^(\d+)\s*(h|hour|hours)\s*ago$", reference_lower):
            hours = int(match.group(1))
            return now - timedelta(hours=hours)
        elif match := re.match(r"^(\d+)\s*(m|minute|minutes)\s*ago$", reference_lower):
            minutes = int(match.group(1))
            return now - timedelta(minutes=minutes)
        elif match := re.match(r"^(\d+)\s*(w|week|weeks)\s*ago$", reference_lower):
            weeks = int(match.group(1))
            return now - timedelta(weeks=weeks)
        elif match := re.match(r"^(\d+)([dhw])$", reference_lower):
            amount = int(match.group(1))
            unit = match.group(2)
            if unit == "d":
                return now - timedelta(days=amount)
            elif unit == "h":
                return now - timedelta(hours=amount)
            elif unit == "w":
                return now - timedelta(weeks=amount)

        # Default to now if parsing fails
        return now

    async def _timestamp_to_commit(self, timestamp: datetime) -> Optional[str]:
        """Convert timestamp to nearest Git commit SHA."""
        try:
            # Use git log to find commit at or before timestamp
            iso_timestamp = timestamp.isoformat()
            output = await self.git_integration._run_git_command(
                ["log", f"--until={iso_timestamp}", "--pretty=format:%H", "-1", "HEAD"]
            )

            commit_sha = output.strip()
            return commit_sha if commit_sha else None
        except GitError:
            return None

    async def _resolve_git_reference(self, reference: str) -> Optional[str]:
        """Resolve Git reference (tag, branch) to commit SHA."""
        try:
            output = await self.git_integration._run_git_command(["rev-parse", reference])
            return output.strip()
        except GitError:
            return None
