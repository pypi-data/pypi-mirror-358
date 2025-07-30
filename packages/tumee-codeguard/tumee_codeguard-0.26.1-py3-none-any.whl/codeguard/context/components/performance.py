"""
Performance metrics components.
"""

from typing import Any, Dict, Union

from rich.console import Console
from rich.table import Table

from ...core.components.base import AnalysisComponent
from ...core.runtime import get_default_console
from ..models import AnalysisResults

console = get_default_console()


class PerformanceMetricsComponent(AnalysisComponent):
    """Performance metrics component showing analysis timing and cache efficiency."""

    name = "performance_metrics"
    description = "Analysis timing, cache efficiency, and performance stats"
    default_params = {}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract performance metrics data."""
        metadata = results.metadata
        perf_data = {
            "analysis_time_seconds": metadata.get("analysis_time_seconds", 0.0),
            "cache_efficiency": metadata.get("cache_efficiency", 0.0),
            "modules_analyzed_fresh": metadata.get("modules_analyzed_fresh", 0),
            "modules_from_cache": metadata.get("modules_from_cache", 0),
            "files_analyzed_fresh": metadata.get("files_analyzed_fresh", 0),
            "files_from_cache": metadata.get("files_from_cache", 0),
            "llm_calls_made": 0,  # TODO: Add LLM call tracking
        }

        return {
            "data": perf_data,
            "display": {
                "type": "table",
                "title": "⚡ Performance Metrics",
                "columns": [
                    {"name": "Metric", "style": "cyan"},
                    {"name": "Value", "style": "yellow"},
                ],
                "rows": [
                    ["Analysis Time", f"{perf_data.get('analysis_time_seconds', 0):.2f}s"],
                    ["Cache Efficiency", f"{perf_data.get('cache_efficiency', 0.0):.1f}%"],
                    ["Modules Fresh", str(perf_data.get("modules_analyzed_fresh", 0))],
                    ["Modules Cached", str(perf_data.get("modules_from_cache", 0))],
                    ["Files Analyzed", str(perf_data.get("files_analyzed_fresh", 0))],
                    ["Files Cached", str(perf_data.get("files_from_cache", 0))],
                    ["LLM Calls", str(perf_data.get("llm_calls_made", 0))],
                ],
            },
        }
