"""
Chat command decorator system.

Provides @command() decorator for marking functions as chat command handlers,
similar to @mcp.tool() but for chat prefix commands.
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict

from ...core.infrastructure.hook_registry import get_hook_registry

logger = logging.getLogger(__name__)

# Global registry of decorated command functions
_command_registry: Dict[str, Callable] = {}


def command(prefix: str):
    """
    Decorator to mark functions as chat command handlers.

    Usage:
        @command("prompt:")
        async def handle_prompt(message: str, payload: PayloadContext) -> HookResult:
            # Handle prompt: commands
            return result

    Args:
        prefix: Command prefix to register (e.g., "prompt:", "sys:")
    """

    def decorator(func: Callable) -> Callable:
        # Validate function signature
        if not callable(func):
            raise ValueError(f"@command decorator can only be applied to callable functions")

        # Store metadata on the function
        func._chat_command_prefix = prefix
        func._chat_command_registered = True

        # Register with global registry
        _register_command_function(prefix, func)

        logger.info(f"Chat command decorator: registered '{prefix}' -> {func.__name__}")

        # Return the original function unchanged
        return func

    return decorator


def _register_command_function(prefix: str, func: Callable) -> None:
    """Register a command function with the global registry."""
    if prefix in _command_registry:
        existing_func = _command_registry[prefix]
        logger.warning(
            f"Overriding existing command '{prefix}': {existing_func.__name__} -> {func.__name__}"
        )

    _command_registry[prefix] = func

    # Defer core hook registry registration until runtime
    # This avoids circular imports and allows method binding
    logger.debug(f"Registered command function '{prefix}' -> {func.__name__}")


def get_command_registry() -> Dict[str, Callable]:
    """Get the current command registry."""
    return _command_registry.copy()


def register_commands_with_core() -> None:
    """Register all decorated commands with the core hook registry."""
    try:
        hook_registry = get_hook_registry()

        registered_count = 0
        for prefix, func in _command_registry.items():
            hook_registry.register_hook(prefix, func)
            registered_count += 1
            logger.debug(f"Registered '{prefix}' with core hook registry")

        logger.info(f"Registered {registered_count} chat commands with core hook registry")

    except Exception as e:
        logger.error(f"Failed to register commands with core hook registry: {e}", exc_info=True)


def clear_command_registry() -> None:
    """Clear all registered commands (primarily for testing)."""
    global _command_registry
    _command_registry.clear()
    logger.debug("Cleared chat command registry")
