"""
VCS-agnostic temporal provider interfaces.

This module defines the abstract interfaces for temporal filesystem operations
that work with any version control system (Git, SVN, Mercurial, etc.).
"""

from pathlib import Path
from typing import List, Optional, Protocol


class ITemporalProvider(Protocol):
    """
    Source control agnostic temporal operations interface.

    This interface abstracts temporal filesystem operations to work with any VCS.
    Implementations provide VCS-specific logic while maintaining a consistent API.
    """

    async def resolve_reference(self, reference: str) -> str:
        """
        Convert human-readable reference to VCS-specific commit reference.

        Args:
            reference: Human reference like "3 days ago", "v1.2.0", "latest", timestamp

        Returns:
            VCS-specific commit reference (Git SHA, SVN revision, etc.)
            Returns "latest" for current/HEAD references

        Examples:
            "latest" -> "latest"
            "3 days ago" -> "abc123f" (Git SHA)
            "v1.2.0" -> "def456a" (Git SHA)
            "12345" -> "12345" (SVN revision)
        """
        ...

    async def read_file_at_commit(self, commit_ref: str, file_path: Path) -> str:
        """
        Read file content at specific commit/revision.

        Args:
            commit_ref: VCS-specific commit reference or "latest"
            file_path: Path to file to read

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist at that commit
            OSError: If file cannot be read
        """
        ...

    async def list_directory_at_commit(self, commit_ref: str, dir_path: Path) -> List[Path]:
        """
        List directory contents at specific commit/revision.

        Args:
            commit_ref: VCS-specific commit reference or "latest"
            dir_path: Path to directory to list

        Returns:
            List of Path objects for directory contents as they existed at commit

        Raises:
            FileNotFoundError: If directory doesn't exist at that commit
            OSError: If directory cannot be read
        """
        ...

    async def file_exists_at_commit(self, commit_ref: str, file_path: Path) -> bool:
        """
        Check if file existed at specific commit/revision.

        Args:
            commit_ref: VCS-specific commit reference or "latest"
            file_path: Path to file to check

        Returns:
            True if file existed at that commit, False otherwise
        """
        ...

    async def directory_exists_at_commit(self, commit_ref: str, dir_path: Path) -> bool:
        """
        Check if directory existed at specific commit/revision.

        Args:
            commit_ref: VCS-specific commit reference or "latest"
            dir_path: Path to directory to check

        Returns:
            True if directory existed at that commit, False otherwise
        """
        ...

    def get_vcs_type(self) -> str:
        """
        Get the VCS type for this provider.

        Returns:
            VCS type identifier ("git", "svn", "hg", "p4", etc.)
        """
        ...

    def get_repo_root(self) -> Path:
        """
        Get the repository root path.

        Returns:
            Path to repository root directory
        """
        ...
