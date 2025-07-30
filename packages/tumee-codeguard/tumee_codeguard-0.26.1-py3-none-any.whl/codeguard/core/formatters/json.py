"""
Universal JSON formatter for all CodeGuard data types.
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

from .base import DataType, FormatterRegistry, UniversalFormatter


@FormatterRegistry.register
class JsonFormatter(UniversalFormatter):
    """Universal JSON formatter supporting all data types."""

    @property
    def format_name(self) -> str:
        return "json"

    async def format_stream(
        self, items: AsyncGenerator[Any, None], data_type: DataType, **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Format items as streaming JSON using universal self-describing format.

        Args:
            items: AsyncGenerator yielding self-describing data objects
            data_type: Ignored - data describes itself
            **kwargs: Additional formatting options

        Yields:
            JSON string chunks for streaming output
        """
        async for item in items:
            # Self-describing data is already in the correct format - just serialize as JSON
            yield json.dumps(item, indent=2) + "\n"

    async def format_collection(self, items: List[Any], data_type: DataType, **kwargs) -> str:
        """
        Format a complete collection as JSON using universal self-describing format.

        Args:
            items: List of self-describing data objects
            data_type: Ignored - data describes itself
            **kwargs: Additional formatting options

        Returns:
            Complete JSON string
        """
        # Self-describing data is already in the correct format - just serialize as JSON
        if len(items) == 1:
            return json.dumps(items[0], indent=2)
        else:
            return json.dumps(items, indent=2)
