#!/usr/bin/env python3
"""
Shared CLI utilities for both CLI and chat systems.
Provides common argument building and error handling functionality.
"""

import argparse
import asyncio
import logging
import sys
from functools import wraps
from pathlib import Path
from typing import Union

import typer
from rich.console import Console

from ..exit_codes import (
    INPUT_VALIDATION_FAILED,
    SUCCESS,
    UNEXPECTED_ERROR,
    get_exit_code_description,
)
from ..runtime import get_default_console

logger = logging.getLogger(__name__)
# Shared console instance
console = get_default_console()


def create_args_namespace(**kwargs):
    """Create argparse.Namespace with provided kwargs, converting Path objects to strings."""
    converted_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, Path):
            converted_kwargs[key] = str(value) if value else None
        else:
            converted_kwargs[key] = value
    return argparse.Namespace(**converted_kwargs)


def calculate_verbosity(quiet: bool = False, verbose: bool = False) -> int:
    """Calculate verbosity level: -1 (quiet), 0 (normal), 1 (verbose)."""
    if quiet:
        return -1
    elif verbose:
        return 1
    else:
        return 0


def is_python_src_invocation() -> bool:
    """
    Detect if CLI was invoked via 'python src/...' pattern (LLM/programmatic usage).

    Returns True for invocations like:
    - python src/cli/cli_typer.py
    - python /path/to/project/src/cli/cli_typer.py

    Returns:
        bool: True if invoked via python src pattern, False otherwise
    """
    return (
        "/src/" in sys.argv[0]
        or sys.argv[0].endswith(".py")
        and "src" in str(Path(sys.argv[0]).parent)
    )


def handle_exit_code_with_message(
    exit_code: int, quiet: bool = False, verbose: bool = False, context: Union[str, None] = None
) -> int:
    """Handle exit codes by displaying appropriate messages based on verbosity level."""
    if exit_code != SUCCESS:
        if quiet:
            console.print(str(exit_code))
        elif verbose:
            description = get_exit_code_description(exit_code)
            console.print(f"[red]Error ({exit_code}):[/red] {description}")
            if context:
                console.print(f"[dim]Context: {context}[/dim]")
        else:
            description = get_exit_code_description(exit_code)
            console.print(f"[red]Error ({exit_code}):[/red] {description}")
    return exit_code


def handle_cli_errors(func):
    """Decorator to handle common CLI errors consistently and provide user-friendly exit code messages."""

    def _handle_result(result, args, kwargs):
        """Common result handling for both sync and async functions."""
        # If result is an integer (exit code), handle it with appropriate verbosity
        if isinstance(result, int):
            if result != SUCCESS:
                # Extract quiet and verbose flags from function kwargs
                quiet = kwargs.get("quiet", False)
                verbose = kwargs.get("verbose", False)

                # Create context information for verbose mode
                func_name = func.__name__
                context_parts = []

                if func_name == "verify":
                    original = kwargs.get("original")
                    modified = kwargs.get("modified")
                    git_revision = kwargs.get("git_revision")

                    if git_revision:
                        context_parts.append(f"git revision {git_revision} of {original}")
                    elif modified is None:
                        context_parts.append(f"file {original} against disk")
                    else:
                        context_parts.append(f"{original} vs {modified}")
                elif func_name in ["tags", "show", "acl"]:
                    # Extract path/file arguments
                    path_arg = kwargs.get("path") or kwargs.get("file") or args[0] if args else None
                    if path_arg:
                        context_parts.append(f"target: {path_arg}")

                context = f"Operation: {func_name}" + (
                    f" - {', '.join(context_parts)}" if context_parts else ""
                )

                handle_exit_code_with_message(result, quiet, verbose, context)

            # For Typer, we need to explicitly exit with the code
            raise typer.Exit(code=result)

        return result

    # Handle both sync and async functions
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return _handle_result(result, args, kwargs)
            except typer.Exit:
                raise
            except Exception as e:
                console.print(f"[red]Error:[/red] {str(e)}")
                logger.exception("Unexpected error in CLI command", exc_info=e, stack_info=True)
                raise typer.Exit(code=UNEXPECTED_ERROR)

        return async_wrapper
    else:

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return _handle_result(result, args, kwargs)
            except typer.Exit:
                raise
            except Exception as e:
                console.print(f"[red]Error:[/red] {str(e)}")
                logger.exception("Unexpected error in CLI command", exc_info=e, stack_info=True)
                raise typer.Exit(code=UNEXPECTED_ERROR)

        return sync_wrapper


class ArgsBuilder:
    """Fluent interface for building command arguments."""

    def __init__(self, **initial_args):
        self.args_dict = initial_args.copy()

    def add_common_args(
        self, quiet=False, verbose=False, output_format="text", output=None, allowed_roots=None
    ):
        """Add commonly used arguments."""
        self.args_dict.update(
            {
                "verbose": calculate_verbosity(quiet, verbose),
                "format": output_format,
                "output": str(output) if output else None,
                "quiet": quiet,
                "allowed_roots": allowed_roots,
            }
        )
        return self

    def add_filtering_args(self, include=None, exclude=None, recursive=False):
        """Add filtering arguments."""
        self.args_dict.update(
            {"include": include, "exclude": exclude or [], "recursive": recursive}
        )
        return self

    def add_context_args(self, priority=None, for_use=None, tree=False, repo_path=None, target="*"):
        """Add context command arguments."""
        self.args_dict.update(
            {
                "priority": priority,
                "for_use": for_use,
                "tree": tree,
                "repo_path": str(repo_path) if repo_path else None,
                "target": target,
            }
        )
        return self

    def build(self):
        """Build the final argparse.Namespace."""
        return create_args_namespace(**self.args_dict)


def buildargs(**initial_args):
    """Convenience function to create ArgsBuilder."""
    return ArgsBuilder(**initial_args)
