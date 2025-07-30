"""
Shared directory traversal filtering logic for CodeGuard.

This module provides a unified traversal filtering function that respects:
- System exclude directories (.git, __pycache__, etc.)
- AI ownership boundaries (AI-OWNER files)
- Gitignore patterns
- Security boundaries

Used by both FileSystemAccess and fs_walk to ensure consistent behavior.
"""

from pathlib import Path
from typing import Optional

from ..interfaces import IFileSystemAccess
from ..language.config import is_ai_ownership_file, is_system_exclude_directory


def should_traverse_directory(
    directory: Path,
    base_path: Path,
    respect_gitignore: bool,
    gitignore_cache: Optional[dict],
    filesystem_access,
    ai_ownership_cache: Optional[dict] = None,
) -> bool:
    """
    Determine if we should traverse into a directory based on filtering rules.

    This is the unified filtering logic used by both FileSystemAccess and fs_walk
    to ensure consistent directory traversal behavior across the codebase.

    Args:
        directory: Directory to check
        base_path: Base path for relative calculations
        respect_gitignore: Whether to respect .gitignore patterns
        gitignore_cache: Optional gitignore cache dictionary
        filesystem_access: IFileSystemAccess instance for security and gitignore checks
        ai_ownership_cache: Optional AI ownership cache to avoid repeated checks

    Returns:
        True if directory should be traversed
    """
    # Check system exclusions first (highest priority)
    if is_system_exclude_directory(directory):
        return False

    # Check if directory is AI-owned AND not the project root
    # AI-owned subdirectories should be treated as opaque module boundaries
    # but we allow traversal if the AI-OWNER is in the project root

    # Use cache if provided, otherwise compute directly
    directory_str = str(directory)
    if ai_ownership_cache is not None:
        if directory_str not in ai_ownership_cache:
            ai_ownership_cache[directory_str] = is_ai_ownership_file(directory) is not None
        has_ai_ownership = ai_ownership_cache[directory_str]
    else:
        has_ai_ownership = is_ai_ownership_file(directory) is not None

    if has_ai_ownership and directory != base_path:
        return False

    # Basic security check
    if not filesystem_access.security_manager.is_path_allowed(directory):
        return False

    # Check gitignore if requested
    if respect_gitignore:
        # If directory would be filtered by gitignore, don't traverse it
        filtered = filesystem_access._filter_gitignore([directory], base_path, gitignore_cache)
        if not filtered:
            return False

    return True
