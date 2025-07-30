"""
Module-related analysis components.
"""

from typing import Any, Dict, List, Union

from rich.console import Console
from rich.table import Table

from ...core.components.base import AnalysisComponent
from ...core.runtime import get_default_console
from ..models import AnalysisResults

console = get_default_console()


class ModulesComponent(AnalysisComponent):
    """Module summary component showing all modules with their metrics."""

    name = "modules"
    description = "Module listing with files, lines, complexity, and language info"
    default_params = {"sort_by": "importance", "limit": 10}

    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module component parameters."""
        validated = super().validate_params(params)

        # Validate sort_by parameter
        valid_sort_options = ["importance", "files", "complexity", "name", "lines"]
        sort_by = validated.get("sort_by", "importance")
        if sort_by not in valid_sort_options:
            raise ValueError(
                f"Invalid sort_by value: {sort_by}. Must be one of: {valid_sort_options}"
            )

        return validated

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract module data."""
        validated_params = self.validate_params(params)
        sort_by = validated_params["sort_by"]
        limit = validated_params["limit"]

        modules_data = []

        # Extract module information
        for module_path, module_context in results.module_contexts.items():
            if hasattr(module_context, "file_analyses"):
                # Calculate metrics from file analyses
                total_lines = 0
                complexities = []
                file_count = len(module_context.file_analyses)

                for file_data in module_context.file_analyses.values():
                    if isinstance(file_data, dict):
                        total_lines += file_data.get("line_count", 0)
                        complexity = file_data.get("complexity_score", 0.0)
                        if complexity > 0:
                            complexities.append(complexity)

                avg_complexity = sum(complexities) / len(complexities) if complexities else 0.0
                max_complexity = max(complexities) if complexities else 0.0
                importance_score = getattr(module_context, "complexity_score", avg_complexity)
                primary_language = getattr(module_context, "primary_language", "unknown")

                modules_data.append(
                    {
                        "module_path": module_path,
                        "file_count": file_count,
                        "total_lines": total_lines,
                        "avg_complexity": avg_complexity,
                        "max_complexity": max_complexity,
                        "importance_score": importance_score,
                        "primary_language": primary_language,
                    }
                )

        # Sort modules
        if sort_by == "files":
            modules_data.sort(key=lambda x: x["file_count"], reverse=True)
        elif sort_by == "complexity":
            modules_data.sort(key=lambda x: x["avg_complexity"], reverse=True)
        elif sort_by == "name":
            modules_data.sort(key=lambda x: x["module_path"])
        elif sort_by == "lines":
            modules_data.sort(key=lambda x: x["total_lines"], reverse=True)
        else:  # importance (default)
            modules_data.sort(key=lambda x: x["importance_score"], reverse=True)

        # Apply limit
        if limit is not None:
            limited_modules = modules_data[:limit]
            truncated_count = len(modules_data) - limit if len(modules_data) > limit else 0
        else:
            limited_modules = modules_data
            truncated_count = 0

        modules_data_final = limited_modules
        if truncated_count > 0:
            # Add truncation indicator
            modules_data_final = limited_modules + [
                {
                    "module_path": "...",
                    "file_count": f"({truncated_count} more)",
                    "total_lines": "...",
                    "avg_complexity": "...",
                    "max_complexity": "...",
                    "importance_score": "...",
                    "primary_language": "...",
                }
            ]

        return {
            "data": {
                "modules": modules_data_final,
                "sort_by": sort_by,
                "total_modules": len(modules_data),
                "truncated_count": truncated_count,
            },
            "display": {
                "type": "table",
                "title": f"📁 Module Summary (sorted by {sort_by.title()})",
                "columns": [
                    {"name": "Module", "style": "cyan", "width": 29},
                    {"name": "Files", "style": "green", "width": 7},
                    {"name": "Lines", "style": "magenta", "width": 7},
                    {"name": "Avg Complexity", "style": "red", "width": 8},
                    {"name": "Max Complexity", "style": "bright_red", "width": 8},
                    {"name": "Importance", "style": "yellow", "width": 12},
                    {"name": "Language", "style": "blue", "width": 12},
                ],
                "row_mapping": {
                    "module_path": "Module",
                    "file_count": "Files",
                    "total_lines": "Lines",
                    "avg_complexity": {
                        "column": "Avg Complexity",
                        "transform": "avg_complex_format",
                    },
                    "max_complexity": {
                        "column": "Max Complexity",
                        "transform": "max_complex_format",
                    },
                    "importance_score": {"column": "Importance", "transform": "importance_format"},
                    "primary_language": "Language",
                },
                "transforms": {
                    "avg_complex_format": {"type": "format", "format": "{avg_complexity:.2f}"},
                    "max_complex_format": {"type": "format", "format": "{max_complexity:.2f}"},
                    "importance_format": {"type": "format", "format": "{importance_score:.2f}"},
                },
            },
        }


class AIModulesComponent(AnalysisComponent):
    """AI modules component showing AI-owned modules."""

    name = "ai_modules"
    description = "AI-owned modules with owner information and data provided"
    default_params = {"limit": 10}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract AI modules data."""
        validated_params = self.validate_params(params)
        limit = validated_params["limit"]

        ai_modules_metadata = results.metadata.get("ai_modules", {})
        ai_modules_count = results.metadata.get("ai_modules_count", 0)

        if ai_modules_count == 0:
            return {
                "data": {"ai_modules": [], "total_count": 0, "truncated_count": 0},
                "display": {"type": "text", "text": ""},
            }

        # Get AI module information
        ai_modules_list = []
        for module_name, ai_info in ai_modules_metadata.items():
            # Determine what data was provided
            data_provided = "Unknown"

            # Check module context for data completeness info
            if module_name in results.module_contexts:
                module_context = results.module_contexts[module_name]
                if hasattr(module_context, "ai_owned") and module_context.ai_owned:
                    data_completeness = module_context.ai_owned.data_completeness
                    if data_completeness:
                        provided = [k for k, v in data_completeness.items() if v]
                        if provided:
                            data_provided = ", ".join(provided[:3])  # Show first 3 types
                        else:
                            data_provided = "Placeholder"
                    elif (
                        hasattr(module_context.ai_owned, "error_message")
                        and module_context.ai_owned.error_message
                    ):
                        data_provided = "Error"
                    else:
                        data_provided = "Full Analysis"

            ai_modules_list.append(
                {
                    "module_name": module_name,
                    "owner_name": ai_info.get("owner_name", "Unknown"),
                    "model": ai_info.get("model", "Unknown"),
                    "data_provided": data_provided,
                }
            )

        # Apply limit
        if limit is not None:
            limited_modules = ai_modules_list[:limit]
            truncated_count = max(0, ai_modules_count - limit)
        else:
            limited_modules = ai_modules_list
            truncated_count = 0

        return {
            "data": {
                "ai_modules": limited_modules,
                "total_count": ai_modules_count,
                "truncated_count": truncated_count,
            },
            "display": {
                "type": "table",
                "title": "🤖 AI-Owned Modules",
                "columns": [
                    {"name": "Module", "style": "cyan", "width": 35},
                    {"name": "Owner", "style": "green", "width": 15},
                    {"name": "Model", "style": "blue", "width": 15},
                    {"name": "Data Provided", "style": "yellow", "width": 20},
                ],
                "row_mapping": {
                    "module_name": "Module",
                    "owner_name": "Owner",
                    "model": "Model",
                    "data_provided": "Data Provided",
                },
                "transforms": {},
            },
        }

    def format_console(self, data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """Format AI modules for console output."""
        ai_modules = data["ai_modules"]
        truncated_count = data["truncated_count"]

        if not ai_modules:
            return ""  # Don't show anything if no AI modules

        rows = []
        for ai_module in ai_modules:
            # Truncate long module names
            module_name = ai_module["module_name"]
            display_name = module_name if len(module_name) <= 38 else module_name[:35] + "..."

            rows.append(
                [
                    display_name,
                    ai_module["owner_name"],
                    ai_module["model"],
                    ai_module["data_provided"],
                ]
            )

        result = {
            "type": "table",
            "title": "🤖 AI Modules",
            "columns": [
                {"name": "Module", "style": "cyan", "width": 29},
                {"name": "Owner Name", "style": "green", "width": 20},
                {"name": "Model", "style": "yellow", "width": 10},
                {"name": "Data Provided", "style": "blue", "width": 33},
            ],
            "rows": rows,
        }

        # Add footer for truncation
        if truncated_count > 0:
            result["footer"] = f"[dim]... and {truncated_count} more AI modules[/dim]"

        return result
