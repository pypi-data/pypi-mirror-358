"""
Metrics Processor for Unified Parser.

Extracts functions, classes, imports, and complexity metrics during unified parsing.
"""

import logging
from typing import Any, Dict, List, Optional

from ...infrastructure.processor import CoreConfiguration
from ..processor_protocol import ParseProcessor
from ..tree_sitter_parser import calculate_metrics
from ..unified_types import UnifiedParseResult

logger = logging.getLogger(__name__)


class MetricsProcessor:
    """Processor that extracts metrics during unified parsing."""

    def __init__(self, config: Optional[CoreConfiguration] = None):
        self.config = config or CoreConfiguration()
        self.functions = []
        self.classes = []
        self.imports = []
        self.exports = []

    async def process_line(
        self,
        line_num: int,
        line_text: str,
        node_context: Optional[Any],
        unified_result: UnifiedParseResult,
    ) -> None:
        """Process a single line for metrics extraction."""
        # Line-by-line metrics extraction is handled in finalize()
        # since tree-sitter metrics work better on the full AST
        pass

    async def finalize(self, unified_result: UnifiedParseResult) -> None:
        """Finalize metrics processing using the parsed AST."""
        if not unified_result.success or not unified_result.root_node:
            return

        try:
            # Use the already-parsed AST instead of re-parsing
            all_metrics = await calculate_metrics(
                unified_result.root_node, unified_result.content, unified_result.language_id
            )

            # Extract structured data
            unified_result.functions = all_metrics.get("functions", [])
            unified_result.classes = all_metrics.get("classes", [])
            unified_result.imports = all_metrics.get("imports", [])
            unified_result.exports = all_metrics.get("exports", [])

            # Extract tree-sitter metrics
            unified_result.total_nodes = all_metrics.get("total_nodes", 0)
            unified_result.named_nodes = all_metrics.get("named_nodes", 0)
            unified_result.max_depth = all_metrics.get("max_depth", 0)
            unified_result.function_count = all_metrics.get("function_count", 0)
            unified_result.class_count = all_metrics.get("class_count", 0)
            unified_result.complexity_score = all_metrics.get("complexity_score", 0.0)

        except Exception as e:
            logger.warning(f"Metrics extraction failed: {e}")
            # Fall back to basic extraction if enhanced metrics fail
            self._fallback_extraction(unified_result)

    def _fallback_extraction(self, unified_result: UnifiedParseResult) -> None:
        """Fallback extraction using regex if tree-sitter fails."""
        # Simple regex-based extraction as fallback
        import re

        content = unified_result.content
        language_id = unified_result.language_id

        # Basic function extraction
        if language_id == "python":
            func_pattern = r"^\s*def\s+(\w+)\s*\("
            class_pattern = r"^\s*class\s+(\w+)\s*[:\(]"
            import_pattern = r"^\s*(?:from\s+\S+\s+)?import\s+(.+)"
        elif language_id in ["javascript", "typescript"]:
            func_pattern = r"^\s*(?:function\s+(\w+)|(\w+)\s*:\s*function|(\w+)\s*=\s*function)"
            class_pattern = r"^\s*class\s+(\w+)"
            import_pattern = r"^\s*import\s+(.+)"
        else:
            # Generic patterns
            func_pattern = r"^\s*\w+\s+(\w+)\s*\("
            class_pattern = r"^\s*class\s+(\w+)"
            import_pattern = r"^\s*#include\s+[\"<](.+)[\">]"

        functions = []
        classes = []
        imports = []

        for line_num, line in enumerate(content.split("\n"), 1):
            # Function extraction
            func_match = re.search(func_pattern, line, re.IGNORECASE)
            if func_match:
                func_name = next(g for g in func_match.groups() if g)
                functions.append({"name": func_name, "line": line_num, "type": "function"})

            # Class extraction
            class_match = re.search(class_pattern, line, re.IGNORECASE)
            if class_match:
                classes.append({"name": class_match.group(1), "line": line_num, "type": "class"})

            # Import extraction
            import_match = re.search(import_pattern, line, re.IGNORECASE)
            if import_match:
                imports.append(
                    {"name": import_match.group(1).strip(), "line": line_num, "type": "import"}
                )

        unified_result.functions = functions
        unified_result.classes = classes
        unified_result.imports = imports
        unified_result.function_count = len(functions)
        unified_result.class_count = len(classes)
