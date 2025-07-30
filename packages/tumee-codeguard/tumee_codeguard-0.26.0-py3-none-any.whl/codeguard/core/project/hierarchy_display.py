"""
Core hierarchy display utilities for project boundaries and P2P networks.

This module provides centralized formatting functions for project hierarchy display,
used by P2P servers, CLI commands, and other services that need to display
project boundaries with worktree relationships and @name support.
"""

from datetime import datetime

from ..filesystem.path_utils import convert_to_username_path
from .boundary_discovery import get_boundary_display_info


def format_hierarchy_display(hierarchy_data: dict) -> str:
    """
    Format hierarchy display data for console output with enhanced worktree relationships.

    This function handles the presentation layer logic for project hierarchy,
    including P2P network hierarchies with worktree relationships and @name support.

    Args:
        hierarchy_data: Dictionary containing hierarchy tree data from discovery manager

    Returns:
        Formatted string ready for display
    """
    lines = []
    lines.append("\n📋 Project Hierarchy:")
    lines.append("=" * 50)

    hierarchy_tree = hierarchy_data.get("tree", {})

    if not hierarchy_tree:
        lines.append("No nodes currently connected")
    else:
        # Sort paths by length (parents before children)
        sorted_paths = sorted(hierarchy_tree.keys(), key=len)

        for path in sorted_paths:
            node_info = hierarchy_tree[path]
            node_id = node_info.get("node_id", "unknown")
            boundaries = node_info.get("boundaries", [])

            # Main node line
            lines.append(f"🖥️  {path} ({node_id})")
            lines.append(f"   📍 Address: {node_info.get('address', 'unknown')}")

            # Show boundaries within this node as an enhanced tree with worktree relationships
            if boundaries:
                tree_lines = _build_enhanced_boundary_tree(boundaries)
                for line in tree_lines:
                    lines.append(f"   {line}")
            lines.append("")  # Empty line between nodes

    lines.append("=" * 50)
    lines.append("📝 Press 'q' to quit, 'l' to list hierarchy")

    return "\n".join(lines)


def format_hierarchy_display_for_server(hierarchy_data: dict) -> str:
    """
    Format hierarchy display data for server output (no interactive prompts).

    Args:
        hierarchy_data: Dictionary containing hierarchy tree data from discovery manager

    Returns:
        Formatted string ready for display (without interactive prompt text)
    """
    lines = []
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    lines.append(f"\n📋 Project Hierarchy Updated: {current_time}")
    lines.append("=" * 50)

    hierarchy_tree = hierarchy_data.get("tree", {})

    if not hierarchy_tree:
        lines.append("No nodes currently connected")
    else:
        # Sort paths by length (parents before children)
        sorted_paths = sorted(hierarchy_tree.keys(), key=len)

        for path in sorted_paths:
            node_info = hierarchy_tree[path]
            node_id = node_info.get("node_id", "unknown")
            boundaries = node_info.get("boundaries", [])

            # Main node line
            lines.append(f"🖥️  {path} ({node_id})")
            lines.append(f"   📍 Address: {node_info.get('address', 'unknown')}")

            # Show boundaries within this node as an enhanced tree with worktree relationships
            if boundaries:
                tree_lines = _build_enhanced_boundary_tree(boundaries)
                for line in tree_lines:
                    lines.append(f"   {line}")
            lines.append("")  # Empty line between nodes

    lines.append("=" * 50)

    return "\n".join(lines)


def _build_enhanced_boundary_tree(boundaries: list) -> list:
    """
    Build an enhanced tree structure showing directory structure with @names.

    This function creates a hierarchical display that shows:
    - Proper directory structure (Projects/, Projects.ai/)
    - Main repositories (🏠) with their @names
    - Worktree relationships (🌿) as peers at appropriate levels
    - AI-owned modules (🤖) indented under their containing repo/worktree
    - Clean display without status clutter or misaligned emojis

    Args:
        boundaries: List of boundary dictionaries

    Returns:
        List of formatted tree lines with enhanced display
    """
    if not boundaries:
        return ["No boundaries found"]

    # Use the original tree building approach but customize the display
    tree = {}
    for boundary in boundaries:
        boundary_path = boundary.get("path", "")
        if not boundary_path:
            continue

        # Normalize path and split into components
        path = convert_to_username_path(boundary_path)
        parts = path.split("/")

        # Build nested tree structure
        current = tree
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {"children": {}, "boundary": None}
            current = current[part]["children"]

            # Store boundary info at the deepest level
            if i == len(parts) - 1:
                current_parent = tree
                for p in parts[:-1]:
                    current_parent = current_parent[p]["children"]
                current_parent[part]["boundary"] = boundary

    # Convert tree to formatted lines with custom formatting
    return _format_enhanced_tree_lines(tree, "", True)


def _format_enhanced_tree_lines(tree: dict, prefix: str, is_root: bool) -> list:
    """
    Format tree structure into clean ASCII tree lines without status clutter.

    Args:
        tree: Nested dictionary representing tree structure
        prefix: Current line prefix for indentation
        is_root: Whether this is the root level

    Returns:
        List of formatted tree lines
    """
    lines = []
    items = sorted(tree.items())

    for i, (name, node) in enumerate(items):
        is_last = i == len(items) - 1

        # Determine tree characters
        if is_root:
            current_prefix = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "
        else:
            current_prefix = prefix + ("└── " if is_last else "├── ")
            next_prefix = prefix + ("    " if is_last else "│   ")

        # Format current line
        boundary = node.get("boundary")
        if boundary:
            # Get boundary display info which includes the @name
            display_info = get_boundary_display_info(boundary)
            name_display = display_info.get("name_display", "")

            # Choose emoji based on boundary type
            repo_type = boundary.get("repo_type", "")
            is_repo = boundary.get("is_repository", False)
            has_ai = boundary.get("has_ai_owner", False)

            if is_repo and repo_type == "main":
                emoji = "🏠"
            elif is_repo and repo_type == "worktree":
                emoji = "🌿"
            elif has_ai:
                emoji = "🤖"
            else:
                emoji = "📁"

            # Display with @name from boundary discovery system
            lines.append(f"{current_prefix}{emoji}{name}{name_display}")
        else:
            # Directory node
            lines.append(f"{current_prefix}{name}/")

        # Recursively format children
        if node["children"]:
            child_lines = _format_enhanced_tree_lines(node["children"], next_prefix, False)
            lines.extend(child_lines)

    return lines


def _get_boundary_name(boundary: dict) -> str:
    """Extract display name from boundary path."""
    path = boundary.get("path", "")
    if path:
        return convert_to_username_path(path).split("/")[-1]
    return "unknown"


def _is_worktree_of_repo(worktree: dict, repo_path: str) -> bool:
    """Check if a worktree belongs to a specific main repository."""
    # This would need to check the actual worktree parent relationship
    # For now, we'll use a simple path-based heuristic
    wt_path = worktree.get("path", "")
    if not wt_path or not repo_path:
        return False

    # Simple heuristic: worktrees often share name prefixes with their parent
    repo_name = repo_path.split("/")[-1] if "/" in repo_path else repo_path
    wt_name = wt_path.split("/")[-1] if "/" in wt_path else wt_path

    return wt_name.startswith(repo_name) or repo_name in wt_name


def _build_boundary_tree(boundaries: list) -> list:
    """
    Build a tree structure from boundary paths (legacy fallback).

    Args:
        boundaries: List of boundary dictionaries

    Returns:
        List of formatted tree lines
    """

    # Build tree structure from paths
    tree = {}
    for boundary in boundaries:
        boundary_path = boundary.get("path", "")
        if not boundary_path:
            continue

        # Normalize path and split into components
        path = convert_to_username_path(boundary_path)
        parts = path.split("/")

        # Build nested tree structure
        current = tree
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {"children": {}, "boundary": None}
            current = current[part]["children"]

            # Store boundary info at the deepest level
            if i == len(parts) - 1:
                current_parent = tree
                for p in parts[:-1]:
                    current_parent = current_parent[p]["children"]
                current_parent[part]["boundary"] = boundary

    # Convert tree to formatted lines
    return _format_tree_lines(tree, "", True)


def _format_tree_lines(tree: dict, prefix: str, is_root: bool) -> list:
    """
    Format tree structure into ASCII tree lines.

    Args:
        tree: Nested dictionary representing tree structure
        prefix: Current line prefix for indentation
        is_root: Whether this is the root level

    Returns:
        List of formatted tree lines
    """
    lines = []
    items = sorted(tree.items())

    for i, (name, node) in enumerate(items):
        is_last = i == len(items) - 1

        # Determine tree characters
        if is_root:
            current_prefix = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "
        else:
            current_prefix = prefix + ("└── " if is_last else "├── ")
            next_prefix = prefix + ("    " if is_last else "│   ")

        # Format current line
        boundary = node.get("boundary")
        if boundary:
            # Get boundary display info
            display_info = get_boundary_display_info(boundary)
            emoji = display_info["emoji"]
            status = display_info["status"]
            name_display = display_info.get("name_display", "")
            lines.append(f"{current_prefix}{name} {emoji} ({status}){name_display}")
        else:
            lines.append(f"{current_prefix}{name}/")

        # Recursively format children
        if node["children"]:
            child_lines = _format_tree_lines(node["children"], next_prefix, False)
            lines.extend(child_lines)

    return lines
