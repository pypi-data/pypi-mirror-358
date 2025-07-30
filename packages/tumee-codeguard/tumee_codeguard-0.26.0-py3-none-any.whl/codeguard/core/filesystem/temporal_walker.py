"""
Temporal filesystem walker - convenience functions for walking historical commits.

This module provides helper functions to easily walk filesystem trees at specific
points in time using the existing fs_walk infrastructure with temporal providers.
"""

from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from ..interfaces import ISecurityManager
from .temporal import TemporalFileSystemAccess, TemporalProviderFactory
from .walker import fs_walk


async def fs_walk_at_commit(
    commit_reference: str,
    directory: Union[str, Path],
    security_manager: ISecurityManager,
    repo_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Walk filesystem tree at a specific commit/revision.

    This is a convenience function that automatically creates a temporal provider
    and filesystem access for the specified commit, then delegates to the standard
    fs_walk function.

    Args:
        commit_reference: Human-readable commit reference ("3 days ago", "v1.2.0", etc.)
        directory: Directory to walk
        security_manager: Security manager for boundary enforcement
        repo_path: Repository root path (auto-detected if None)
        **kwargs: Additional arguments passed to fs_walk()

    Yields:
        File/directory information dictionaries as they existed at the commit

    Examples:
        # Walk current working directory
        async for item in fs_walk_at_commit("working", "/src", security_mgr):
            print(item)

        # Walk 3 days ago
        async for item in fs_walk_at_commit("3 days ago", "/src", security_mgr):
            print(item)

        # Walk specific version tag
        async for item in fs_walk_at_commit("v1.2.0", "/src", security_mgr):
            print(item)
    """
    # Auto-detect VCS and create temporal provider
    provider = TemporalProviderFactory.create_provider(repo_path)

    # Resolve human reference to VCS-specific commit reference
    resolved_commit_ref = await provider.resolve_reference(commit_reference)

    # Create temporal filesystem access
    temporal_fs = TemporalFileSystemAccess(resolved_commit_ref, provider, security_manager)

    # Delegate to standard fs_walk with temporal filesystem
    async for item in fs_walk(temporal_fs, directory, repo_path=repo_path, **kwargs):
        yield item


async def fs_walk_current_vs_historical(
    historical_reference: str,
    directory: Union[str, Path],
    security_manager: ISecurityManager,
    repo_path: Optional[Union[str, Path]] = None,
    **kwargs,
) -> tuple[AsyncGenerator[Dict[str, Any], None], AsyncGenerator[Dict[str, Any], None]]:
    """
    Walk filesystem tree at both current and historical states.

    This function returns two async generators: one for the current working
    directory state and one for the historical commit state. Useful for
    comparison operations.

    Args:
        historical_reference: Historical commit reference to compare against
        directory: Directory to walk
        security_manager: Security manager for boundary enforcement
        repo_path: Repository root path (auto-detected if None)
        **kwargs: Additional arguments passed to fs_walk()

    Returns:
        Tuple of (current_walker, historical_walker) async generators

    Example:
        current, historical = await fs_walk_current_vs_historical(
            "3 days ago", "/src", security_mgr
        )

        current_files = [item async for item in current]
        historical_files = [item async for item in historical]

        # Compare current vs historical
        added_files = set(current_files) - set(historical_files)
    """
    # Current walker (working directory)
    current_walker = fs_walk_at_commit("working", directory, security_manager, repo_path, **kwargs)

    # Historical walker
    historical_walker = fs_walk_at_commit(
        historical_reference, directory, security_manager, repo_path, **kwargs
    )

    return current_walker, historical_walker


async def get_vcs_info(repo_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Get information about the detected VCS in a repository.

    Args:
        repo_path: Repository root path (auto-detected if None)

    Returns:
        Dictionary with VCS information

    Example:
        info = await get_vcs_info("/path/to/repo")
        print(f"VCS Type: {info['vcs_type']}")
        print(f"Repo Root: {info['repo_root']}")
    """
    try:
        provider = TemporalProviderFactory.create_provider(repo_path)
        return {
            "vcs_type": provider.get_vcs_type(),
            "repo_root": str(provider.get_repo_root()),
            "supported": True,
        }
    except ValueError as e:
        return {
            "vcs_type": None,
            "repo_root": str(Path(repo_path) if repo_path else Path.cwd()),
            "supported": False,
            "error": str(e),
        }


# Convenience aliases for common operations


async def fs_walk_working(
    directory: Union[str, Path], security_manager: ISecurityManager, **kwargs
) -> AsyncGenerator[Dict[str, Any], None]:
    """Walk current working directory (alias for fs_walk_at_commit("working", ...))."""
    async for item in fs_walk_at_commit("working", directory, security_manager, **kwargs):
        yield item


async def fs_walk_days_ago(
    days: int, directory: Union[str, Path], security_manager: ISecurityManager, **kwargs
) -> AsyncGenerator[Dict[str, Any], None]:
    """Walk filesystem as it was N days ago."""
    reference = f"{days} days ago"
    async for item in fs_walk_at_commit(reference, directory, security_manager, **kwargs):
        yield item


async def fs_walk_tag(
    tag: str, directory: Union[str, Path], security_manager: ISecurityManager, **kwargs
) -> AsyncGenerator[Dict[str, Any], None]:
    """Walk filesystem at a specific version tag."""
    async for item in fs_walk_at_commit(tag, directory, security_manager, **kwargs):
        yield item
