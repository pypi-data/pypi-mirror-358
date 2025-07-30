"""
CLI component integration for CodeGuard commands.

This module provides CLI-specific integration for the component system.
"""

from .display import ComponentDisplay
from .parser import ComponentArgumentParser

__all__ = ["ComponentArgumentParser", "ComponentDisplay"]
