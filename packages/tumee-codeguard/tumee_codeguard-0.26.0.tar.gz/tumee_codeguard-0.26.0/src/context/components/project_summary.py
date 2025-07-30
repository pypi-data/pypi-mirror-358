"""
Project summary components.
"""

from typing import Any, Dict

from rich.console import Console
from rich.table import Table

from ...core.components.base import AnalysisComponent
from ...core.runtime import get_default_console
from ..models import AnalysisResults

console = get_default_console()


class ProjectSummaryComponent(AnalysisComponent):
    """Project overview component showing basic project statistics."""

    name = "project_summary"
    description = "Basic project statistics (files, modules, structure)"
    default_params = {}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract project summary data."""
        project_data = {
            "total_files": results.project_summary.total_files,
            "module_count": results.project_summary.module_count,
            "project_overview": results.project_summary.project_overview,
        }

        return {
            "data": project_data,
            "display": {
                "type": "table",
                "title": "📊 Project Overview",
                "columns": [
                    {"name": "Metric", "style": "cyan"},
                    {"name": "Value", "style": "green"},
                ],
                "rows": [
                    ["Total Files", str(project_data.get("total_files", 0))],
                    ["Total Modules", str(project_data.get("module_count", 0))],
                    ["Project Structure", project_data.get("project_overview", "N/A")],
                ],
            },
        }
