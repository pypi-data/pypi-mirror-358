"""
Filesystem access factory for creating FileSystemAccess instances.

This module provides centralized filesystem access creation logic without
circular import dependencies.
"""

import argparse
import json
from pathlib import Path
from typing import List, Optional

from ..filesystem.access import FileSystemAccess
from ..interfaces import IFileSystemAccess
from ..security.roots import create_security_manager, parse_cli_roots


def create_filesystem_access_from_args(args: argparse.Namespace) -> IFileSystemAccess:
    """
    Create a FileSystemAccess instance from command-line arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Configured FileSystemAccess instance with security boundaries
    """
    # Handle CLI roots if provided
    cli_roots = None
    if hasattr(args, "allowed_roots") and args.allowed_roots:
        # If it's already a list (from MCP), use it directly
        if isinstance(args.allowed_roots, list):
            cli_roots = args.allowed_roots
        # If it's a string (from CLI), parse it
        elif isinstance(args.allowed_roots, str):
            cli_roots = parse_cli_roots(args.allowed_roots)
        else:
            # Fallback: try to parse as string
            cli_roots = parse_cli_roots(str(args.allowed_roots))

    # Load config file roots
    config_roots = load_config_roots()

    # Get MCP roots if available (from mcp server context)
    mcp_roots = None
    try:
        from ...servers.mcp_server.root_validation import get_mcp_roots

        mcp_roots = get_mcp_roots()
    except ImportError:
        # Not in MCP context, skip MCP roots
        pass

    # Create security manager with roots hierarchy: default CWD < config < CLI < MCP
    security_manager = create_security_manager(
        cli_roots=cli_roots,
        config_roots=config_roots,
        mcp_roots=mcp_roots,
    )

    # Create filesystem access layer
    return FileSystemAccess(security_manager)


def load_config_roots() -> Optional[List[str]]:
    """
    Load allowed roots from configuration files.

    Returns:
        List of root paths from config, or None if no config found
    """
    # Check for config file in standard locations
    config_paths = [
        Path.home() / ".codeguard" / "config.json",
        Path.cwd() / ".codeguard.json",
        Path.cwd() / "codeguard.json",
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("allowed_roots")
            except (json.JSONDecodeError, OSError):
                # Skip invalid config files
                continue

    return None
