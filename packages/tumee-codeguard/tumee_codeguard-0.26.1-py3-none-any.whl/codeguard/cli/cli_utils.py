"""
CLI utility functions for CodeGuard.
Shared helper functions used by CLI commands.
"""

import argparse
import json
import os
from pathlib import Path
from typing import List, Optional, Union

from ..core.factories import create_validator_from_args
from ..core.filesystem.path_utils import smart_truncate_path
from ..utils.reporter import Reporter


def create_reporter_from_args(args: argparse.Namespace) -> Reporter:
    """
    Create a Reporter instance from command-line arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Configured Reporter instance
    """
    # Determine output file
    output_file = args.output

    # For command-specific report paths
    if hasattr(args, "report") and args.report:
        output_file = args.report

    # Determine format
    report_format = args.format

    # For scan command's report format
    if hasattr(args, "report_format") and args.report_format:
        report_format = args.report_format

    return Reporter(
        format=report_format,
        output_file=output_file,
        console_style=args.console_style,
        include_content=not args.no_content,
        include_diff=not args.no_diff,
        max_content_lines=args.max_content_lines,
    )
