#!/usr/bin/env python3
"""
Profile file enumeration performance.
Run with: kernprof -l -v tests/test_file_enumeration_profile.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.filesystem.access import FileSystemAccess
from src.core.filesystem.walker import fs_walk
from src.core.security.roots import RootsSecurityManager
from src.utils.profiling import profile


@profile
async def profile_file_enumeration():
    """Profile the file enumeration on this codebase."""
    # Use current project root as test case
    project_root = Path(__file__).parent.parent

    # Set up security manager
    security_manager = RootsSecurityManager([str(project_root)])
    filesystem_access = FileSystemAccess(security_manager)

    print(f"Profiling file enumeration on: {project_root}")

    # Count files found
    file_count = 0
    dir_count = 0

    # Profile the fs_walk function
    async for item in fs_walk(
        filesystem_access=filesystem_access,
        directory=project_root,
        respect_gitignore=True,
        default_include=True,
        traversal_mode="breadth_first",
        max_depth=1,
        yield_type="both",
    ):
        if item.get("type") == "directory":
            dir_count += 1
        else:
            file_count += 1

        # Stop after tiny number for profiling - just 5 items
        if file_count + dir_count > 5:
            break

    print(f"Enumerated {file_count} files and {dir_count} directories")


if __name__ == "__main__":
    asyncio.run(profile_file_enumeration())
