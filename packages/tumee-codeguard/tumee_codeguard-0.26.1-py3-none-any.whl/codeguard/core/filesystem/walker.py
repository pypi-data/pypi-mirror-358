"""
Filesystem walker that can optionally inspect file content for guard tags.

This module unifies the 3 different implementations:
1. Context discovery (only reads .ai-attributes files)
2. Guard tag scanning (parses individual source files for guard tags)
3. Current context_walker (yields files but doesn't parse content)
"""

import asyncio
import logging
import pathlib
import time
from collections import deque
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from utils.profiling import detect_blocking_async

from ..factories import create_validator_from_args
from ..infrastructure.filtering import create_filter
from ..interfaces import IFileSystemAccess, IStaticAnalyzer

# Import for AI ownership security check
from ..language.config import is_ai_owned_module
from ..validation.guard_tag_extractor import extract_guard_tags_with_target_filter
from .traversal_utils import should_traverse_directory

logger = logging.getLogger(__name__)


async def fs_walk(
    filesystem_access,
    directory: Union[str, pathlib.Path],
    repo_path: Optional[Union[str, pathlib.Path]] = None,
    priority: Optional[str] = None,
    for_use: Optional[str] = None,
    respect_gitignore: bool = True,
    cli_excludes: Optional[List[str]] = None,
    default_include: bool = False,
    registered_roots: Optional[List[str]] = None,
    traversal_mode: str = "breadth_first",  # "breadth_first", "depth_first", "upward"
    target: str = "*",  # Which target to look for in guard tags (ai, human, * for all)
    project_root: Optional[Union[str, pathlib.Path]] = None,  # Project root for relative paths
    max_depth: Optional[
        int
    ] = None,  # Maximum depth to traverse (0=current level only, 1=one level down, etc.)
    yield_type: str = "files",  # "files", "directories", "both" - what to yield
    static_analyzer: Optional[IStaticAnalyzer] = None,  # If provided, enables content inspection
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Filesystem walker that can optionally inspect file content for guard tags.

    Args:
        filesystem_access: IFileSystemAccess instance for secure operations
        directory: Directory to search
        repo_path: Repository root path
        priority: Filter by priority level (high, medium, low)
        for_use: Filter by usage scope (testing, configuration, etc.)
        respect_gitignore: Whether to respect .gitignore files
        cli_excludes: Additional CLI exclude patterns
        default_include: Default policy for files with no rules
        registered_roots: List of registered root paths for level calculation
        traversal_mode: How to traverse the directory tree
        target: Target to look for when parsing guard tags ("ai" or "human")
        max_depth: Maximum depth to traverse (0=current level only, 1=one level down, etc.)
        yield_type: What to yield - "files", "directories", or "both"
        static_analyzer: If provided, enables content inspection and guard tag parsing

    Yields:
        Context file/directory information dictionaries with optional guard tag data
    """
    directory = pathlib.Path(directory).resolve()

    if traversal_mode == "upward":
        async for item in _walk_upward(
            filesystem_access,
            directory,
            repo_path,
            priority,
            for_use,
            registered_roots,
            target,
            project_root,
            max_depth,
            yield_type,
            static_analyzer,
        ):
            yield item
    elif traversal_mode == "depth_first":
        async for item in _walk_depth_first(
            filesystem_access,
            directory,
            repo_path,
            priority,
            for_use,
            respect_gitignore,
            cli_excludes,
            default_include,
            registered_roots,
            target,
            project_root,
            max_depth,
            yield_type,
            static_analyzer,
        ):
            yield item
    else:  # breadth_first (default)
        async for item in _walk_breadth_first(
            filesystem_access,
            directory,
            repo_path,
            priority,
            for_use,
            respect_gitignore,
            cli_excludes,
            default_include,
            registered_roots,
            target,
            project_root,
            max_depth,
            yield_type,
            static_analyzer,
        ):
            yield item


async def _walk_upward(
    filesystem_access,
    directory,
    repo_path,
    priority,
    for_use,
    registered_roots,
    target,
    project_root,
    max_depth,
    yield_type,
    static_analyzer: Optional[IStaticAnalyzer] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Walk UP from directory to find .ai-attributes files and optionally parse content."""

    # Walk UP from directory using async filesystem operations
    current_level = 0
    async for current_dir in filesystem_access.safe_traverse_upward(directory):
        await asyncio.sleep(0)  # Yield control to event loop
        # Check max_depth limit for upward traversal
        if max_depth is not None and current_level > max_depth:
            break

        current_level += 1

        # Yield directory if requested
        if yield_type in ("directories", "both"):
            try:
                relative_path = current_dir.relative_to(directory)
                level = len(relative_path.parts)
            except ValueError:
                try:
                    relative_path = directory.relative_to(current_dir)
                    level = -len(relative_path.parts)
                except ValueError:
                    relative_path = ""
                    level = -1

            directory_info = {
                "path": str(current_dir),
                "directory": str(current_dir.parent),
                "type": "directory",
                "filename": current_dir.name,
                "level": level,
                "relative_path": str(relative_path) if level >= 0 else str(current_dir),
                "is_directory": True,
            }

            if priority is None and for_use is None:
                yield directory_info

        # Check for .ai-attributes in current directory (only if yielding files)
        if yield_type in ("files", "both"):
            ai_attrs_file = current_dir / ".ai-attributes"

            if filesystem_access.safe_file_exists(ai_attrs_file):
                try:
                    # Always read .ai-attributes files
                    content = await filesystem_access.safe_read_file(ai_attrs_file)

                    # Calculate level for upward traversal
                    try:
                        relative_path = current_dir.relative_to(directory)
                        level = len(relative_path.parts)
                    except ValueError:
                        try:
                            relative_path = directory.relative_to(current_dir)
                            level = -len(relative_path.parts)
                        except ValueError:
                            level = -1

                    context_info = {
                        "path": str(ai_attrs_file),
                        "directory": str(current_dir),
                        "type": "ai_attributes",
                        "content": content,
                        "level": level,
                        "relative_path": (
                            str(ai_attrs_file.relative_to(directory))
                            if level >= 0
                            else str(ai_attrs_file)
                        ),
                    }

                    # Apply filters if specified
                    if priority is None and for_use is None:
                        yield context_info

                except Exception:
                    continue


async def _walk_breadth_first(
    filesystem_access,
    directory,
    repo_path,
    priority,
    for_use,
    respect_gitignore,
    cli_excludes,
    default_include,
    registered_roots,
    target,
    project_root,
    max_depth,
    yield_type,
    static_analyzer: Optional[IStaticAnalyzer] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Walk breadth-first and optionally inspect file content for guard tags."""

    # Create filter engine
    filter_engine = create_filter(
        respect_gitignore=respect_gitignore,
        use_ai_attributes=True,
        cli_excludes=cli_excludes,
        default_include=default_include,
        include_default_excludes=True,
    )

    # Create validator if we have a static analyzer (i.e., need to inspect content)
    validator = None
    if static_analyzer is not None:
        # Create minimal args for validator
        import argparse

        args = argparse.Namespace(
            normalize_whitespace=True,
            normalize_line_endings=True,
            ignore_blank_lines=True,
            ignore_indentation=False,
            context_lines=3,
            allowed_roots=None,
        )
        validator = create_validator_from_args(args)

    # Create gitignore cache once for the entire traversal
    gitignore_cache = {} if respect_gitignore else None

    # AI ownership cache to avoid repeated checks
    ai_ownership_cache = {}

    # Note: static_analyzer is now passed as a parameter when inspect_content=True

    # Performance tracking
    start_time = time.time()
    dirs_processed = 0
    items_yielded = 0

    # Implement breadth-first traversal
    dirs_to_process = deque([(directory, 0)])

    while dirs_to_process:
        await asyncio.sleep(0)  # Yield control to event loop
        current_dir, current_level = dirs_to_process.popleft()
        dirs_processed += 1

        try:
            # 🔒 SECURITY: Check if current directory is AI-owned (cached)
            current_dir_str = str(current_dir)
            if current_dir_str not in ai_ownership_cache:
                ai_ownership_cache[current_dir_str] = is_ai_owned_module(current_dir)

            if ai_ownership_cache[current_dir_str]:
                logger.debug(
                    f"🔒 SECURITY: Skipping AI-owned directory {current_dir} - access denied"
                )
                continue

            items = await filesystem_access.safe_list_directory(current_dir)

            # Process items based on yield_type
            for item in items:
                if item.is_file() and yield_type in ("files", "both"):
                    # Apply filtering
                    should_include, reason = filter_engine.should_include_file(item, directory)
                    if not should_include:
                        continue

                    # Calculate level and relative path
                    try:
                        relative_path = item.relative_to(directory)
                        level = len(relative_path.parts) - 1
                    except ValueError:
                        level = -1
                        relative_path = (
                            item.relative_to(current_dir) if current_dir != directory else item
                        )

                    try:
                        context_info = await _process_file(
                            filesystem_access,
                            item,
                            directory,
                            level,
                            relative_path,
                            target,
                            validator,
                            pathlib.Path(project_root) if project_root else None,
                            static_analyzer,
                        )

                        if context_info and (priority is None and for_use is None):
                            items_yielded += 1
                            yield context_info

                    except Exception:
                        continue

                elif item.is_dir() and yield_type in ("directories", "both"):
                    # Apply filtering to directories too
                    should_include, reason = filter_engine.should_include_file(item, directory)
                    if not should_include:
                        continue

                    # Calculate level and relative path for directory
                    try:
                        relative_path = item.relative_to(directory)
                        level = len(relative_path.parts) - 1
                    except ValueError:
                        level = -1
                        relative_path = (
                            item.relative_to(current_dir) if current_dir != directory else item
                        )

                    # Yield directory info
                    directory_info = {
                        "path": str(item),
                        "directory": str(item.parent),
                        "type": "directory",
                        "filename": item.name,
                        "level": level,
                        "relative_path": str(relative_path) if level >= 0 else str(item),
                        "is_directory": True,
                    }

                    if priority is None and for_use is None:
                        items_yielded += 1
                        yield directory_info

            # Add subdirectories to queue for next level (respecting max_depth and traversal rules)
            for item in items:
                if item.is_dir() and filesystem_access.is_path_allowed(item):
                    # Check max_depth limit
                    if max_depth is None or current_level < max_depth:
                        # Use shared traversal filtering logic
                        if should_traverse_directory(
                            item,
                            directory,
                            respect_gitignore,
                            gitignore_cache,
                            filesystem_access,
                            ai_ownership_cache,
                        ):
                            dirs_to_process.append((item, current_level + 1))

        except (OSError, PermissionError):
            continue

    # Log performance statistics
    elapsed_time = time.time() - start_time
    ai_cache_hit_rate = (
        ((len(ai_ownership_cache) - dirs_processed) / len(ai_ownership_cache) * 100)
        if ai_ownership_cache
        else 0
    )
    logger.debug(
        f"Breadth-first walker completed in {elapsed_time:.2f}s - {dirs_processed} dirs processed, {items_yielded} items yielded, AI cache entries: {len(ai_ownership_cache)}"
    )


async def _walk_depth_first(
    filesystem_access,
    directory,
    repo_path,
    priority,
    for_use,
    respect_gitignore,
    cli_excludes,
    default_include,
    registered_roots,
    target,
    project_root,
    max_depth,
    yield_type,
    static_analyzer: Optional[IStaticAnalyzer] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Walk depth-first and optionally inspect file content for guard tags."""

    # Create filter engine
    filter_engine = create_filter(
        respect_gitignore=respect_gitignore,
        use_ai_attributes=True,
        cli_excludes=cli_excludes,
        default_include=default_include,
        include_default_excludes=True,
    )

    # Create validator if we have a static analyzer (i.e., need to inspect content)
    validator = None
    if static_analyzer is not None:
        import argparse

        args = argparse.Namespace(
            normalize_whitespace=True,
            normalize_line_endings=True,
            ignore_blank_lines=True,
            ignore_indentation=False,
            context_lines=3,
            allowed_roots=None,
        )
        validator = create_validator_from_args(args)

    # Create gitignore cache once for the entire traversal
    gitignore_cache = {} if respect_gitignore else None

    # AI ownership cache to avoid repeated checks
    ai_ownership_cache = {}

    # Note: static_analyzer is now passed as a parameter when inspect_content=True

    async def depth_first_recursive(current_dir: pathlib.Path, current_level: int):
        try:
            # 🔒 SECURITY: Check if current directory is AI-owned (cached)
            current_dir_str = str(current_dir)
            if current_dir_str not in ai_ownership_cache:
                ai_ownership_cache[current_dir_str] = is_ai_owned_module(current_dir)

            if ai_ownership_cache[current_dir_str]:
                logger.debug(
                    f"🔒 SECURITY: Skipping AI-owned directory {current_dir} - access denied"
                )
                return

            items = await filesystem_access.safe_list_directory(current_dir)

            # Process items based on yield_type
            for item in items:
                await asyncio.sleep(0)  # Yield control to event loop
                if item.is_file() and yield_type in ("files", "both"):
                    should_include, reason = filter_engine.should_include_file(item, directory)
                    if not should_include:
                        continue

                    try:
                        relative_path = item.relative_to(directory)
                        level = len(relative_path.parts) - 1
                    except ValueError:
                        level = -1
                        relative_path = (
                            item.relative_to(current_dir) if current_dir != directory else item
                        )

                    try:
                        context_info = await _process_file(
                            filesystem_access,
                            item,
                            directory,
                            level,
                            relative_path,
                            target,
                            validator,
                            pathlib.Path(project_root) if project_root else None,
                            static_analyzer,
                        )

                        if context_info and (priority is None and for_use is None):
                            yield context_info

                    except Exception:
                        continue

                elif item.is_dir() and yield_type in ("directories", "both"):
                    # Apply filtering to directories too
                    should_include, reason = filter_engine.should_include_file(item, directory)
                    if not should_include:
                        continue

                    # Calculate level and relative path for directory
                    try:
                        relative_path = item.relative_to(directory)
                        level = len(relative_path.parts) - 1
                    except ValueError:
                        level = -1
                        relative_path = (
                            item.relative_to(current_dir) if current_dir != directory else item
                        )

                    # Yield directory info
                    directory_info = {
                        "path": str(item),
                        "directory": str(item.parent),
                        "type": "directory",
                        "filename": item.name,
                        "level": level,
                        "relative_path": str(relative_path) if level >= 0 else str(item),
                        "is_directory": True,
                    }

                    if priority is None and for_use is None:
                        yield directory_info

            # Recursively process subdirectories (respecting max_depth and traversal rules)
            for item in items:
                await asyncio.sleep(0)  # Yield control to event loop
                if item.is_dir() and filesystem_access.is_path_allowed(item):
                    # Check max_depth limit
                    if max_depth is None or current_level < max_depth:
                        # Use shared traversal filtering logic
                        if should_traverse_directory(
                            item,
                            directory,
                            respect_gitignore,
                            gitignore_cache,
                            filesystem_access,
                            ai_ownership_cache,
                        ):
                            async for subitem in depth_first_recursive(item, current_level + 1):
                                yield subitem

        except (OSError, PermissionError):
            pass

    async for item in depth_first_recursive(directory, 0):
        yield item


@detect_blocking_async(max_yield_gap_ms=100.0, log_args=True)
async def _process_file(
    filesystem_access,
    item: Path,
    directory: Path,
    level: int,
    relative_path: Path,
    target: str,
    validator,
    project_root: Optional[Path] = None,
    static_analyzer: Optional[IStaticAnalyzer] = None,
) -> Optional[Dict[str, Any]]:
    """
    Process a single file, optionally using static analyzer for comprehensive analysis.

    This unifies the 3 different approaches:
    1. If static_analyzer is None: Only read .ai-attributes files (context discovery approach)
    2. If static_analyzer provided: Use static analyzer for comprehensive analysis
    """

    if item.name == ".ai-attributes":
        # Always read .ai-attributes files - these are processed differently
        file_type = "ai_attributes"
        content = await filesystem_access.safe_read_file(item)

        context_info = {
            "path": str(item),
            "directory": str(item.parent),
            "type": file_type,
            "filename": item.name,
            "level": level,
            "relative_path": str(relative_path) if level >= 0 else str(item),
            "content": content,
        }
        return context_info

    # For regular files, use static analyzer if provided
    if static_analyzer is None:
        # Just return basic file info without content analysis
        return {
            "path": str(item),
            "directory": str(item.parent),
            "type": "context_file",
            "filename": item.name,
            "level": level,
            "relative_path": str(relative_path) if level >= 0 else str(item),
            "has_guard_tags": False,
        }

    # Use static analyzer for comprehensive analysis
    try:
        file_content = await filesystem_access.safe_read_file(item)

        # Add periodic yield for responsiveness during parsing
        await asyncio.sleep(0)

        # Use StaticAnalyzer for comprehensive analysis (created once per walker operation)
        analysis = await static_analyzer.analyze_file(str(item))

        # When static_analyzer provided, only return files with context tags
        # When static_analyzer is None, return all files (handled elsewhere in function)
        if static_analyzer is not None and not analysis.get("has_context_tags", False):
            return None

        # Convert StaticAnalyzer result to context_info format
        context_info = {
            "path": str(item),
            "directory": str(item.parent),
            "type": "context_file",
            "filename": item.name,
            "level": level,
            "relative_path": str(relative_path),
            "has_guard_tags": analysis.get("has_context_tags", False),
            # Add comprehensive metadata when available
            "file_metadata": {
                "size_bytes": analysis.get("size_bytes", 0),
                "line_count": analysis.get("line_count", 0),
            },
            "language_id": analysis.get("language", "unknown"),
            "tree_sitter_metrics": analysis.get("tree_sitter_metrics", {}),
            "content_rule_applied": "full_file",  # Static analyzer always does full file
            "analysis_success": "error" not in analysis,
        }

        # Add context regions if any were found
        if analysis.get("context_regions"):
            context_info["context_regions"] = analysis["context_regions"]

        # Add error information if analysis failed
        if "error" in analysis:
            context_info["error"] = analysis["error"]

        return context_info

    except Exception as e:
        # Fallback - return basic info with error
        return {
            "path": str(item),
            "directory": str(item.parent),
            "type": "context_file",
            "filename": item.name,
            "level": level,
            "relative_path": str(relative_path) if level >= 0 else str(item),
            "has_guard_tags": False,
            "error": f"Failed to analyze file: {e}",
            "analysis_success": False,
        }


# Convenience functions that wrap the fs_walker for backward compatibility


async def get_context_files_breadth_first(
    filesystem_access,
    directory: Union[str, pathlib.Path],
    repo_path: Optional[Union[str, pathlib.Path]] = None,
    priority: Optional[str] = None,
    for_use: Optional[str] = None,
    respect_gitignore: bool = True,
    cli_excludes: Optional[List[str]] = None,
    default_include: bool = False,
    registered_roots: Optional[List[str]] = None,
    target: str = "*",
    project_root: Optional[Union[str, pathlib.Path]] = None,
    max_depth: Optional[int] = None,
    static_analyzer: Optional[IStaticAnalyzer] = None,
) -> AsyncGenerator[Dict, None]:
    """Breadth-first context discovery with optional content inspection."""
    async for item in fs_walk(
        filesystem_access,
        directory,
        repo_path,
        priority,
        for_use,
        respect_gitignore,
        cli_excludes,
        default_include,
        registered_roots,
        traversal_mode="breadth_first",
        target=target,
        project_root=project_root,
        max_depth=max_depth,
        static_analyzer=static_analyzer,
    ):
        yield item


async def get_context_files_depth_first(
    filesystem_access,
    directory: Union[str, pathlib.Path],
    repo_path: Optional[Union[str, pathlib.Path]] = None,
    priority: Optional[str] = None,
    for_use: Optional[str] = None,
    respect_gitignore: bool = True,
    cli_excludes: Optional[List[str]] = None,
    default_include: bool = False,
    registered_roots: Optional[List[str]] = None,
    target: str = "ai",
    project_root: Optional[Union[str, pathlib.Path]] = None,
    max_depth: Optional[int] = None,
    static_analyzer: Optional[IStaticAnalyzer] = None,
) -> AsyncGenerator[Dict, None]:
    """Depth-first context discovery with optional content inspection."""
    async for item in fs_walk(
        filesystem_access,
        directory,
        repo_path,
        priority,
        for_use,
        respect_gitignore,
        cli_excludes,
        default_include,
        registered_roots,
        traversal_mode="depth_first",
        target=target,
        project_root=project_root,
        max_depth=max_depth,
        static_analyzer=static_analyzer,
    ):
        yield item


async def get_context_files_upward(
    filesystem_access,
    directory: Union[str, pathlib.Path],
    repo_path: Optional[Union[str, pathlib.Path]] = None,
    priority: Optional[str] = None,
    for_use: Optional[str] = None,
    registered_roots: Optional[List[str]] = None,
    target: str = "ai",
    project_root: Optional[Union[str, pathlib.Path]] = None,
    max_depth: Optional[int] = None,
    static_analyzer: Optional[IStaticAnalyzer] = None,
) -> AsyncGenerator[Dict, None]:
    """Upward context discovery with optional content inspection."""
    async for item in fs_walk(
        filesystem_access,
        directory,
        repo_path,
        priority,
        for_use,
        registered_roots=registered_roots,
        traversal_mode="upward",
        target=target,
        project_root=project_root,
        static_analyzer=static_analyzer,
        max_depth=max_depth,
    ):
        yield item
