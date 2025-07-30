"""
MCP Roots security enforcement for CodeGuard.

This module provides filesystem access control and boundary enforcement
based on the MCP roots capability specification.
"""

import os
from pathlib import Path
from typing import List, Optional, Set, Union

from ..interfaces import ISecurityManager
from ..types import SecurityError


class RootsSecurityManager(ISecurityManager):
    """
    Core security service that enforces MCP roots filesystem boundaries.

    This manager ensures all filesystem operations stay within approved root directories,
    implementing the MCP roots capability for secure directory access control.
    """

    def __init__(self, allowed_roots: List[Union[str, Path]]):
        """
        Initialize security manager with allowed root directories.

        Args:
            allowed_roots: List of directory paths that define access boundaries.
                          All filesystem access must be within these roots.

        Raises:
            SecurityError: If any root path is invalid or inaccessible
        """
        if not allowed_roots:
            raise SecurityError("At least one root directory must be specified")

        self.allowed_roots: List[Path] = []

        for root in allowed_roots:
            root_path = Path(root).expanduser().resolve()

            # Validate that root exists and is a directory
            if not root_path.exists():
                raise SecurityError(f"Root directory does not exist: {root_path}")

            if not root_path.is_dir():
                raise SecurityError(f"Root path is not a directory: {root_path}")

            # Ensure we can read the directory
            try:
                list(root_path.iterdir())
            except (PermissionError, OSError) as e:
                raise SecurityError(f"Cannot access root directory {root_path}: {e}")

            self.allowed_roots.append(root_path)

    def is_path_allowed(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is within any allowed root directory.

        Args:
            path: Path to check for access permission

        Returns:
            True if path is within allowed boundaries, False otherwise
        """
        try:
            target_path = Path(path).resolve()
        except (OSError, ValueError):
            return False

        # Check if path is within any allowed root
        for root in self.allowed_roots:
            try:
                # Check if target_path is the same as or a subdirectory of root
                target_path.relative_to(root)
                return True
            except ValueError:
                # relative_to() raises ValueError if path is not relative to root
                continue

        return False

    def safe_resolve(self, path: Union[str, Path]) -> Path:
        """
        Safely resolve a path and validate it's within allowed boundaries.

        Args:
            path: Path to resolve and validate

        Returns:
            Resolved Path object if within boundaries

        Raises:
            SecurityError: If path is outside allowed root directories
        """
        try:
            resolved_path = Path(path).resolve()
        except (OSError, ValueError) as e:
            raise SecurityError(f"Cannot resolve path {path}: {e}")

        if not self.is_path_allowed(resolved_path):
            raise SecurityError(
                f"Access denied: {resolved_path} is outside allowed root directories. "
                f"Allowed roots: {[str(r) for r in self.allowed_roots]}"
            )

        return resolved_path

    def get_traversal_boundary(self, current_path: Union[str, Path]) -> Optional[Path]:
        """
        Get the root boundary for upward directory traversal from current path.

        This method determines the furthest ancestor directory that upward traversal
        should reach before stopping, based on the allowed roots.

        Args:
            current_path: Starting path for traversal

        Returns:
            Path object representing the traversal boundary, or None if path is not allowed
        """
        try:
            current = Path(current_path).resolve()
        except (OSError, ValueError):
            return None

        if not self.is_path_allowed(current):
            return None

        # Find which root contains this path
        for root in self.allowed_roots:
            try:
                current.relative_to(root)
                return root  # This root contains the current path
            except ValueError:
                continue

        return None

    def validate_directory_access(self, directory: Union[str, Path]) -> Path:
        """
        Validate access to a directory and return resolved path.

        Args:
            directory: Directory path to validate

        Returns:
            Resolved directory Path object

        Raises:
            SecurityError: If directory access is not allowed
        """
        resolved_dir = self.safe_resolve(directory)

        if not resolved_dir.is_dir():
            raise SecurityError(f"Path is not a directory: {resolved_dir}")

        return resolved_dir

    def validate_file_access(self, file_path: Union[str, Path]) -> Path:
        """
        Validate access to a file and return resolved path.

        Args:
            file_path: File path to validate

        Returns:
            Resolved file Path object

        Raises:
            SecurityError: If file access is not allowed
        """
        resolved_file = self.safe_resolve(file_path)

        # For file access, we allow the file to not exist yet (for creation)
        # but its parent directory must exist and be accessible
        if not resolved_file.exists():
            parent_dir = resolved_file.parent
            if not parent_dir.exists():
                raise SecurityError(f"Parent directory does not exist: {parent_dir}")
            if not parent_dir.is_dir():
                raise SecurityError(f"Parent path is not a directory: {parent_dir}")

        return resolved_file

    def add_root(self, new_root: Union[str, Path]) -> None:
        """
        Add a new allowed root directory.

        Args:
            new_root: New root directory to add to allowed list

        Raises:
            SecurityError: If new root is invalid or inaccessible
        """
        root_path = Path(new_root).resolve()

        # Validate the new root
        if not root_path.exists():
            raise SecurityError(f"Root directory does not exist: {root_path}")

        if not root_path.is_dir():
            raise SecurityError(f"Root path is not a directory: {root_path}")

        # Check if this root is already covered by existing roots
        for existing_root in self.allowed_roots:
            try:
                root_path.relative_to(existing_root)
                # New root is subdirectory of existing root, no need to add
                return
            except ValueError:
                pass

        # Remove any existing roots that would be subdirectories of the new root
        self.allowed_roots = [
            root for root in self.allowed_roots if not self._is_subdirectory(root, root_path)
        ]

        self.allowed_roots.append(root_path)

    def _is_subdirectory(self, potential_child: Path, potential_parent: Path) -> bool:
        """Check if potential_child is a subdirectory of potential_parent."""
        try:
            potential_child.relative_to(potential_parent)
            return True
        except ValueError:
            return False

    def get_allowed_roots(self) -> List[Path]:
        """
        Get list of currently allowed root directories.

        Returns:
            Copy of the allowed roots list
        """
        return self.allowed_roots.copy()


def determine_allowed_roots(
    cli_roots: Optional[List[str]] = None,
    config_roots: Optional[List[str]] = None,
    mcp_roots: Optional[List[str]] = None,
) -> List[Path]:
    """
    Determine final allowed roots from all sources with priority hierarchy.

    Priority (lowest to highest): hard default < config < CLI < MCP
    Each level can ADD to the previous level's roots.

    Args:
        cli_roots: Roots specified via CLI --allowed-roots flag
        config_roots: Roots specified in config file
        mcp_roots: Roots specified via MCP protocol

    Returns:
        List of resolved Path objects for allowed roots
    """
    roots: Set[Path] = set()

    # 1. Hard default: User home directory
    roots.add(Path.home().resolve())

    # 2. Config file additions
    if config_roots:
        for root in config_roots:
            try:
                roots.add(Path(root).expanduser().resolve())
            except (OSError, ValueError):
                # Skip invalid paths from config
                pass

    # 3. CLI additions
    if cli_roots:
        for root in cli_roots:
            try:
                roots.add(Path(root).expanduser().resolve())
            except (OSError, ValueError):
                # Skip invalid paths from CLI
                pass

    # 4. MCP protocol additions
    if mcp_roots:
        for root in mcp_roots:
            try:
                roots.add(Path(root).expanduser().resolve())
            except (OSError, ValueError):
                # Skip invalid paths from MCP
                pass

    return list(roots)


def create_security_manager(
    cli_roots: Optional[List[str]] = None,
    config_roots: Optional[List[str]] = None,
    mcp_roots: Optional[List[str]] = None,
) -> RootsSecurityManager:
    """
    Create a security manager with roots determined from all sources.

    Args:
        cli_roots: Roots specified via CLI --allowed-roots flag
        config_roots: Roots specified in config file
        mcp_roots: Roots specified via MCP protocol

    Returns:
        RootsSecurityManager with determined allowed roots

    Raises:
        SecurityError: If no valid roots can be determined
    """
    allowed_roots = determine_allowed_roots(cli_roots, config_roots, mcp_roots)

    if not allowed_roots:
        raise SecurityError("No valid root directories could be determined")

    return RootsSecurityManager(allowed_roots)


def create_default_security_manager() -> RootsSecurityManager:
    """
    Create a default security manager with user home directory as root.

    This is the fallback when no other root specification is available.

    Returns:
        RootsSecurityManager with user home directory as the only allowed root
    """
    return create_security_manager()


def parse_cli_roots(roots_string: Optional[str]) -> Optional[List[str]]:
    """
    Parse CLI roots string into list of root paths.

    Accepts comma-separated or colon-separated paths.

    Args:
        roots_string: String like "/path1,/path2" or "/path1:/path2"

    Returns:
        List of root path strings, or None if input is None/empty
    """
    if not roots_string:
        return None

    # Support both comma and colon separators
    if "," in roots_string:
        return [path.strip() for path in roots_string.split(",") if path.strip()]
    elif ":" in roots_string:
        return [path.strip() for path in roots_string.split(":") if path.strip()]
    else:
        # Single path
        return [roots_string.strip()] if roots_string.strip() else None
