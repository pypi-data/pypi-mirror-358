"""
Root validation utilities for MCP server.

This module provides validation functionality with MCP roots security context.
It's separated from server.py to avoid circular import dependencies.
"""

from typing import List, Optional

from .validators import create_validator as create_validator_factory

# Global state for MCP roots
mcp_roots: Optional[List[str]] = None


def set_mcp_roots(roots: Optional[List[str]]) -> None:
    """Set the MCP roots for validation."""
    global mcp_roots
    mcp_roots = roots


def get_mcp_roots() -> Optional[List[str]]:
    """Get the current MCP roots."""
    return mcp_roots


def has_mcp_roots() -> bool:
    """Check if MCP roots are set and not empty."""
    return mcp_roots is not None and len(mcp_roots) > 0


def create_validator(
    normalize_whitespace=True,
    normalize_line_endings=True,
    ignore_blank_lines=True,
    ignore_indentation=False,
    context_lines=3,
):
    """Create a validator with MCP roots security."""
    return create_validator_factory(
        mcp_roots=mcp_roots,
        normalize_whitespace=normalize_whitespace,
        normalize_line_endings=normalize_line_endings,
        ignore_blank_lines=ignore_blank_lines,
        ignore_indentation=ignore_indentation,
        context_lines=context_lines,
    )
