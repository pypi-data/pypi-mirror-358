"""
Context discovery logic for MCP server.

This module handles automatic discovery of context files from root directories,
caching results, and notifying MCP clients of resource changes.
"""

import asyncio
import concurrent.futures
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import diskcache

from ....core.filesystem.walker import get_context_files_breadth_first
from ....core.formatters.base import DataType, FormatterRegistry


def _get_context_cache() -> diskcache.Cache:
    """Get context cache instance."""
    cache_dir = Path(tempfile.gettempdir()) / "codeguard_context_cache"
    return diskcache.Cache(str(cache_dir), timeout=3600)  # 1 hour timeout


async def _discover_context_for_root(
    root: str,
    root_index: int,
    respect_gitignore: bool = True,
    cli_excludes: List[str] = None,
    default_include: bool = False,
    registered_roots: List[str] = None,
    tree_format: bool = False,
) -> Tuple[str, Dict]:
    """Synchronous context discovery for a single root (runs in thread pool)."""
    root_id = f"root_{root_index}"

    # Include filtering options in cache key for proper cache invalidation
    filtering_hash = hashlib.sha256(
        f"{respect_gitignore}{cli_excludes or []}{default_include}".encode()
    ).hexdigest()[:8]
    cache_key = f"context_root_{hashlib.sha256(root.encode()).hexdigest()[:16]}_{filtering_hash}"

    cache = _get_context_cache()

    # Try to load from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        print(f"   📁 Using cached context for {root} (with filtering)")
        return root_id, {"path": root, "context_files": cached_result["context_files"]}

    print(f"   🔍 Discovering context files in {root} (with hierarchical filtering)...")

    # Use fs_walker to get context files and then format with core formatters
    # This gives us the option to use inspect_content for file parsing if needed
    from ....core.filesystem.access import FileSystemAccess

    # Create filesystem access instance for secure operations
    fs = FileSystemAccess()

    # Collect context files using the unified fs_walker
    context_files = []
    async for context_info in get_context_files_breadth_first(
        filesystem_access=fs,
        directory=root,
        repo_path=None,
        priority=None,
        for_use=None,
        respect_gitignore=respect_gitignore,
        cli_excludes=cli_excludes,
        default_include=default_include,
        registered_roots=registered_roots,
        inspect_content=True,  # Parse individual files for guard tags (like CLI context commands)
        target="*",  # Support all target types
        project_root=root,  # Use root as project root for relative paths
    ):
        context_files.append(context_info)

    # Format the results using core formatters
    formatter = FormatterRegistry.get_formatter("json")
    result_json = await formatter.format_collection(
        context_files, DataType.CONTEXT_FILES, directory=root, tree_format=tree_format
    )
    result = json.loads(result_json)

    # Save to cache with 1 hour expiration
    cache.set(cache_key, result, expire=3600)

    print(f"   ✅ Found {len(result['context_files'])} context files in {root}")
    return root_id, {"path": root, "context_files": result["context_files"]}


async def discover_and_register_context(
    roots: List[str],
    context_data: Dict,
    context_data_lock: asyncio.Lock,
    session_context=None,
    respect_gitignore: bool = True,
    cli_excludes: List[str] = None,
    default_include: bool = False,
    tree_format: bool = False,
) -> None:
    """Discover context files from roots using async fs_walker with hierarchical filtering."""

    # Reset context data thread-safely
    async with context_data_lock:
        context_data.clear()
        context_data.update({"roots": {}, "all_files": []})

    # Create discovery tasks for parallel async execution
    # Create async tasks for parallel discovery (no need for thread executor anymore)
    discovery_tasks = [
        _discover_context_for_root(
            root,
            i,
            respect_gitignore,
            cli_excludes,
            default_include,
            roots,  # Pass all roots for level calculation
            tree_format,
        )
        for i, root in enumerate(roots)
    ]

    # Wait for all discoveries to complete in parallel
    results = await asyncio.gather(*discovery_tasks)

    # Merge results back in main thread with thread safety
    async with context_data_lock:
        for root_id, root_data in results:
            context_data["roots"][root_id] = root_data
            context_data["all_files"].extend(root_data["context_files"])

    file_list = "\n".join([f"     - {file}" for file in context_data["all_files"]])
    print(
        f"   ✅ Context discovery complete: {len(context_data['all_files'])} files found\n{file_list}"
    )

    # Notify MCP clients that resources have changed (in main async context)
    if session_context:
        try:
            await session_context.send_resource_list_changed()
            print(f"   📡 Sent resource list changed notification to MCP clients")
        except Exception as e:
            print(f"   ⚠️  Failed to send resource notification: {e}")
