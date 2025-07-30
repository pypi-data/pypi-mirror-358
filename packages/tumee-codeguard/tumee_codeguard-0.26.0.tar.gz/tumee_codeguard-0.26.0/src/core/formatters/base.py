"""
Unified base formatter interface for all CodeGuard data types.
"""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union


class DataType(Enum):
    """Supported data types for formatting."""

    VALIDATION_RESULTS = "validation_results"
    CONTEXT_FILES = "context_files"
    ACL_PERMISSIONS = "acl_permissions"
    DIRECTORY_GUARDS = "directory_guards"
    ANALYSIS_RESULTS = "analysis_results"
    P2P_STATUS = "p2p_status"
    P2P_NODE_LIST = "p2p_node_list"
    PROMPT_INJECT_RULES = "prompt_inject_rules"
    SMART_NOTES = "smart_notes"


class BaseFormatter(ABC):
    """Unified base class for all CodeGuard formatters."""

    def __init__(self):
        """Initialize base formatter with expected total tracking."""
        self._expected_total: Optional[float] = None

    @abstractmethod
    async def format_stream(
        self, items: AsyncGenerator[Any, None], data_type: DataType, **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Format items as they stream in.

        Args:
            items: AsyncGenerator yielding data objects (ValidationResult, context files, etc.)
            data_type: Type of data being formatted
            **kwargs: Additional formatting options

        Yields:
            Formatted string chunks for streaming output
        """
        yield  # type: ignore
        raise NotImplementedError

    @abstractmethod
    async def format_collection(
        self, items: Union[Any, List[Any]], data_type: DataType, **kwargs
    ) -> str:
        """
        Format a complete collection of items or a single item.

        Args:
            items: Single data object or list of data objects
            data_type: Type of data being formatted
            **kwargs: Additional formatting options

        Returns:
            Complete formatted string
        """
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the name of this format (e.g., 'json', 'html')."""
        pass

    @property
    @abstractmethod
    def supported_data_types(self) -> List[DataType]:
        """Return list of data types this formatter supports."""
        pass

    def supports_data_type(self, data_type: DataType) -> bool:
        """Check if this formatter supports the given data type."""
        return data_type in self.supported_data_types

    def supports_progress(self) -> bool:
        """
        Check if this formatter supports progress display.

        Returns:
            True if formatter can display progress, False otherwise
        """
        return False

    async def show_progress(self, **progress_data) -> None:
        """
        Display progress information during long-running operations.

        Args:
            **progress_data: Progress information including:
                - phase: Current operation phase (str)
                - current: Current item number (int)
                - total: Total items (int, optional)
                - message: Progress message (str, optional)
                - percentage: Progress percentage (float, optional)
        """
        pass

    def create_progress_callback(self) -> Callable:
        """Create a progress callback function for operations that need progress reporting."""

        async def progress_callback(**kwargs):
            await self.show_progress(**kwargs)
            await asyncio.sleep(0)  # Yield control to event loop

        return progress_callback

    async def finish_progress(self) -> None:
        """Finish and cleanup progress display."""
        pass


class ValidationFormatter(BaseFormatter):
    """Base class for formatters that only handle validation results (backward compatibility)."""

    @property
    def supported_data_types(self) -> List[DataType]:
        return [DataType.VALIDATION_RESULTS]

    @abstractmethod
    async def format_validation_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format validation results as they stream in (legacy method)."""
        yield  # type: ignore
        raise NotImplementedError

    @abstractmethod
    async def format_validation_collection(self, items: List[Any], **kwargs) -> str:
        """Format a complete collection of validation results (legacy method)."""
        pass

    async def format_stream(
        self, items: AsyncGenerator[Any, None], data_type: DataType, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Unified interface delegates to validation-specific method."""
        if data_type != DataType.VALIDATION_RESULTS:
            raise ValueError(
                f"ValidationFormatter only supports VALIDATION_RESULTS, got {data_type}"
            )
        async for chunk in self.format_validation_stream(items, **kwargs):
            yield chunk

    async def format_collection(self, items: List[Any], data_type: DataType, **kwargs) -> str:
        """Unified interface delegates to validation-specific method."""
        if data_type != DataType.VALIDATION_RESULTS:
            raise ValueError(
                f"ValidationFormatter only supports VALIDATION_RESULTS, got {data_type}"
            )
        return await self.format_validation_collection(items, **kwargs)


class UniversalFormatter(BaseFormatter):
    """Base class for formatters that handle multiple data types."""

    @property
    def supported_data_types(self) -> List[DataType]:
        return list(DataType)  # Support all data types by default


class FormatterRegistry:
    """Registry for managing available formatters."""

    _formatters = {}

    @classmethod
    def register(cls, formatter_class):
        """Register a formatter class."""
        instance = formatter_class()
        cls._formatters[instance.format_name] = instance
        return formatter_class

    @classmethod
    def get_formatter(cls, format_name: str) -> Optional[BaseFormatter]:
        """Get a formatter by name."""
        return cls._formatters.get(format_name)

    @classmethod
    def get_available_formats(cls) -> list:
        """Get list of available format names."""
        return list(cls._formatters.keys())


def format_context_file_content(
    cf: Dict[str, Any], verbosity: int = 0, max_lines: int = 999999
) -> List[str]:
    """
    Shared utility to format context file content for display.

    Args:
        cf: Context file dictionary
        verbosity: Verbosity level (-1=quiet, 0=normal, 1+=verbose)
        max_lines: Maximum lines to show per content region

    Returns:
        List of formatted lines ready for display
    """
    lines = []

    # No content in quiet mode
    if verbosity < 0:
        return lines

    if cf.get("type") == "ai_attributes" and "content" in cf:
        # Show .ai-attributes content
        lines.append("  Content:")
        for line in cf["content"].strip().split("\n"):
            lines.append(f"    {line}")
        lines.append("")
    elif cf.get("context_regions"):
        # Show context regions for files with guard tags
        lines.append("  Context Regions:")
        for region in cf["context_regions"]:
            lines.append(f"    Lines {region['start_line']}-{region['end_line']}:")
            # Show content with line limits
            content_lines = region["content"].strip().split("\n")
            for i, line in enumerate(content_lines[:max_lines]):
                lines.append(f"      {line}")
            if len(content_lines) > max_lines:
                lines.append(f"      ... ({len(content_lines) - max_lines} more lines)")
        lines.append("")
    elif "file_metadata" in cf:
        # Show basic file metadata for context files without regions
        metadata = cf["file_metadata"]
        lines.append(f"  Size: {metadata.get('size_bytes', 0)} bytes")
        lines.append(f"  Language: {cf.get('language_id', 'unknown')}")
        if cf.get("has_guard_tags"):
            lines.append("  Contains guard tags (but no context regions)")
        lines.append("")

    return lines
