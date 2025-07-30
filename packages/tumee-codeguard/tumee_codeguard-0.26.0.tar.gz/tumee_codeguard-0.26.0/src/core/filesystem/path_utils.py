"""
Path Utilities for Filesystem Operations

Provides utilities for path expansion, normalization, and user-aware path conversion.
Extracted from discovery_manager.py to make these utilities available across the codebase.
"""

import getpass
import os
import pwd
from typing import Union


def expand_path_for_io(path: str) -> str:
    """Expand path to absolute format ONLY for file I/O operations."""
    return str(os.path.abspath(os.path.expanduser(path)))


def convert_to_username_path(abs_path: str) -> str:
    """Convert absolute path to ~username/ format for multi-user compatibility."""
    # Get current user info
    current_user = getpass.getuser()

    try:
        # Get the home directory for current user
        user_home = pwd.getpwnam(current_user).pw_dir

        if abs_path.startswith(user_home):
            # Replace with ~username/ format
            relative_part = abs_path[len(user_home) :].lstrip(os.sep)
            if relative_part:
                return f"~{current_user}/{relative_part}"
            else:
                return f"~{current_user}/"

        # For paths outside user home, try to find which user's home it belongs to
        for user_entry in pwd.getpwall():
            if user_entry.pw_dir and abs_path.startswith(user_entry.pw_dir + os.sep):
                relative_part = abs_path[len(user_entry.pw_dir) :].lstrip(os.sep)
                return f"~{user_entry.pw_name}/{relative_part}"

        # If not in any user's home directory, return absolute path
        return abs_path

    except Exception:
        # Fallback to absolute path if username lookup fails
        return abs_path


def normalize_path_for_storage(path: str) -> str:
    """Convert path to normalized ~username/ format for storage in configs and network messages."""
    # If already in ~username/ format, keep it
    if path.startswith("~") and "/" in path:
        return path

    # If just ~, expand to ~username/
    if path == "~":
        return f"~{getpass.getuser()}/"

    # If absolute path, convert to ~username/ format
    if os.path.isabs(path):
        return convert_to_username_path(path)

    # For relative paths like ".", convert to absolute first, then to ~username/
    abs_path = os.path.abspath(path)
    return convert_to_username_path(abs_path)


def smart_truncate_path(path: str, max_length: int = 50) -> str:
    """Smart truncation that uses maximum available space while preserving filename."""
    if len(path) <= max_length:
        return path

    # Split path into parts
    parts = path.split("/")
    if len(parts) <= 2:
        # Short path, just truncate from middle
        if len(path) > max_length:
            excess = len(path) - max_length + 3  # +3 for "..."
            start_keep = (len(path) - excess) // 2
            return path[:start_keep] + "..." + path[start_keep + excess :]
        return path

    filename = parts[-1]
    first_dir = parts[0] if parts else ""

    # Calculate minimum space needed: first_dir + "/" + "..." + "/" + filename
    min_space_needed = len(first_dir) + 1 + 3 + 1 + len(filename)  # = first_dir/.../filename

    if min_space_needed > max_length:
        # Even minimal truncation won't fit, need to truncate filename too
        available_for_filename = max_length - len(first_dir) - 5  # -5 for "/.../."
        if "." in filename and available_for_filename > 5:
            name_part, ext = filename.rsplit(".", 1)
            name_chars = available_for_filename - len(ext) - 1  # -1 for "."
            if name_chars > 0:
                return f"{first_dir}/.../{name_part[:name_chars]}.{ext}"
        return f"{first_dir}/.../{filename[:available_for_filename]}"

    # We have space to work with. Calculate how much middle path we can include
    available_for_middle = (
        max_length - len(first_dir) - len(filename) - 2
    )  # -2 for "/" at start and end

    if len(parts) == 3:
        # Simple case: first_dir/middle/filename
        middle = parts[1]
        if len(middle) <= available_for_middle:
            return path  # Original path fits
        else:
            # Truncate the middle directory
            chars_to_keep = available_for_middle - 3  # -3 for "..."
            if chars_to_keep > 0:
                return f"{first_dir}/{middle[:chars_to_keep]}.../{filename}"
            else:
                return f"{first_dir}/.../{filename}"

    # Multiple middle directories - try to fit as much as possible
    middle_parts = parts[1:-1]
    full_middle = "/".join(middle_parts)

    if len(full_middle) <= available_for_middle:
        return path  # Original path fits

    # Need to truncate middle path. Try to keep some of it
    if available_for_middle > 3:  # Room for "..."
        chars_to_keep = available_for_middle - 3
        return f"{first_dir}/{full_middle[:chars_to_keep]}.../{filename}"
    else:
        # No room for middle content, just use "..."
        return f"{first_dir}/.../{filename}"
