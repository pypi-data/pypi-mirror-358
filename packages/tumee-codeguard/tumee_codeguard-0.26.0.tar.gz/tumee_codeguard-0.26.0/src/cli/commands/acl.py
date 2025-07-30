"""
ACL and context CLI commands for CodeGuard.
Handles access control list operations and context file management.
"""

import argparse
from pathlib import Path
from typing import List, Optional, Sequence, Union

from ...context.analyzers.static_analyzer import StaticAnalyzer
from ...core.factories import create_validator_from_args
from ...core.filesystem.walker import (
    _process_file,
    get_context_files_breadth_first,
    get_context_files_depth_first,
    get_context_files_upward,
)
from ...core.formatters.base import DataType, FormatterRegistry
from ...core.infrastructure.filtering import create_filter
from ...core.security.permissions import PermissionResolver
from ...core.validation.directory_guard import DirectoryGuard
from ...core.validation.validator import CodeGuardValidator


async def cmd_acl(args: argparse.Namespace) -> int:
    """
    Execute the 'acl' command to get effective permissions for a file or directory.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        return 1

    try:
        # Create validator with filesystem access
        validator = create_validator_from_args(args)

        # Get effective permissions asynchronously
        result = await format_effective_permissions(
            validator.fs,
            path=path,
            repo_path=args.repo_path,
            verbose=args.verbose,
            recursive=args.recursive,
            format=args.format,
            identifier=getattr(args, "identifier", None),
            include_context=getattr(args, "include_context", False),
        )

        # Output the result
        print(result)

        return 0
    except Exception as e:
        print(f"Error getting effective permissions: {str(e)}")
        return 1


async def cmd_batch_acl(args: argparse.Namespace) -> int:
    """
    Execute the 'batch-acl' command to get permissions for multiple paths.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    # Convert paths to Path objects and validate
    paths = [Path(p) for p in args.paths]
    invalid_paths = [p for p in paths if not p.exists()]

    if invalid_paths:
        print(f"Error: The following paths do not exist:")
        for p in invalid_paths:
            print(f"  - {p}")
        return 1

    try:
        # Create validator with filesystem access
        validator = create_validator_from_args(args)

        # Get batch permissions
        result = await format_batch_permissions(
            filesystem_access=validator.fs,
            validator=validator,
            paths=paths,
            repo_path=args.repo_path,
            verbose=args.verbose,
            format=args.format,
        )

        # Output the result
        print(result)

        return 0
    except Exception as e:
        print(f"Error getting batch permissions: {str(e)}")
        return 1


async def cmd_context_up_direct(args: argparse.Namespace) -> int:
    """
    Execute the 'context-up-direct' command to get context files by walking UP from directory.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    directory = Path(args.directory)

    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        return 1

    try:
        # Create validator with filesystem access
        validator = create_validator_from_args(args)

        # Determine project root (use repo_path if available, otherwise directory)
        project_root = Path(args.repo_path) if args.repo_path else directory

        # Get context files using upward traversal with fs_walker
        context_files = []
        # Create static analyzer for content inspection
        static_analyzer = StaticAnalyzer(validator.fs)
        async for context_info in get_context_files_upward(
            filesystem_access=validator.fs,
            directory=directory,
            repo_path=args.repo_path,
            priority=args.priority,
            for_use=args.for_use,
            registered_roots=getattr(args, "allowed_roots", None),
            target=getattr(args, "target", "*"),  # Use CLI target parameter, default to all types
            project_root=project_root,
            static_analyzer=static_analyzer,  # Enable content inspection
        ):
            context_files.append(context_info)

        # Calculate verbosity level (-1=quiet, 0=normal, 1+=verbose)
        quiet = getattr(args, "quiet", False)
        verbose = getattr(args, "verbose", False)
        verbosity = -1 if quiet else (1 if verbose else 0)

        # Format using core formatters
        formatter = FormatterRegistry.get_formatter(args.format.lower())
        if formatter:
            result = await formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=directory,
                traversal="upward",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )
        else:
            # Fallback to JSON
            json_formatter = FormatterRegistry.get_formatter("json")
            if json_formatter is None:
                raise RuntimeError("JSON formatter not available")
            result = await json_formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=directory,
                traversal="upward",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )

        # Output the result
        print(result)

        return 0
    except Exception as e:
        print(f"Error getting context files with upward traversal: {str(e)}")
        return 1


async def cmd_context_down_deep(args: argparse.Namespace) -> int:
    """
    Execute the 'context-down-deep' command to recursively search all context files depth-first.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    directory = Path(args.directory)

    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        return 1

    try:
        # Create validator with filesystem access
        validator = create_validator_from_args(args)

        # Determine project root (use repo_path if available, otherwise directory)
        project_root = Path(args.repo_path) if args.repo_path else directory

        # Get context files using depth-first traversal with fs_walker
        context_files = []
        # Create static analyzer for content inspection
        static_analyzer = StaticAnalyzer(validator.fs)
        async for context_info in get_context_files_depth_first(
            filesystem_access=validator.fs,
            directory=directory,
            repo_path=args.repo_path,
            priority=args.priority,
            for_use=None,
            respect_gitignore=True,
            cli_excludes=getattr(args, "excludes", None),
            default_include=True,  # Include files by default so we can inspect content for context tags
            registered_roots=getattr(args, "allowed_roots", None),
            target=getattr(args, "target", "*"),  # Use CLI target parameter, default to all types
            project_root=project_root,
            static_analyzer=static_analyzer,  # Enable content inspection
        ):
            context_files.append(context_info)

        # Calculate verbosity level (-1=quiet, 0=normal, 1+=verbose)
        quiet = getattr(args, "quiet", False)
        verbose = getattr(args, "verbose", False)
        verbosity = -1 if quiet else (1 if verbose else 0)

        # Format using core formatters
        formatter = FormatterRegistry.get_formatter(args.format.lower())
        if formatter:
            result = await formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=directory,
                traversal="depth-first",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )
        else:
            # Fallback to JSON
            json_formatter = FormatterRegistry.get_formatter("json")
            if json_formatter is None:
                raise RuntimeError("JSON formatter not available")
            result = await json_formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=directory,
                traversal="depth-first",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )

        # Output the result
        print(result)

        return 0
    except Exception as e:
        print(f"Error getting context files: {str(e)}")
        return 1


async def cmd_context_down_wide(args: argparse.Namespace) -> int:
    """
    Execute the 'context-down-wide' command to search all context files breadth-first.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """

    directory = Path(args.directory)

    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        return 1

    try:
        # Create validator with filesystem access
        validator = create_validator_from_args(args)

        # Determine project root (use repo_path if available, otherwise directory)
        project_root = Path(args.repo_path) if args.repo_path else directory

        # Get context files using breadth-first traversal with fs_walker
        context_files = []
        # Create static analyzer for content inspection
        static_analyzer = StaticAnalyzer(validator.fs)
        async for context_info in get_context_files_breadth_first(
            filesystem_access=validator.fs,
            directory=directory,
            repo_path=args.repo_path,
            priority=args.priority,
            for_use=args.for_use,
            respect_gitignore=True,
            cli_excludes=getattr(args, "excludes", None),
            default_include=False,
            registered_roots=getattr(args, "allowed_roots", None),
            target="both",  # Support both AI and human guard tags
            project_root=project_root,
            static_analyzer=static_analyzer,  # Enable content inspection
        ):
            context_files.append(context_info)

        # Calculate verbosity level (-1=quiet, 0=normal, 1+=verbose)
        quiet = getattr(args, "quiet", False)
        verbose = getattr(args, "verbose", False)
        verbosity = -1 if quiet else (1 if verbose else 0)

        # Format using core formatters
        formatter = FormatterRegistry.get_formatter(args.format.lower())
        if formatter:
            result = await formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=directory,
                traversal="breadth-first",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )
        else:
            # Fallback to JSON
            json_formatter = FormatterRegistry.get_formatter("json")
            if json_formatter is None:
                raise RuntimeError("JSON formatter not available")
            result = await json_formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=directory,
                traversal="breadth-first",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )

        # Output the result
        print(result)

        return 0
    except Exception as e:
        print(f"Error getting context files with breadth-first search: {str(e)}")
        return 1


async def cmd_context_path(args: argparse.Namespace) -> int:
    """
    Execute the 'context-path' command to scan a single file or directory (no subdirs).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    target_path = Path(args.path)

    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}")
        return 1

    try:
        # Create validator with filesystem access
        validator = create_validator_from_args(args)

        # Determine project root (use repo_path if available, otherwise target's parent)
        project_root = (
            Path(args.repo_path)
            if args.repo_path
            else target_path.parent if target_path.is_file() else target_path
        )

        context_files = []

        if target_path.is_file():
            # Single file - process it directly
            relative_path = target_path.name  # Just the filename for a single file
            level = 0  # Single file is at level 0

            # Create StaticAnalyzer for file processing
            static_analyzer = StaticAnalyzer(validator.fs)

            context_info = await _process_file(
                validator.fs,
                target_path,
                target_path.parent,
                level,
                Path(relative_path),
                target=getattr(args, "target", "*"),
                validator=validator,
                project_root=project_root,
                static_analyzer=static_analyzer,
            )

            if context_info:
                context_files.append(context_info)
        else:
            # Directory - use depth-first walker with max_depth=0 to scan only the target level
            # Create static analyzer for content inspection
            static_analyzer = StaticAnalyzer(validator.fs)
            async for context_info in get_context_files_depth_first(
                filesystem_access=validator.fs,
                directory=target_path,
                repo_path=args.repo_path,
                priority=args.priority,
                for_use=None,
                respect_gitignore=True,
                cli_excludes=getattr(args, "excludes", None),
                default_include=True,  # Need to inspect content for context tags
                registered_roots=getattr(args, "allowed_roots", None),
                target=getattr(
                    args, "target", "*"
                ),  # Use CLI target parameter, default to all types
                static_analyzer=static_analyzer,  # Enable content inspection
                project_root=project_root,
                max_depth=0,  # Only scan current level, no subdirectories
            ):
                context_files.append(context_info)

        # Calculate verbosity level (-1=quiet, 0=normal, 1+=verbose)
        quiet = getattr(args, "quiet", False)
        verbose = getattr(args, "verbose", False)
        verbosity = -1 if quiet else (1 if verbose else 0)

        # Format using core formatters
        formatter = FormatterRegistry.get_formatter(args.format.lower())
        if formatter:
            result = await formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=target_path,
                traversal="path",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )
        else:
            # Fallback to JSON
            json_formatter = FormatterRegistry.get_formatter("json")
            if json_formatter is None:
                raise RuntimeError("JSON formatter not available")
            result = await json_formatter.format_collection(
                context_files,
                DataType.CONTEXT_FILES,
                directory=target_path,
                traversal="path",
                tree_format=getattr(args, "tree", False),
                verbosity=verbosity,
            )

        # Output the result
        print(result)

        return 0
    except Exception as e:
        print(f"Error scanning path: {str(e)}")
        return 1


# CLI wrapper functions moved from core/security/acl.py
# These are CLI business logic that format and parse arguments


async def format_effective_permissions(
    filesystem_access,
    path: Union[str, Path],
    repo_path: Optional[Union[str, Path]] = None,
    verbose: bool = False,
    recursive: bool = False,
    format: str = "json",
    identifier: Optional[str] = None,
    include_context: bool = False,
) -> str:
    """
    Format effective permissions for a path for CLI output.

    This is a CLI wrapper that handles argument processing, validator setup,
    and output formatting around the core permission resolution logic.

    Args:
        filesystem_access: FileSystemAccess instance for secure operations
        path: Path to get permissions for
        repo_path: Repository root path
        verbose: Whether to include detailed source information
        recursive: Whether to recursively check children (for directories)
        format: Output format (json, yaml, text)
        identifier: Specific identifier (e.g., "claude-4", "security-team")
        include_context: Whether to include context file information

    Returns:
        Formatted permissions information as string
    """
    # Create validator with the provided filesystem access (don't create new one)
    validator = CodeGuardValidator(
        filesystem_access=filesystem_access,
        normalize_whitespace=True,
        normalize_line_endings=True,
        ignore_blank_lines=True,
        ignore_indentation=False,
        context_lines=3,
        enable_directory_guards=True,
    )

    # Create directory guard for this specific repo if repo_path provided
    directory_guard = None
    if repo_path:
        repo_path = Path(repo_path).resolve()
        directory_guard = DirectoryGuard(filesystem_access, root_directory=repo_path)
        # Load rules from the repo directory upward to enable proper context detection
        await directory_guard.load_rules_from_directory(filesystem_access, repo_path)

    # Get permissions asynchronously, passing the specific directory guard
    # Use format="raw" to get dictionary instead of formatted string
    permissions = await validator.get_effective_permissions(
        filesystem_access,
        path=path,
        verbose=verbose,
        recursive=recursive,
        directory_guard=directory_guard,
        format="raw",
        include_context=include_context,
    )

    # Filter by identifier if provided
    if identifier and isinstance(permissions, dict) and "permissions" in permissions:
        # Filter permissions by identifier
        perms_dict = permissions["permissions"]
        if (
            isinstance(perms_dict, dict)
            and "ai" in perms_dict
            and isinstance(perms_dict["ai"], dict)
        ):
            # If AI permissions are detailed (with identifiers), filter them
            ai_perms = perms_dict["ai"]
            if identifier in ai_perms:
                perms_dict["ai"] = {identifier: ai_perms[identifier]}
            else:
                # Identifier not found, return none
                perms_dict["ai"] = {identifier: "none"}

    # Context detection is now handled by the permission resolver
    # No need for duplicate logic here

    # Format output using core formatters
    formatter = FormatterRegistry.get_formatter(format.lower())
    if formatter:
        return await formatter.format_collection(
            [permissions], DataType.ACL_PERMISSIONS, verbose=verbose, recursive=recursive
        )
    else:
        # Fallback to JSON if format not found
        json_formatter = FormatterRegistry.get_formatter("json")
        if json_formatter is None:
            raise RuntimeError("JSON formatter not available")
        return await json_formatter.format_collection(
            [permissions], DataType.ACL_PERMISSIONS, verbose=verbose, recursive=recursive
        )


async def format_batch_permissions(
    filesystem_access,
    validator: CodeGuardValidator,
    paths: Sequence[Union[str, Path]],
    repo_path: Optional[Union[str, Path]] = None,
    verbose: bool = False,
    format: str = "json",
) -> str:
    """
    Format permissions for multiple paths in a batch for CLI output.

    This is a CLI wrapper that handles batch processing and output formatting
    around the core permission resolution logic.

    Args:
        filesystem_access: FileSystemAccess instance for secure operations
        validator: CodeGuardValidator instance for validation operations
        paths: List of paths to get permissions for
        repo_path: Repository root path
        verbose: Whether to include detailed source information
        format: Output format (json, yaml, text)

    Returns:
        Formatted batch permissions information as string
    """

    # Get permissions for each path asynchronously
    results = []
    async for result in format_batch_permissions_generator(
        filesystem_access, validator, paths, repo_path, verbose
    ):
        results.append(result)

    # Create response
    response = {"batch_results": results, "total": len(results), "status": "success"}

    # Format output using core formatters
    formatter = FormatterRegistry.get_formatter(format.lower())
    if formatter:
        return await formatter.format_collection([response], DataType.ACL_PERMISSIONS, batch=True)
    else:
        # Fallback to JSON if format not found
        json_formatter = FormatterRegistry.get_formatter("json")
        if json_formatter is None:
            raise RuntimeError("JSON formatter not available")
        return await json_formatter.format_collection(
            [response], DataType.ACL_PERMISSIONS, batch=True
        )


async def format_batch_permissions_generator(
    filesystem_access,
    validator: CodeGuardValidator,
    paths: Sequence[Union[str, Path]],
    repo_path: Optional[Union[str, Path]] = None,
    verbose: bool = False,
):
    """
    Async generator to format permissions for multiple paths.

    This is a CLI wrapper generator that processes multiple paths and yields
    formatted permission information for each path.

    Args:
        filesystem_access: FileSystemAccess instance for secure operations
        validator: CodeGuardValidator instance for validation operations
        paths: List of paths to get permissions for
        repo_path: Repository root path
        verbose: Whether to include detailed source information

    Yields:
        Formatted permission information dictionaries for each path
    """

    # Process each path async
    for path in paths:
        try:
            # Check if path exists using filesystem access
            path_obj = Path(path)
            if filesystem_access.safe_file_exists(
                path_obj
            ) or filesystem_access.safe_directory_exists(path_obj):
                permissions = await validator.get_effective_permissions(
                    filesystem_access, path=path, verbose=verbose, recursive=False
                )
                yield permissions
            else:
                yield {
                    "path": str(path),
                    "status": "error",
                    "error": "Path not found or not accessible",
                }
        except Exception as e:
            yield {"path": str(path), "status": "error", "error": str(e)}
