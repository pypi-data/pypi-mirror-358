#!/usr/bin/env python3
"""
CodeGuard CLI 2.0 - Typer-based implementation
Clean, consistent, and user-friendly command interface
"""

import argparse
import asyncio
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import click
import typer
import yaml

from ..core.console_shared import CONSOLE, cprint, set_output_level_from_flags
from ..core.decorators.filesystem import with_filesystem_access
from ..core.discovery_config import set_discovery_config_from_cli
from ..core.exit_codes import (
    SUCCESS,
    UNEXPECTED_ERROR,
)
from ..core.factories.filesystem import create_filesystem_access_from_args
from ..core.formatters.base import BaseFormatter
from ..core.infrastructure.cli_utils import (
    buildargs,
    handle_cli_errors,
)
from ..core.project.hierarchy_display import format_hierarchy_display_for_server
from ..core.runtime import get_default_console
from ..ide.worker_mode import start_worker_mode
from ..utils.logging_config import get_logger
from ..utils.signal_handlers import SignalManager
from ..version import __version__
from .commands.p2p import p2p_app
from .commands.prompt_inject import prompt_app
from .commands.setup import setup_app
from .commands.smart_notes import smart_app
from .commands.ssl import ssl_app
from .commands.sys import sys_app

# Initialize console and logger
console = get_default_console()
logger = get_logger(__name__)


# === BOILERPLATE REDUCTION HELPERS ===


# Global state for allowed roots
_allowed_roots = None


def setup_command_progress(
    output_format: str,
    component_specs: Optional[List] = None,
    phase: str = "Starting",
    message: str = "Initializing...",
    quiet: bool = False,
    total_expected_work: Optional[int] = None,
) -> BaseFormatter:
    """
    Common function to set up progress formatting for any command.

    Args:
        output_format: Output format (console, table, json, etc.)
        component_specs: Component specifications for the command
        phase: Initial phase message
        message: Initial progress message
        quiet: Whether to suppress output
        total_expected_work: Total expected work units (overrides default calculation)

    Returns:
        BaseFormatter instance (use formatter.create_progress_callback() for callback)
    """
    from ..core.progress.progress_factory import setup_unified_progress

    # Get worker mode from environment (set by worker service)
    worker_mode = os.environ.get("CODEGUARD_WORKER_MODE", "")

    # Determine if we should show progress
    show_progress = output_format.lower() in ["console", "table"] and not quiet

    # Always create formatter - it decides whether to display based on show_progress
    progress_formatter = setup_unified_progress(
        worker_mode=worker_mode,
        component_specs=component_specs or [],
        show_progress=show_progress,
        total_expected_work=total_expected_work,
    )

    # Show progress IMMEDIATELY
    if total_expected_work is not None:
        overall_total = total_expected_work
    else:
        overall_total = len(component_specs) + 1 if component_specs else 1  # +1 for routing step
    asyncio.run(
        progress_formatter.show_progress(
            phase=phase,
            message=message,
            overall_total=overall_total,
            overall_current=0,
        )
    )

    return progress_formatter


# Main application
app = typer.Typer(
    name="codeguard",
    help="Code Change Detection and Guard Validation Tool",
    rich_markup_mode="rich",
    add_completion=True,
)


# === CORE COMMANDS ===


@app.command()
@handle_cli_errors
def verify(
    original: Path,
    modified: Optional[Path] = typer.Argument(
        None, help="Modified file (if not provided, compares to disk)"
    ),
    git_revision: Optional[str] = typer.Option(
        None, "--git-revision", help="Compare to git revision instead"
    ),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Process directories recursively"
    ),
    include: Optional[str] = typer.Option(None, "--include", help="Include pattern (e.g., '*.py')"),
    exclude: List[str] = typer.Option([], "--exclude", help="Exclude patterns"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    target: str = typer.Option("human", "--target", help="Target audience: ai, human, all"),
    context_lines: int = typer.Option(3, "--context-lines", help="Context lines around changes"),
    report: Optional[Path] = typer.Option(None, "--report", help="Save report to file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Compare files or directories for guard violations."""
    from .commands.file_commands import cmd_verify, cmd_verify_disk, cmd_verify_git
    from .p2p_integration import execute_with_p2p_routing

    # Prepare arguments for P2P routing
    command_args = {
        "original": str(original),
        "modified": str(modified) if modified else None,
        "git_revision": git_revision,
        "recursive": recursive,
        "include": include,
        "exclude": exclude,
        "output_format": output_format,
        "output": str(output) if output else None,
        "target": target,
        "context_lines": context_lines,
        "report": str(report) if report else None,
        "quiet": quiet,
        "verbose": verbose,
    }

    # Define local execution function
    async def local_execute(args_dict):
        if git_revision:
            args = (
                buildargs(
                    file=str(original),
                    revision=git_revision,
                    repo_path=None,
                    report=str(report) if report else None,
                    target=target,
                    context_lines=context_lines,
                    console_style="detailed",
                    no_content=False,
                    no_diff=False,
                    max_content_lines=10,
                    normalize_whitespace=True,
                    normalize_line_endings=True,
                    ignore_blank_lines=True,
                    ignore_indentation=False,
                )
                .add_common_args(quiet, verbose, output_format, output, _allowed_roots)
                .add_filtering_args(include, exclude, recursive)
                .build()
            )
            return await cmd_verify_git(args)
        elif modified is None:
            args = (
                buildargs(
                    modified=str(original),
                    report=str(report) if report else None,
                    target=target,
                    context_lines=context_lines,
                    console_style="detailed",
                    no_content=False,
                    no_diff=False,
                    max_content_lines=10,
                    normalize_whitespace=True,
                    normalize_line_endings=True,
                    ignore_blank_lines=True,
                    ignore_indentation=False,
                )
                .add_common_args(quiet, verbose, output_format, output, _allowed_roots)
                .add_filtering_args(include, exclude, recursive)
                .build()
            )
            return await cmd_verify_disk(args)
        else:
            args = (
                buildargs(
                    original=str(original),
                    modified=str(modified),
                    report=str(report) if report else None,
                    target=target,
                    context_lines=context_lines,
                    console_style="detailed",
                    no_content=False,
                    no_diff=False,
                    max_content_lines=10,
                    normalize_whitespace=True,
                    normalize_line_endings=True,
                    ignore_blank_lines=True,
                    ignore_indentation=False,
                )
                .add_common_args(quiet, verbose, output_format, output)
                .add_filtering_args(include, exclude, recursive)
                .build()
            )
            return await cmd_verify(args)

    # Create filesystem access for verify command
    fs_args = argparse.Namespace()
    fs_args.allowed_roots = [str(original.parent.resolve())]
    filesystem_access = create_filesystem_access_from_args(fs_args)

    # Use common function to set up progress
    progress_formatter = setup_command_progress(
        output_format=output_format,
        component_specs=[],  # Verify command doesn't use components
        phase="Starting verification",
        message="Initializing...",
        quiet=quiet,
    )
    progress_callback = progress_formatter.create_progress_callback()

    # Capture original command line for P2P execution
    original_command_line = " ".join(sys.argv[1:])

    # Execute with P2P routing
    return asyncio.run(
        execute_with_p2p_routing(
            filesystem_access=filesystem_access,
            progress_callback=progress_callback,
            command_name="verify",
            command_args=command_args,
            subcommand=None,
            local_executor_func=local_execute,
            original_command_line=original_command_line,
        )
    )


@app.command()
@handle_cli_errors
@with_filesystem_access()
def tags(
    directory: Path = typer.Argument(Path("."), help="Directory or file to analyze"),
    filesystem_access=typer.Option(None, hidden=True),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", "-r", help="Search recursively"
    ),
    include: Optional[str] = typer.Option(None, "--include", help="Include pattern"),
    exclude: List[str] = typer.Option([], "--exclude", help="Exclude patterns"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    count_only: bool = typer.Option(False, "--count-only", help="Show only tag counts"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed tag information"),
):
    """Report guard tag locations and counts in files."""
    from .commands.file_commands import cmd_tags

    return asyncio.run(
        cmd_tags(
            directory=directory,
            filesystem_access=filesystem_access,
            include=include,
            exclude=exclude,
            recursive=recursive,
            quiet=False,
            verbose=verbose,
            count_only=count_only,
            format=output_format,
            output=output,
        )
    )


@app.command()
@handle_cli_errors
def show(
    file: Path,
    theme: Optional[str] = typer.Option(None, "--theme", help="Visualization theme"),
    syntax: bool = typer.Option(False, "--syntax", help="Show syntax node types"),
    color: bool = typer.Option(True, "--color/--no-color", help="Enable colored output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Display file with guard permission visualization."""
    from .commands.themes import cmd_showfile

    return asyncio.run(
        cmd_showfile(
            buildargs(file=file, theme=theme, syntax=syntax, color=color)
            .add_common_args(quiet, verbose, allowed_roots=_allowed_roots)
            .build()
        )
    )


@app.command()
@handle_cli_errors
def acl(
    path: Path,
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Check recursively"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Detailed information"),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format"),
    identifier: Optional[str] = typer.Option(None, "--identifier", help="Specific identifier"),
    include_context: bool = typer.Option(False, "--include-context", help="Include context info"),
    repo_path: Optional[Path] = typer.Option(None, "--repo-path", help="Repository root path"),
):
    """Get effective permissions for file or directory."""
    from .commands.acl import cmd_acl

    return asyncio.run(
        cmd_acl(
            buildargs(
                path=path,
                identifier=identifier,
                include_context=include_context,
                repo_path=repo_path,
            )
            .add_common_args(False, verbose, output_format, allowed_roots=_allowed_roots)
            .add_filtering_args(recursive=recursive)
            .build()
        )
    )


# === CONTEXT COMMANDS ===
context_app = typer.Typer(
    name="context",
    help="Context file discovery with three traversal modes: up, down, wide.\n\n"
    "💡 TIP: Use 'codeguard context COMMAND --help' for all options.\n"
    "📖 Use 'codeguard --help --full' for complete documentation.",
)


@context_app.command("up")
@handle_cli_errors
def context_up(
    directory: Path = typer.Argument(Path("."), help="Starting directory"),
    priority: Optional[str] = typer.Option(
        None, "--priority", help="Filter by priority: high, medium, low"
    ),
    for_use: Optional[str] = typer.Option(None, "--for", help="Filter by usage scope"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    tree: bool = typer.Option(False, "--tree", help="Tree-style output"),
    repo_path: Optional[Path] = typer.Option(None, "--repo-path", help="Repository root"),
    target: str = typer.Option("*", "--target", help="Target audience: ai, human, * (default: *)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Walk UP from directory to find context files."""
    from .commands.acl import cmd_context_up_direct

    return asyncio.run(
        cmd_context_up_direct(
            buildargs(directory=directory)
            .add_common_args(quiet, verbose, output_format, allowed_roots=_allowed_roots)
            .add_context_args(priority, for_use, tree, repo_path, target)
            .build()
        )
    )


@context_app.command("down")
@handle_cli_errors
def context_down(
    directory: Path = typer.Argument(Path("."), help="Starting directory"),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", "-r", help="Search recursively"
    ),
    priority: Optional[str] = typer.Option(None, "--priority", help="Filter by priority"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    tree: bool = typer.Option(False, "--tree", help="Tree-style output"),
    repo_path: Optional[Path] = typer.Option(None, "--repo-path", help="Repository root"),
    target: str = typer.Option("*", "--target", help="Target audience: ai, human, * (default: *)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Walk DOWN through directory tree (depth-first) for context files."""
    from .commands.acl import cmd_context_down_deep

    return asyncio.run(
        cmd_context_down_deep(
            buildargs(directory=directory)
            .add_common_args(quiet, verbose, output_format, allowed_roots=_allowed_roots)
            .add_filtering_args(recursive=recursive)
            .add_context_args(priority, None, tree, repo_path, target)
            .build()
        )
    )


@context_app.command("wide")
@handle_cli_errors
def context_wide(
    directory: Path = typer.Argument(Path("."), help="Starting directory"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Filter by priority"),
    for_use: Optional[str] = typer.Option(None, "--for", help="Filter by usage scope"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    tree: bool = typer.Option(False, "--tree", help="Tree-style output"),
    repo_path: Optional[Path] = typer.Option(None, "--repo-path", help="Repository root"),
    target: str = typer.Option("*", "--target", help="Target audience: ai, human, * (default: *)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Search directory tree (breadth-first) for context files."""
    from .commands.acl import cmd_context_down_wide

    return asyncio.run(
        cmd_context_down_wide(
            buildargs(directory=directory)
            .add_common_args(quiet, verbose, output_format)
            .add_context_args(priority, for_use, tree, repo_path, target)
            .build()
        )
    )


@context_app.command("path")
@handle_cli_errors
def context_path(
    path: Path = typer.Argument(..., help="File or directory to scan (no subdirs)"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Filter by priority"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    tree: bool = typer.Option(False, "--tree", help="Tree-style output"),
    repo_path: Optional[Path] = typer.Option(None, "--repo-path", help="Repository root"),
    target: str = typer.Option("*", "--target", help="Target audience: ai, human, * (default: *)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Scan a single file or directory (no subdirs) for context."""
    from .commands.acl import cmd_context_path

    return asyncio.run(
        cmd_context_path(
            buildargs(path=path)
            .add_common_args(quiet, verbose, output_format)
            .add_context_args(priority, None, tree, repo_path, target)
            .build()
        )
    )


@context_app.command("list-components")
@handle_cli_errors
def context_list_components(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed component information"
    ),
):
    """List all available analysis components with descriptions."""
    from .commands.context_scanner import cmd_list_components

    return cmd_list_components(verbose=verbose)


@context_app.command("list-presets")
@handle_cli_errors
def context_list_presets():
    """List all available component presets."""
    from .commands.context_scanner import cmd_list_presets

    return cmd_list_presets()


@context_app.command("analyze")
@handle_cli_errors
@with_filesystem_access()
def context_analyze(
    directory: Path = typer.Argument(..., help="Project directory to analyze"),
    filesystem_access=typer.Option(None, hidden=True),
    components: Optional[str] = typer.Option(
        None,
        "--components",
        "-c",
        help="Component specifications (e.g., 'summary,dependency_graph' or 'project_summary,ai_modules:limit=20,modules:sort_by=complexity;limit=10'). Use 'context list-components' to see available components.",
    ),
    analysis_mode: str = typer.Option("FULL", "--mode", help="Analysis mode (FULL, INCREMENTAL)"),
    max_depth: int = typer.Option(999, "--max-depth", help="Maximum directory traversal depth"),
    output_format: str = typer.Option(
        "console", "--format", help="Output format (console, html, json, markdown, text, yaml)"
    ),
    output_file: Optional[Path] = typer.Option(None, "--output", help="Output file path"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip cache and force fresh analysis"),
    cache_only: bool = typer.Option(
        False, "--cache-only", help="Only use cached data, fail if no cache available"
    ),
    show_progress: Optional[bool] = typer.Option(
        None,
        "--show-progress/--no-progress",
        help="Show progress during analysis (auto-detects based on format)",
    ),
):
    """Analyze project context using intelligent context scanner.

    Examples:
      # Use a preset
      codeguard context analyze ./project --components summary

      # Request specific components
      codeguard context analyze ./project --components project_summary,ai_modules:limit=10

      # Use complex parameters
      codeguard context analyze ./project --components modules:sort_by=complexity;limit=15

      # Combine presets and components
      codeguard context analyze ./project --components summary,dependency_graph

    Use 'context list-components' to see all available components.
    Use 'context list-presets' to see all available presets.
    """
    # Early help detection - show help even with invalid parameters
    if "--help" in sys.argv or "-h" in sys.argv:
        # Get the current command context to show proper help
        ctx = click.get_current_context()
        typer.echo(ctx.get_help())
        raise typer.Exit()

    # Log entry to context_analyze
    logger.info(f"🔧 CONTEXT_ANALYZE_START: Entered context_analyze with directory={directory}")

    from .commands.context_scanner import cmd_context_analyze
    from .p2p_integration import execute_with_p2p_routing

    # Create filesystem access using the same pattern as other CLI commands
    fs_args = argparse.Namespace()
    fs_args.allowed_roots = [str(directory.resolve())]
    filesystem_access = create_filesystem_access_from_args(fs_args)

    # Create THE ONLY progress formatter at command start - before any routing decisions
    if show_progress is None:
        show_progress = output_format.lower() in ["console", "table"]

    from .commands.context_scanner import ComponentArgumentParser

    # Parse components to get proper component specs
    component_parser = ComponentArgumentParser()
    if components:
        try:
            component_specs = component_parser.parse_components_argument(components)
        except Exception:
            component_specs = component_parser.parse_components_argument("summary")
    else:
        component_specs = component_parser.parse_components_argument("summary")

    # Calculate total expected work including scanner's built-in stages
    SCANNER_BUILTIN_STAGES = (
        4  # file_counting, structure_analysis, static_analysis, dependency_analysis
    )
    ROUTING_STAGE = 1  # P2P routing stage
    total_expected_work = SCANNER_BUILTIN_STAGES + len(component_specs) + ROUTING_STAGE

    # Use common function to set up progress
    progress_formatter = setup_command_progress(
        output_format=output_format,
        component_specs=component_specs,
        phase="Starting analysis",
        message="Initializing...",
        quiet=False,  # context analyze doesn't have a quiet option
        total_expected_work=total_expected_work,
    )
    progress_callback = progress_formatter.create_progress_callback()

    # Capture original command line for P2P execution
    original_command_line = " ".join(sys.argv[1:])  # Remove python executable

    return asyncio.run(
        execute_with_p2p_routing(
            filesystem_access=filesystem_access,
            progress_callback=progress_callback,
            command_name="context",
            command_args={
                "directory": directory,
                "components": components,
                "analysis_mode": analysis_mode,
                "max_depth": max_depth,
                "output_format": output_format,
                "output_file": output_file,
                "no_cache": no_cache,
                "cache_only": cache_only,
                "show_progress": show_progress,
            },
            subcommand="analyze",
            local_executor_func=cmd_context_analyze,
            original_command_line=original_command_line,
        )
    )


@context_app.command("query")
@handle_cli_errors
@with_filesystem_access()
def context_query(
    directory: Path = typer.Argument(..., help="Project directory to query"),
    filesystem_access=typer.Option(None, hidden=True),
    components: str = typer.Option(
        "summary", "--components", "-c", help="Component specifications to display"
    ),
    output_format: str = typer.Option(
        "console", "--format", help="Output format (console, html, json, markdown, text, yaml)"
    ),
    output_file: Optional[Path] = typer.Option(None, "--output", help="Output file path"),
):
    """Query cached project context without performing new analysis."""
    from .commands.context_scanner import cmd_context_query

    return asyncio.run(
        cmd_context_query(
            directory=directory,
            filesystem_access=filesystem_access,
            components=components,
            output_format=output_format,
            output_file=output_file,
        )
    )


@context_app.command("stats")
@handle_cli_errors
@with_filesystem_access()
def context_stats(
    directory: Path = typer.Argument(..., help="Project directory to check"),
    filesystem_access=typer.Option(None, hidden=True),
    output_format: str = typer.Option("table", "--format", help="Output format (table, json)"),
):
    """Show context cache and performance statistics."""
    from .commands.context_scanner import cmd_context_stats

    return cmd_context_stats(
        directory=directory,
        filesystem_access=filesystem_access,
        output_format=output_format,
    )


@context_app.command("invalidate")
@handle_cli_errors
@with_filesystem_access()
def context_invalidate(
    directory: Path = typer.Argument(..., help="Project directory to invalidate"),
    filesystem_access=typer.Option(None, hidden=True),
):
    """Invalidate cached context for the project."""
    from .commands.context_scanner import cmd_context_invalidate

    return cmd_context_invalidate(directory=directory, filesystem_access=filesystem_access)


app.add_typer(context_app, name="context")


# === GUARDS COMMANDS ===
guards_app = typer.Typer(name="guards", help="Directory guard management")


@guards_app.command("create")
@handle_cli_errors
def create_guards(
    directory: Path = typer.Argument(Path("."), help="Directory for .ai-attributes"),
    rules: List[str] = typer.Option([], "--rule", help="Add rule: 'pattern:guard'"),
    descriptions: List[str] = typer.Option(
        [], "--description", help="Add description: 'pattern:desc'"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Create .ai-attributes file with guard rules."""
    from .commands.directory_guards import cmd_create_aiattributes

    return cmd_create_aiattributes(
        buildargs(directory=directory, rule=rules, description=descriptions)
        .add_common_args(quiet, verbose, allowed_roots=_allowed_roots)
        .build()
    )


@guards_app.command("list")
@handle_cli_errors
def list_guards(
    directory: Path = typer.Argument(Path("."), help="Starting directory"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="List recursively"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """List guard rules from .ai-attributes files."""
    from .commands.directory_guards import cmd_list_aiattributes

    return cmd_list_aiattributes(
        buildargs(directory=str(directory))
        .add_common_args(quiet, verbose, output_format)
        .add_filtering_args(recursive=recursive)
        .build()
    )


@guards_app.command("validate")
@handle_cli_errors
def validate_guards(
    directory: Path = typer.Argument(Path("."), help="Starting directory"),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", "-r", help="Validate recursively"
    ),
    fix: bool = typer.Option(False, "--fix", help="Fix invalid files"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Validate .ai-attributes files."""
    from .commands.directory_guards import cmd_validate_aiattributes

    return cmd_validate_aiattributes(
        buildargs(directory=str(directory), fix=fix)
        .add_common_args(quiet, verbose)
        .add_filtering_args(recursive=recursive)
        .build()
    )


@guards_app.command("directories")
@handle_cli_errors
def list_guarded_directories(
    directory: Path = typer.Argument(Path("."), help="Starting directory"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """List directories with guard annotations."""
    from .commands.directory_guards import cmd_list_guarded_directories

    return cmd_list_guarded_directories(
        buildargs(directory=str(directory))
        .add_common_args(quiet, verbose, output_format, allowed_roots=_allowed_roots)
        .build()
    )


app.add_typer(guards_app, name="guards")


# === SETUP COMMANDS ===
app.add_typer(setup_app, name="setup")


# === SSL COMMANDS ===
app.add_typer(ssl_app, name="ssl")


# === PROMPT INJECTION COMMANDS ===
app.add_typer(prompt_app, name="prompt")


# === SMART NOTES COMMANDS ===
app.add_typer(smart_app, name="smart")


# === SYSTEM COMMANDS ===
app.add_typer(sys_app, name="sys")


# === P2P COMMANDS ===
app.add_typer(p2p_app, name="p2p")


# === TUI COMMAND ===
@app.command()
@handle_cli_errors
def tui():
    """Launch interactive Terminal User Interface for CodeGuard operations."""
    from .commands.tui_command import main as tui_main

    return tui_main()


# === SERVE COMMANDS ===
# serve_app is defined later in the file, will be added after definition


def format_comprehensive_help(help_data: Dict[str, Any], command: Optional[str] = None) -> None:
    """Format comprehensive help output with all parameters."""
    console.print(f"[bold blue]CodeGuard v{help_data['version']}[/bold blue]")
    console.print(help_data["description"])
    console.print()

    console.print("[bold green]📋 Commands:[/bold green]")
    for cmd_name, cmd_info in help_data["commands"].items():
        if command and cmd_name != command:
            continue
        console.print(f"  [cyan]{cmd_name}[/cyan] - {cmd_info.get('help', 'No description')}")

        # Show parameters for main commands
        if "parameters" in cmd_info and cmd_info["parameters"]:
            for param_name, param_info in cmd_info["parameters"].items():
                flags = " ".join(param_info.get("flags", [param_name]))
                help_text = param_info.get("help", "No description")
                required = " (required)" if param_info.get("required", False) else ""
                console.print(f"    {flags}: {help_text}{required}")

        # Show subcommands with their parameters
        if "subcommands" in cmd_info:
            for sub_name, sub_info in cmd_info["subcommands"].items():
                console.print(
                    f"    [dim cyan]{cmd_name} {sub_name}[/dim cyan] - {sub_info.get('help', 'No description')}"
                )

                # Show parameters for subcommands
                if "parameters" in sub_info and sub_info["parameters"]:
                    for param_name, param_info in sub_info["parameters"].items():
                        flags = " ".join(param_info.get("flags", [param_name]))
                        help_text = param_info.get("help", "No description")
                        required = " (required)" if param_info.get("required", False) else ""
                        console.print(f"      {flags}: {help_text}{required}")

        console.print()  # Add spacing between commands


@app.command()
def help(
    full: bool = typer.Option(
        False, "--full", help="Show comprehensive documentation with all parameters"
    ),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json, yaml"),
    command: Optional[str] = typer.Option(None, "--command", help="Show help for specific command"),
):
    """Show help information. Use --full for comprehensive documentation."""
    # Ensure scripts are registered for complete help
    ensure_scripts_registered()

    if full:
        # Show comprehensive help like docs command
        help_data = extract_full_help()

        if format.lower() == "json":
            console.print(json.dumps(help_data, indent=2))
        elif format.lower() == "yaml":
            console.print(yaml.dump(help_data, default_flow_style=False, sort_keys=False))
        else:
            format_comprehensive_help(help_data, command)
    else:
        # Show standard Typer help - same as --help
        import sys

        sys.argv = [sys.argv[0], "--help"]
        app()


@app.command()
def docs(
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json, yaml"),
    command: Optional[str] = typer.Option(None, "--command", help="Show docs for specific command"),
):
    """Show complete CLI documentation extracted from actual command definitions.\n\n💡 Use --format json for machine-readable output perfect for LLMs."""
    # Ensure scripts are registered for complete documentation
    ensure_scripts_registered()

    help_data = extract_full_help()

    if format.lower() == "json":
        console.print(json.dumps(help_data, indent=2))
    elif format.lower() == "yaml":
        console.print(yaml.dump(help_data, default_flow_style=False, sort_keys=False))
    else:
        format_comprehensive_help(help_data, command)


# === INTEGRATION COMMANDS ===

# Create serve subcommand group
serve_app = typer.Typer(name="serve", help="Start CodeGuard network services")


@serve_app.command("mcp")
def serve_mcp(
    host: str = typer.Option("127.0.0.1", "--host", help="Host for MCP server"),
    port: int = typer.Option(8000, "--port", help="MCP server port"),
    transport: str = typer.Option("network", "--transport", help="MCP transport protocol"),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path"),
):
    """Start MCP (Model Context Protocol) server."""
    return _start_services(["mcp"], host, port, 9000, "INFO", True, config)


@serve_app.command("proxy")
def serve_proxy(
    host: str = typer.Option("127.0.0.1", "--host", help="Host for proxy server"),
    port: int = typer.Option(9000, "--port", help="Proxy server port"),
    log_level: str = typer.Option("INFO", "--log-level", help="Proxy log level"),
    enable_hooks: bool = typer.Option(
        True, "--enable-hooks/--disable-hooks", help="Enable proxy hooks"
    ),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path"),
):
    """Start LLM proxy server."""
    return _start_services(["proxy"], host, 8000, port, log_level, enable_hooks, config)


@serve_app.command("llm")
def serve_llm(
    host: str = typer.Option("127.0.0.1", "--host", help="Host for LLM servers"),
    mcp_port: int = typer.Option(8000, "--mcp-port", help="MCP server port"),
    proxy_port: int = typer.Option(9000, "--proxy-port", help="Proxy server port"),
    mcp_transport: str = typer.Option("network", "--mcp-transport", help="MCP transport protocol"),
    proxy_log_level: str = typer.Option("INFO", "--proxy-log-level", help="Proxy log level"),
    enable_hooks: bool = typer.Option(
        True, "--enable-hooks/--disable-hooks", help="Enable proxy hooks"
    ),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path"),
):
    """Start LLM-related services (MCP and proxy servers)."""
    return _start_services(
        ["mcp", "proxy"], host, mcp_port, proxy_port, proxy_log_level, enable_hooks, config
    )


@serve_app.command("all")
def serve_all(
    host: str = typer.Option("127.0.0.1", "--host", help="Host for all servers"),
    mcp_port: int = typer.Option(8000, "--mcp-port", help="MCP server port"),
    proxy_port: int = typer.Option(9000, "--proxy-port", help="Proxy server port"),
    mcp_transport: str = typer.Option("network", "--mcp-transport", help="MCP transport protocol"),
    proxy_log_level: str = typer.Option("INFO", "--proxy-log-level", help="Proxy log level"),
    enable_hooks: bool = typer.Option(
        True, "--enable-hooks/--disable-hooks", help="Enable proxy hooks"
    ),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path"),
):
    """Start all CodeGuard network services."""
    return _start_services(
        ["mcp", "proxy"], host, mcp_port, proxy_port, proxy_log_level, enable_hooks, config
    )


@serve_app.command("p2p")
def serve_p2p(
    paths: Optional[List[Path]] = typer.Argument(
        None, help="Paths to manage (defaults to current directory)"
    ),
    host: str = typer.Option("127.0.0.1", "--host", help="Host for P2P server"),
    p2p_port: Optional[int] = typer.Option(None, "--p2p-port", help="P2P server port"),
    force: bool = typer.Option(False, "--force", help="Force P2P registration despite conflicts"),
    p2p_config: Optional[Path] = typer.Option(None, "--p2p-config", help="P2P config file path"),
    max_depth: int = typer.Option(
        999, "--max-depth", help="Maximum directory traversal depth for boundary discovery"
    ),
):
    """Start P2P path management service only."""
    # Default to current directory if no paths specified
    if not paths:
        paths = [Path.cwd()]

    # Import the normalization function
    from ..servers.p2p_server.network_manager.discovery_manager import normalize_path_for_storage

    path_strs = [normalize_path_for_storage(str(p)) for p in paths]

    cprint(f"🚀 Starting P2P service for paths: {path_strs}", mode=CONSOLE.VERBOSE)

    # Set discovery configuration
    path_objects: List[Union[str, Path]] = [Path(p) for p in path_strs]
    set_discovery_config_from_cli(max_depth=max_depth, paths=path_objects)

    # Start only P2P service
    return _start_services(
        ["p2p"],
        host,
        None,  # mcp_port (unused)
        None,  # proxy_port (unused)
        None,  # proxy_log_level (unused)
        None,  # enable_hooks (unused)
        None,  # config (unused)
        p2p_port=p2p_port,
        p2p_config=p2p_config,
        p2p_paths=path_strs,
        p2p_force=force,
    )


@serve_app.command("ide")
def serve_ide(
    min_version: Optional[str] = typer.Option(
        None, "--min-version", help="Minimum version requirement"
    )
):
    """Start IDE attachment mode."""
    try:
        start_worker_mode(min_version)
        return SUCCESS
    except Exception as e:
        console.print(f"[red]Error: IDE mode failed:[/red] {str(e)}")
        return UNEXPECTED_ERROR


@serve_app.command("manage")
def serve_manage(
    paths: Optional[List[Path]] = typer.Argument(
        None, help="Paths to manage (defaults to current directory)"
    ),
    host: str = typer.Option("127.0.0.1", "--host", help="Host for all servers"),
    mcp_port: int = typer.Option(8000, "--mcp-port", help="MCP server port"),
    proxy_port: int = typer.Option(9000, "--proxy-port", help="Proxy server port"),
    p2p_port: Optional[int] = typer.Option(None, "--p2p-port", help="P2P server port"),
    proxy_log_level: str = typer.Option("INFO", "--proxy-log-level", help="Proxy log level"),
    enable_hooks: bool = typer.Option(
        True, "--enable-hooks/--disable-hooks", help="Enable proxy hooks"
    ),
    force: bool = typer.Option(False, "--force", help="Force P2P registration despite conflicts"),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path"),
    p2p_config: Optional[Path] = typer.Option(None, "--p2p-config", help="P2P config file path"),
):
    """Start full CodeGuard management stack: MCP server, LLM proxy, and P2P path management."""
    # Default to current directory if no paths specified
    if not paths:
        paths = [Path.cwd()]

    # Import the normalization function
    from ..servers.p2p_server.network_manager.discovery_manager import normalize_path_for_storage

    path_strs = [normalize_path_for_storage(str(p)) for p in paths]

    console.print(f"🚀 Starting CodeGuard management stack for: {path_strs}")

    # Start all three services: MCP, proxy, and P2P
    return _start_services(
        ["mcp", "proxy", "p2p"],
        host,
        mcp_port,
        proxy_port,
        proxy_log_level,
        enable_hooks,
        config,
        p2p_port=p2p_port,
        p2p_config=p2p_config,
        p2p_paths=path_strs,
        p2p_force=force,
    )


def _start_services(
    services: List[str],
    host: str,
    mcp_port: Optional[int],
    proxy_port: Optional[int],
    proxy_log_level: Optional[str],
    enable_hooks: Optional[bool],
    config: Optional[Path],
    p2p_port: Optional[int] = None,
    p2p_config: Optional[Path] = None,
    p2p_paths: Optional[List[str]] = None,
    p2p_force: bool = False,
):
    """Internal function to start services with given parameters."""
    try:
        # Remove duplicates while preserving order
        services = list(dict.fromkeys(services))

        console.print(f"🚀 Starting CodeGuard services on {host}: {', '.join(services)}")

        # Create shared shutdown coordination BEFORE starting any services
        from ..utils.signal_handlers import create_shutdown_manager

        # Validate required parameters for each service
        if "mcp" in services and mcp_port is None:
            raise ValueError("MCP service requested but mcp_port is None")
        if "proxy" in services and proxy_port is None:
            raise ValueError("Proxy service requested but proxy_port is None")
        if "proxy" in services and proxy_log_level is None:
            raise ValueError("Proxy service requested but proxy_log_level is None")
        if "proxy" in services and enable_hooks is None:
            raise ValueError("Proxy service requested but enable_hooks is None")

        # Collect all ports that will be used
        service_ports = []
        if "mcp" in services and mcp_port:
            service_ports.extend([mcp_port, mcp_port + 1])  # SSE and HTTP ports
        if "proxy" in services and proxy_port:
            service_ports.append(proxy_port)
        if "p2p" in services and p2p_port:
            service_ports.append(p2p_port)

        shutdown_event, signal_manager = create_shutdown_manager(
            shutdown_event=None, service_name="CLI services", service_ports=service_ports
        )

        async def run_all_services():

            async def run_mcp():
                try:
                    from ..servers.mcp_server.runtime.server import run_server
                    from ..servers.mcp_server.server import mcp

                    console.print(f"🚀 MCP server starting on {host}:{mcp_port}")
                    await run_server(
                        mcp_instance=mcp,
                        transport="network",
                        host=host,
                        port=mcp_port,
                        shutdown_event=shutdown_event,
                    )
                except Exception as e:
                    console.print(f"[red]MCP server error:[/red] {str(e)}")

            async def run_proxy():
                try:
                    from ..servers.llm_proxy.__main__ import run_proxy_with_shutdown

                    console.print(f"🚀 Proxy server starting on {host}:{proxy_port}")
                    await run_proxy_with_shutdown(
                        config_path=str(config) if config else None,
                        host=host,
                        port=proxy_port,  # type: ignore  # Already validated above
                        shutdown_event=shutdown_event,
                    )
                except Exception as e:
                    console.print(f"[red]Proxy server error:[/red] {str(e)}")

            async def run_p2p():
                try:
                    cprint("🔧 P2P server initialization starting...")
                    from ..servers.p2p_server import HierarchicalNetworkManager
                    from ..servers.p2p_server.config import get_p2p_service
                    from ..servers.p2p_server.models import NodeMode

                    cprint("🔧 Loading P2P configuration...")
                    # Load P2P configuration using the new service
                    p2p_service = get_p2p_service()
                    if p2p_config:
                        # If a specific config file is provided, we need to load it differently
                        # For now, we'll load the default config and log the custom path
                        cprint(
                            f"⚠️  Custom config file specified but not yet supported: {p2p_config}"
                        )
                        cprint("📄 Using hierarchical config loading instead...")
                    p2p_config_obj = p2p_service.load_config()

                    cprint("🔧 Applying CLI overrides...")
                    # Override settings from CLI
                    if p2p_force:
                        p2p_config_obj.force_registration = p2p_force
                    if p2p_port:
                        p2p_config_obj.port_range_start = p2p_port
                        p2p_config_obj.port_range_end = p2p_port
                    if host != "127.0.0.1":
                        p2p_config_obj.bind_host = host

                    paths_to_manage = p2p_paths or [str(Path.cwd().absolute())]

                    cprint("🔧 Creating filesystem access for boundary discovery...")
                    # Create filesystem access using the same pattern as other CLI commands
                    fs_args = argparse.Namespace()
                    fs_args.allowed_roots = paths_to_manage
                    filesystem_access = create_filesystem_access_from_args(fs_args)

                    cprint("🔧 Creating network manager...")
                    # Create and start network manager with dedicated server priority (100)
                    node = HierarchicalNetworkManager(
                        p2p_config_obj,
                        paths_to_manage,
                        shutdown_event=shutdown_event,
                        discovery_priority=100,
                        filesystem_access=filesystem_access,
                        node_mode=NodeMode.SERVER,  # This is a server node
                    )

                    # Start P2P services first to initialize sockets
                    cprint(
                        f"🚀 P2P server starting for paths: {paths_to_manage}", mode=CONSOLE.VERBOSE
                    )
                    await node.start_services()
                    if not node.node_id:
                        raise RuntimeError("Failed to initialize P2P node - no node ID assigned")

                    cprint(f"📡 P2P node: {node.node_id}", mode=CONSOLE.VERBOSE)

                    # Now log the actual listening port
                    cprint(
                        f"🔗 P2P listening on: {node.get_local_ip()}:{node.port}",
                        mode=CONSOLE.VERBOSE,
                    )

                    # Display initial hierarchy tree after startup
                    try:
                        hierarchy_data = await node.discovery_manager.get_cached_hierarchy()
                        if hierarchy_data and hierarchy_data.get("tree"):
                            formatted_output = format_hierarchy_display_for_server(hierarchy_data)
                            cprint(formatted_output)
                    except Exception as e:
                        # Don't fail startup if hierarchy display fails
                        logger.debug(f"Error displaying initial hierarchy: {e}")

                    # Keep running until shutdown
                    try:
                        await shutdown_event.wait()
                    except asyncio.CancelledError:
                        cprint("🔧 P2P server shutdown requested")
                    finally:
                        cprint("🔧 Shutting down P2P services...")
                        await node.shutdown()
                        cprint("✅ P2P server shutdown complete")

                except Exception as e:
                    cprint(f"[red]❌ P2P server error:[/red] {str(e)}")
                    cprint("[red]📋 Full traceback:[/red]")
                    cprint(traceback.format_exc())
                    raise  # Re-raise to ensure the error propagates

            # Create task list - each service runs independently
            tasks = []

            if "mcp" in services:
                tasks.append(asyncio.create_task(run_mcp()))

            if "proxy" in services:
                tasks.append(asyncio.create_task(run_proxy()))

            if "p2p" in services:
                tasks.append(asyncio.create_task(run_p2p()))

            if not tasks:
                console.print("[red]No valid services specified[/red]")
                return

            cprint(
                f"✅ Starting {len(tasks)} service(s). Press Ctrl+C to stop all.",
                mode=CONSOLE.VERBOSE,
            )

            # Give services a moment to start, then re-register signal handlers to override FastMCP's
            await asyncio.sleep(0.5)  # Let FastMCP/Uvicorn register their handlers first
            try:
                # Check if signal_manager is actually a SignalManager (not nullcontext)
                if isinstance(signal_manager, SignalManager):
                    signal_manager.register_handlers()  # Now override them with ours
                    cprint("🛑 Signal handlers registered - Ctrl+C will now work properly")
            except Exception as e:
                cprint(f"⚠️  Could not register signal handlers: {e}")

            # Run all services concurrently
            try:
                await asyncio.gather(*tasks)
            except KeyboardInterrupt:
                cprint("\n[yellow]KeyboardInterrupt received, shutting down...[/yellow]")
                shutdown_event.set()
            except Exception as e:
                cprint(f"[red]Service error:[/red] {e}")

        # Run all services in a single event loop with signal manager context
        with signal_manager:
            asyncio.run(run_all_services())

        return SUCCESS

    except Exception as e:
        logger.error(f"Error starting services: {str(e)}", exc_info=True)
        return UNEXPECTED_ERROR


# Register serve_app with main app
app.add_typer(serve_app, name="serve")


# Commands moved to setup subcommand group


# === VERSION AND INFO ===


def version_callback(value: bool):
    if value:
        console.print(f"CodeGuard {__version__}")
        raise typer.Exit()


def lazy_script_loading_callback(ctx, param, value):
    """Callback that triggers script loading for help commands."""
    if value:  # If help flag is set
        ensure_scripts_registered()
    return value


def extract_full_help() -> Dict[str, Any]:
    """
    Extract complete CLI documentation from Typer's actual command definitions.
    """
    help_data = {
        "name": "codeguard",
        "version": __version__,
        "description": "Code Change Detection and Guard Validation Tool",
        "commands": {},
    }

    # Get Typer's Click context to access the actual command structure
    click_app = typer.main.get_command(app)

    # Extract main commands from Typer's Click app
    for cmd_name, cmd in getattr(click_app, "commands", {}).items():
        raw_help = cmd.help or cmd.short_help or "No description"
        # Filter out lines that don't start with alphanumeric (removes emoji tips)
        help_lines = raw_help.split("\n")
        clean_lines = [line for line in help_lines if line.strip() and line.strip()[0].isalnum()]
        cmd_help = "\n".join(clean_lines) if clean_lines else "No description"

        # Extract parameters from the Click command
        parameters = {}
        for param in cmd.params:
            if hasattr(param, "name") and param.name:
                param_info = {
                    "help": getattr(param, "help", "") or "No description",
                    "type": param.__class__.__name__,
                    "required": getattr(param, "required", False),
                }

                # Add parameter flags/options
                if hasattr(param, "opts"):
                    param_info["flags"] = list(param.opts)
                elif hasattr(param, "name"):
                    param_info["flags"] = [f"--{param.name}"]

                parameters[param.name] = param_info

        # Check if this is a group (has subcommands)
        if hasattr(cmd, "commands") and cmd.commands:
            subcommands = {}
            for sub_name, sub_cmd in cmd.commands.items():
                raw_sub_help = sub_cmd.help or sub_cmd.short_help or "No description"
                # Filter out lines that don't start with alphanumeric (removes emoji tips)
                sub_help_lines = raw_sub_help.split("\n")
                clean_sub_lines = [
                    line for line in sub_help_lines if line.strip() and line.strip()[0].isalnum()
                ]
                sub_help = "\n".join(clean_sub_lines) if clean_sub_lines else "No description"

                # Extract subcommand parameters
                sub_parameters = {}
                for param in sub_cmd.params:
                    if hasattr(param, "name") and param.name:
                        param_info = {
                            "help": getattr(param, "help", "") or "No description",
                            "type": param.__class__.__name__,
                            "required": getattr(param, "required", False),
                        }

                        if hasattr(param, "opts"):
                            param_info["flags"] = list(param.opts)
                        elif hasattr(param, "name"):
                            param_info["flags"] = [f"--{param.name}"]

                        sub_parameters[param.name] = param_info

                subcommands[sub_name] = {"help": sub_help, "parameters": sub_parameters}

            help_data["commands"][cmd_name] = {
                "help": cmd_help,
                "parameters": parameters,
                "subcommands": subcommands,
            }
        else:
            help_data["commands"][cmd_name] = {"help": cmd_help, "parameters": parameters}

    return help_data


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show version and exit"
    ),
    full: Optional[bool] = typer.Option(
        None,
        "--full",
        callback=lazy_script_loading_callback,
        help="Show complete CLI documentation",
    ),
    format: Optional[str] = typer.Option(
        None, "--format", help="Output format for --full: text, json, yaml"
    ),
    allowed_roots: Optional[str] = typer.Option(
        None,
        "--allowed-roots",
        help="Comma-separated list of allowed root directories for security",
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (errors only)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    CodeGuard - Code Change Detection and Guard Validation Tool

    A modern tool for tracking and validating code modifications with respect
    to designated "guarded" regions across multiple programming languages.

    💡 TIP: Use --full for complete documentation
    📖 Use --full --format json for machine-readable help
    """
    global _allowed_roots
    _allowed_roots = allowed_roots

    # Set global output level based on flags
    set_output_level_from_flags(quiet, verbose)

    if full:
        help_data = extract_full_help()
        output_format = format or "text"

        if output_format.lower() == "json":
            console.print(json.dumps(help_data, indent=2))
        elif output_format.lower() == "yaml":
            if yaml:
                console.print(yaml.dump(help_data, default_flow_style=False, sort_keys=False))
            else:
                console.print(
                    "[red]Error:[/red] PyYAML not available. Install with: pip install pyyaml"
                )
                console.print("Falling back to JSON:")
                console.print(json.dumps(help_data, indent=2))
        else:
            # Enhanced text format
            console.print(f"[bold blue]CodeGuard v{help_data['version']}[/bold blue]")
            console.print(help_data["description"])
            console.print()

            console.print("[bold green]📋 Commands:[/bold green]")
            for cmd, info in help_data["commands"].items():
                console.print(f"  [cyan]{cmd}[/cyan] - {info.get('help', 'No description')}")

                # Show parameters for main commands
                if "parameters" in info and info["parameters"]:
                    for param_name, param_info in info["parameters"].items():
                        flags = " ".join(param_info.get("flags", [param_name]))
                        help_text = param_info.get("help", "No description")
                        required = " (required)" if param_info.get("required", False) else ""
                        console.print(f"    {flags}: {help_text}{required}")

                # Show subcommands with their parameters
                if "subcommands" in info:
                    for sub, sub_info in info["subcommands"].items():
                        console.print(
                            f"    [dim cyan]{cmd} {sub}[/dim cyan] - {sub_info.get('help', 'No description')}"
                        )

                        # Show parameters for subcommands
                        if "parameters" in sub_info and sub_info["parameters"]:
                            for param_name, param_info in sub_info["parameters"].items():
                                flags = " ".join(param_info.get("flags", [param_name]))
                                help_text = param_info.get("help", "No description")
                                required = (
                                    " (required)" if param_info.get("required", False) else ""
                                )
                                console.print(f"      {flags}: {help_text}{required}")

                console.print()  # Add spacing between commands

        raise typer.Exit()


# === SCRIPT LOADING FROM MANIFEST ===
# Fast startup using pre-built manifest
_scripts_registered = False


def ensure_scripts_registered():
    """Ensure scripts are registered only once."""
    global _scripts_registered
    if not _scripts_registered:
        try:
            from .script_loader import register_manifest_commands

            register_manifest_commands(app)
            _scripts_registered = True
        except Exception as e:
            # Don't fail the entire CLI if script loading fails
            console.print(f"[yellow]Warning: Script loading failed: {e}[/yellow]")


# Register scripts immediately for fast access
ensure_scripts_registered()


if __name__ == "__main__":
    app()
