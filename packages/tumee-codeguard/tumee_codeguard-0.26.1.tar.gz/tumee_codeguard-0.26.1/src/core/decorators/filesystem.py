"""
Filesystem setup decorator for CLI commands.

This module provides a decorator to simplify the common filesystem setup
pattern used across CLI commands.
"""

import asyncio
import functools
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar, Union, cast

from ..filesystem.access import FileSystemAccess
from ..interfaces import IFileSystemAccess
from ..security.roots import RootsSecurityManager

F = TypeVar("F", bound=Callable[..., Any])


def with_filesystem_access() -> Callable[[F], F]:
    """
    Decorator that sets up filesystem access for CLI commands.

    Handles the common pattern of:
    1. Resolving the directory parameter
    2. Creating RootsSecurityManager with the resolved directory
    3. Creating FileSystemAccess instance
    4. Injecting filesystem_access into the decorated function

    The decorated function MUST have a 'directory' parameter of type Path.

    Supports both sync and async functions automatically.

    Usage:
        @with_filesystem_access()
        def my_command(directory: Path, filesystem_access: IFileSystemAccess, **kwargs):
            # Use filesystem_access and resolved directory
            pass

        @with_filesystem_access()
        async def my_async_command(directory: Path, filesystem_access: IFileSystemAccess, **kwargs):
            # Use filesystem_access and resolved directory
            pass
    """

    def decorator(func: F) -> F:
        def _setup_filesystem(args, kwargs):
            """Common filesystem setup logic."""
            # Get the directory parameter
            directory = kwargs.get("directory")
            if directory is None:
                # Try to get from positional args based on function signature
                import inspect

                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                if "directory" in param_names:
                    param_index = param_names.index("directory")
                    if param_index < len(args):
                        directory = args[param_index]

            if directory is None:
                raise ValueError("Required parameter 'directory' not found")

            # Convert to Path if it's a string
            if isinstance(directory, str):
                directory = Path(directory)

            # Resolve the directory and create filesystem access
            resolved_dir = directory.resolve()
            security_manager = RootsSecurityManager([str(resolved_dir)])
            filesystem_access = FileSystemAccess(security_manager)

            # Inject filesystem_access and resolved directory
            kwargs["filesystem_access"] = filesystem_access
            kwargs["directory"] = resolved_dir

            return args, kwargs

        # Check if the function is async and return appropriate wrapper
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                args, kwargs = _setup_filesystem(args, kwargs)
                return await func(*args, **kwargs)

            return cast(F, async_wrapper)
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                args, kwargs = _setup_filesystem(args, kwargs)
                return func(*args, **kwargs)

            return cast(F, sync_wrapper)

    return decorator
