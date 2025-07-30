"""
Chat command discovery system.

Discovers and registers @command decorated functions from modules.
"""

import importlib
import logging
import pkgutil
from typing import Any, Callable, Dict, List, Optional

from .decorators import get_command_registry, register_commands_with_core

logger = logging.getLogger(__name__)


def discover_commands(package_paths: Optional[List[str]] = None) -> Dict[str, Callable]:
    """
    Discover chat commands from specified packages.

    Args:
        package_paths: List of package paths to scan. If None, uses default chat paths.

    Returns:
        Dictionary mapping command prefixes to handler functions
    """
    if package_paths is None:
        # Default paths where chat commands are likely to be
        package_paths = [
            "src.chat.prompt",
            "src.chat.sys",
            "src.chat.urgent",
        ]

    discovered_commands = {}

    for package_path in package_paths:
        try:
            commands = _discover_commands_in_package(package_path)
            discovered_commands.update(commands)
            logger.info(f"Discovered {len(commands)} commands in {package_path}")
        except Exception as e:
            logger.debug(f"Could not discover commands in {package_path}: {e}")

    # Also include any commands that were already registered
    registry_commands = get_command_registry()
    discovered_commands.update(registry_commands)

    return discovered_commands


def _discover_commands_in_package(package_path: str) -> Dict[str, Callable]:
    """Discover commands in a specific package."""
    commands = {}

    try:
        # Import the package to trigger decorator registration
        module = importlib.import_module(package_path)

        # Look for decorated functions in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and hasattr(attr, "_chat_command_prefix"):
                prefix = attr._chat_command_prefix
                commands[prefix] = attr
                logger.debug(f"Found decorated command: {prefix} -> {attr.__name__}")

        # Try to find submodules
        if hasattr(module, "__path__"):
            for _, name, _ in pkgutil.iter_modules(module.__path__):
                submodule_path = f"{package_path}.{name}"
                try:
                    subcommands = _discover_commands_in_package(submodule_path)
                    commands.update(subcommands)
                except Exception as e:
                    logger.debug(f"Could not scan submodule {submodule_path}: {e}")

    except ImportError as e:
        logger.debug(f"Could not import package {package_path}: {e}")

    return commands


def get_registered_commands() -> List[str]:
    """Get list of currently registered command prefixes."""
    return list(get_command_registry().keys())


def ensure_commands_discovered() -> None:
    """
    Ensure chat commands are discovered and registered.

    This function can be called at server startup to trigger command discovery.
    """
    try:
        commands = discover_commands()
        logger.info(f"Chat command discovery complete: {len(commands)} commands registered")

        # Log registered commands for debugging
        for prefix in sorted(commands.keys()):
            func = commands[prefix]
            logger.debug(f"  {prefix} -> {func.__module__}.{func.__name__}")

        # Register all commands with core hook registry
        register_commands_with_core()

    except Exception as e:
        logger.error(f"Error during command discovery: {e}", exc_info=True)
