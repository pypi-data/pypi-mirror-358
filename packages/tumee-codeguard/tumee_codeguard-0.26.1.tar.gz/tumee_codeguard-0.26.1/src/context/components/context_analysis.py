"""
Context-specific analysis components.
"""

from typing import Any, Dict, Union

from rich.console import Console
from rich.table import Table

from ...core.components.base import AnalysisComponent
from ...core.runtime import get_default_console
from ..models import AnalysisResults

console = get_default_console()


class ContextOverviewComponent(AnalysisComponent):
    """Context overview component for AI context analysis."""

    name = "context_overview"
    description = "Overview of AI context tags and regions in the codebase"
    default_params = {}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract context overview data."""
        total_context_files = 0
        total_context_lines = 0

        # Count context files and lines
        for module_context in results.module_contexts.values():
            if hasattr(module_context, "file_analyses"):
                for file_data in module_context.file_analyses.values():
                    if isinstance(file_data, dict) and file_data.get("context_line_count", 0) > 0:
                        total_context_files += 1
                        total_context_lines += file_data.get("context_line_count", 0)

        context_data = {
            "total_context_files": total_context_files,
            "total_context_lines": total_context_lines,
        }

        return {
            "data": context_data,
            "display": {
                "type": "table",
                "title": "📍 Context Overview",
                "columns": [
                    {"name": "Metric", "style": "cyan"},
                    {"name": "Value", "style": "green"},
                ],
                "rows": [
                    ["Total Context Files", str(context_data.get("total_context_files", 0))],
                    ["Total Context Lines", str(context_data.get("total_context_lines", 0))],
                ],
            },
        }
