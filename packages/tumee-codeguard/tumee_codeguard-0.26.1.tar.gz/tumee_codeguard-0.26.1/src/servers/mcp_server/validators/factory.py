"""
Validator factory for MCP server.

This module provides secure validator creation with MCP roots constraints.
"""

import argparse
from typing import List, Optional

from ....core.factories import create_validator_from_args


def create_validator(
    mcp_roots: Optional[List[str]] = None,
    normalize_whitespace=True,
    normalize_line_endings=True,
    ignore_blank_lines=True,
    ignore_indentation=False,
    context_lines=3,
):
    """
    Create a validator with MCP roots security.

    Args:
        mcp_roots: List of allowed root directories
        normalize_whitespace: Normalize whitespace in comparisons
        normalize_line_endings: Normalize line endings in comparisons
        ignore_blank_lines: Ignore blank lines in comparisons
        ignore_indentation: Ignore indentation changes in comparisons
        context_lines: Number of context lines around violations

    Returns:
        CodeGuardValidator with secure filesystem access
    """
    # Create args namespace for validator creation
    args = argparse.Namespace(
        normalize_whitespace=normalize_whitespace,
        normalize_line_endings=normalize_line_endings,
        ignore_blank_lines=ignore_blank_lines,
        ignore_indentation=ignore_indentation,
        context_lines=context_lines,
        allowed_roots=mcp_roots,  # Keep as list - factory will handle type detection
    )

    return create_validator_from_args(args)
