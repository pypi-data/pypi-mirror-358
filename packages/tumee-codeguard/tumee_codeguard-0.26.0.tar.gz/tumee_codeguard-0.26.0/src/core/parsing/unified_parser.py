"""
Unified Document Parser for CodeGuard CLI.

This module provides a single-pass parsing system that extracts all document information
in one operation: tree-sitter AST, guard tags, metrics, and line-by-line analysis.
"""

import asyncio
import logging
from typing import List, Optional

from ..infrastructure.processor import CoreConfiguration
from .processor_protocol import ParseProcessor
from .processors import GuardTagProcessor, MetricsProcessor
from .unified_types import LineContext, UnifiedParseResult

logger = logging.getLogger(__name__)


class UnifiedParser:
    """Unified document parser that processes everything in one pass."""

    def __init__(self):
        self.processors: List[ParseProcessor] = []

    def register_processor(self, processor: ParseProcessor) -> None:
        """Register a processor for line-by-line analysis."""
        self.processors.append(processor)

    async def parse_document(self, content: str, language_id: str) -> UnifiedParseResult:
        """
        Parse document in one unified pass.

        Args:
            content: Source code content
            language_id: Programming language identifier

        Returns:
            UnifiedParseResult with all extracted information
        """
        # Step 1: Parse tree-sitter AST once
        from .tree_sitter_parser import parse_document as ts_parse_document

        parse_result = ts_parse_document(content, language_id)
        lines = content.split("\n")

        # Step 2: Create unified result with core data
        unified_result = UnifiedParseResult(
            tree=parse_result.tree,
            root_node=parse_result.root_node,
            language_id=parse_result.language,
            success=parse_result.success,
            content=content,
            error_message=parse_result.error_message,
            line_count=len(lines),
            byte_count=len(content.encode("utf-8")),
        )

        if not parse_result.success:
            return unified_result

        # Step 3: Process each line with all registered processors
        for i, line_text in enumerate(lines):
            line_number = i + 1  # Convert to 1-based

            # Add periodic yield for responsiveness
            if i % 100 == 0:
                await asyncio.sleep(0)

            # Get node context for this line using the already-parsed tree
            node_context = None
            if parse_result.root_node:
                try:
                    from .tree_sitter_parser import find_node_at_position

                    # Convert line_number (1-based) to 0-based for tree-sitter
                    line_0_based = line_number - 1
                    node = find_node_at_position(parse_result.root_node, line_0_based, 0)
                    node_type = node.type if node else "unknown"
                    node_context = {"node_type": node_type}
                except Exception:
                    node_context = {"node_type": "unknown"}

            # Create line context
            unified_result.line_contexts[line_number] = LineContext(
                line_number=line_number,
                text=line_text,
                node_type=node_context.get("node_type", "unknown") if node_context else "unknown",
                language_id=language_id,
                is_empty=not line_text.strip(),
            )

            # Process line with all registered processors
            for processor in self.processors:
                try:
                    await processor.process_line(
                        line_number, line_text, node_context, unified_result
                    )
                except Exception as e:
                    logger.warning(
                        f"Processor {type(processor).__name__} failed on line {line_number}: {e}"
                    )

        # Step 4: Finalize with all processors
        for processor in self.processors:
            try:
                await processor.finalize(unified_result)
            except Exception as e:
                logger.warning(f"Processor {type(processor).__name__} finalization failed: {e}")

        return unified_result


# Global parser instance
_unified_parser = None


def get_unified_parser(config: Optional[CoreConfiguration] = None) -> UnifiedParser:
    """Get the global unified parser instance with default processors."""
    global _unified_parser
    if _unified_parser is None:
        _unified_parser = UnifiedParser()
        # Register default processors with shared configuration
        _unified_parser.register_processor(GuardTagProcessor(config))
        _unified_parser.register_processor(MetricsProcessor(config))
    return _unified_parser


def create_unified_parser() -> UnifiedParser:
    """Create a new unified parser instance (for testing/custom usage)."""
    return UnifiedParser()
