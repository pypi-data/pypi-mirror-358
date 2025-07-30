"""
Validator factory for creating CodeGuardValidator instances.

This module provides centralized validator creation logic to avoid circular imports
between CLI utilities and core modules.
"""

import argparse

from ..validation.validator import CodeGuardValidator
from .filesystem import create_filesystem_access_from_args


def create_validator_from_args(args: argparse.Namespace) -> CodeGuardValidator:
    """
    Create a CodeGuardValidator instance from command-line arguments with secure filesystem access.

    Args:
        args: Parsed command-line arguments

    Returns:
        Configured CodeGuardValidator instance with filesystem security
    """
    # Create filesystem access layer using shared factory
    filesystem_access = create_filesystem_access_from_args(args)

    return CodeGuardValidator(
        filesystem_access=filesystem_access,
        normalize_whitespace=getattr(args, "normalize_whitespace", True),
        normalize_line_endings=getattr(args, "normalize_line_endings", True),
        ignore_blank_lines=getattr(args, "ignore_blank_lines", True),
        ignore_indentation=getattr(args, "ignore_indentation", False),
        context_lines=getattr(args, "context_lines", 3),
    )
