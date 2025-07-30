"""
Context analysis components for the CodeGuard context scanner.

This module provides specialized components for context analysis output.
"""

from .loader import register_all_context_components

# Auto-register all context components when this module is imported
register_all_context_components()

__all__ = ["register_all_context_components"]
