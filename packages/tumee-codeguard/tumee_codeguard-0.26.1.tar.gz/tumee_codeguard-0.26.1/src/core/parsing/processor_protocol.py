"""
Protocol definition for parse processors.
"""

from typing import Any, Optional, Protocol

from .unified_types import UnifiedParseResult


class ParseProcessor(Protocol):
    """Protocol for document parse processors."""

    async def process_line(
        self,
        line_num: int,
        line_text: str,
        node_context: Optional[Any],
        unified_result: UnifiedParseResult,
    ) -> None:
        """Process a single line and update unified_result."""
        ...

    async def finalize(self, unified_result: UnifiedParseResult) -> None:
        """Finalize processing after all lines are processed."""
        ...
