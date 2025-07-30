"""
Temporal provider factory for auto-detecting VCS and creating appropriate providers.

This module provides a factory for creating temporal providers based on the
detected version control system in a given directory.
"""

from pathlib import Path
from typing import Optional, Union

from .interfaces import ITemporalProvider
from .providers.git_provider import GitTemporalProvider


class TemporalProviderFactory:
    """
    Factory for creating temporal providers based on detected VCS.

    This factory automatically detects the version control system in use
    and returns the appropriate temporal provider implementation.
    """

    @staticmethod
    def create_provider(repo_path: Optional[Union[str, Path]] = None) -> ITemporalProvider:
        """
        Auto-detect VCS and create appropriate temporal provider.

        Args:
            repo_path: Path to repository root. If None, uses current directory.

        Returns:
            Temporal provider instance for the detected VCS

        Raises:
            ValueError: If no supported VCS is detected

        Examples:
            # Auto-detect from current directory
            provider = TemporalProviderFactory.create_provider()

            # Specify repository path
            provider = TemporalProviderFactory.create_provider("/path/to/repo")
        """
        if repo_path is None:
            repo_path = Path.cwd()
        else:
            repo_path = Path(repo_path)

        # Try to detect VCS by looking for characteristic directories/files
        if TemporalProviderFactory._is_git_repo(repo_path):
            return GitTemporalProvider(repo_path)
        elif TemporalProviderFactory._is_svn_repo(repo_path):
            # Future: return SvnTemporalProvider(repo_path)
            raise ValueError("SVN temporal provider not yet implemented")
        elif TemporalProviderFactory._is_mercurial_repo(repo_path):
            # Future: return HgTemporalProvider(repo_path)
            raise ValueError("Mercurial temporal provider not yet implemented")
        elif TemporalProviderFactory._is_perforce_workspace(repo_path):
            # Future: return P4TemporalProvider(repo_path)
            raise ValueError("Perforce temporal provider not yet implemented")
        else:
            raise ValueError(f"No supported VCS detected in {repo_path}")

    @staticmethod
    def get_detected_vcs_type(repo_path: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Detect the VCS type without creating a provider.

        Args:
            repo_path: Path to repository root. If None, uses current directory.

        Returns:
            VCS type identifier ("git", "svn", "hg", "p4") or None if not detected
        """
        if repo_path is None:
            repo_path = Path.cwd()
        else:
            repo_path = Path(repo_path)

        if TemporalProviderFactory._is_git_repo(repo_path):
            return "git"
        elif TemporalProviderFactory._is_svn_repo(repo_path):
            return "svn"
        elif TemporalProviderFactory._is_mercurial_repo(repo_path):
            return "hg"
        elif TemporalProviderFactory._is_perforce_workspace(repo_path):
            return "p4"
        else:
            return None

    @staticmethod
    def is_vcs_repo(repo_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Check if the path contains any supported VCS.

        Args:
            repo_path: Path to check. If None, uses current directory.

        Returns:
            True if any supported VCS is detected, False otherwise
        """
        return TemporalProviderFactory.get_detected_vcs_type(repo_path) is not None

    # Private VCS detection methods

    @staticmethod
    def _is_git_repo(repo_path: Path) -> bool:
        """Check if path is a Git repository."""
        # Look for .git directory or .git file (for worktrees)
        git_path = repo_path / ".git"
        return git_path.exists()

    @staticmethod
    def _is_svn_repo(repo_path: Path) -> bool:
        """Check if path is an SVN working copy."""
        # Look for .svn directory (SVN 1.7+)
        svn_path = repo_path / ".svn"
        return svn_path.exists() and svn_path.is_dir()

    @staticmethod
    def _is_mercurial_repo(repo_path: Path) -> bool:
        """Check if path is a Mercurial repository."""
        # Look for .hg directory
        hg_path = repo_path / ".hg"
        return hg_path.exists() and hg_path.is_dir()

    @staticmethod
    def _is_perforce_workspace(repo_path: Path) -> bool:
        """Check if path is a Perforce workspace."""
        # Look for .p4config file or P4CONFIG environment variable
        p4config_path = repo_path / ".p4config"
        return p4config_path.exists() and p4config_path.is_file()

    @staticmethod
    def create_git_provider(repo_path: Optional[Union[str, Path]] = None) -> GitTemporalProvider:
        """
        Create a Git temporal provider directly.

        Args:
            repo_path: Path to Git repository root. If None, uses current directory.

        Returns:
            Git temporal provider instance

        Raises:
            ValueError: If path is not a Git repository
        """
        if repo_path is None:
            repo_path = Path.cwd()
        else:
            repo_path = Path(repo_path)

        if not TemporalProviderFactory._is_git_repo(repo_path):
            raise ValueError(f"Not a Git repository: {repo_path}")

        return GitTemporalProvider(repo_path)
