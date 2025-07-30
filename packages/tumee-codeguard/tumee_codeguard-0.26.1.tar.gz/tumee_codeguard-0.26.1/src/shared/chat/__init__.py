"""
Chat command system with decorator-based registration.
"""

from .decorators import command
from .discovery import discover_commands, get_registered_commands

__all__ = ["command", "discover_commands", "get_registered_commands"]
