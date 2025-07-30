"""
Reporter for CodeGuard.

This module provides functionality for generating reports of validation results
in different formats.
"""

import asyncio
from enum import Enum
from typing import Any, AsyncGenerator, Optional, TextIO, Union

from ..core.formatters import FormatterRegistry
from ..core.formatters.base import DataType
from ..core.formatters.console import ConsoleStyle
from ..core.parsing.comparison_engine import GuardViolation
from ..core.validation.result import ValidationResult


class ReportFormat(Enum):
    """
    Supported output formats for validation reports.

    Values:
        JSON: Machine-readable JSON format
        YAML: Human-friendly YAML format
        TEXT: Plain text format for terminals
        HTML: HTML format with syntax highlighting
        MARKDOWN: Markdown format for documentation
        CONSOLE: Rich console output with colors and formatting
    """

    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    CONSOLE = "console"  # Rich console output


class Reporter:
    """
    Reporter for generating validation result reports.

    This class handles the generation of validation reports in various formats,
    suitable for different use cases (human reading, CI/CD integration,
    documentation, etc.). It supports both file and stream output.

    Attributes:
        format_name: The report format to generate
        output_file: Output destination (file path or file object)
        console_style: Console output style (for CONSOLE format)
        include_content: Whether to include code content in reports
        include_diff: Whether to include diff summaries when available
        max_content_lines: Maximum lines of content to show per violation
    """

    def __init__(
        self,
        format: Union[str, ReportFormat] = ReportFormat.TEXT,
        output_file: Optional[Union[str, TextIO]] = None,
        console_style: Union[str, ConsoleStyle] = ConsoleStyle.DETAILED,
        include_content: bool = True,
        include_diff: bool = True,
        max_content_lines: int = 10,
    ) -> None:
        """
        Initialize the reporter with specified options.

        Args:
            format: Report format to generate (default: TEXT).
                   Can be a ReportFormat enum value or string.
            output_file: Optional output destination. Can be:
                        - File path as string
                        - File-like object (must have write() method)
                        - None for stdout (default)
            console_style: Style for CONSOLE format output (default: DETAILED)
            include_content: Whether to include code content in reports
                           (default: True)
            include_diff: Whether to include diff summaries when available
                         (default: True)
            max_content_lines: Maximum lines of content to show per violation
                             (default: 10, 0 for unlimited)
        """
        if isinstance(format, str):
            format_lower = format.lower()
            # Check if format is valid by seeing if we have a formatter for it
            if FormatterRegistry.get_formatter(format_lower) is not None:
                self.format_name = format_lower
            else:
                self.format_name = "text"
        elif isinstance(format, ReportFormat):
            self.format_name = format.value
        else:
            self.format_name = "text"

        self.output_file = output_file

        if isinstance(console_style, str):
            style_lower = console_style.lower()
            # Validate console style against ConsoleStyle enum values
            valid_styles = [style.value for style in ConsoleStyle]
            if style_lower in valid_styles:
                self.console_style = style_lower
            else:
                self.console_style = "detailed"
        elif isinstance(console_style, ConsoleStyle):
            self.console_style = console_style.value
        else:
            self.console_style = "detailed"

        self.include_content = include_content
        self.include_diff = include_diff
        self.max_content_lines = max_content_lines

    async def generate_stream_report(
        self, items: AsyncGenerator[Any, None], output: Optional[TextIO] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming formatted report for validation results.

        This method generates a report in the configured format as items stream in,
        providing real-time output. The report includes a summary, violation details,
        and optionally code content and diffs.

        Args:
            items: AsyncGenerator yielding ValidationResult or violation objects
            output: Optional file-like object to write to. If None, uses the
                   output_file specified during initialization or stdout.

        Yields:
            Report chunks as strings for streaming output

        Raises:
            IOError: If unable to write to the output file
            ValueError: If the requested format is not available
        """
        # Get the formatter for the requested format
        formatter = FormatterRegistry.get_formatter(self.format_name)
        if formatter is None:
            # Fall back to text formatter
            formatter = FormatterRegistry.get_formatter("text")

        # Generate the report using the formatter's streaming method
        async for chunk in formatter.format_stream(
            items,
            DataType.VALIDATION_RESULTS,
            include_content=self.include_content,
            include_diff=self.include_diff,
            max_content_lines=self.max_content_lines,
            console_style=self.console_style,
        ):
            # Write to output if provided
            output_target = output or self.output_file
            if output_target:
                if isinstance(output_target, str):
                    # For file paths, we'll accumulate and write at the end
                    # This is not ideal for streaming but needed for file I/O
                    pass
                else:
                    output_target.write(chunk)

            yield chunk

    async def generate_report_to_file(
        self, items: AsyncGenerator[Any, None], file_path: str
    ) -> None:
        """
        Generate a complete report and write to file.

        Args:
            items: AsyncGenerator yielding ValidationResult or violation objects
            file_path: Path to write the complete report to
        """
        chunks = []
        async for chunk in self.generate_stream_report(items):
            chunks.append(chunk)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("".join(chunks))
