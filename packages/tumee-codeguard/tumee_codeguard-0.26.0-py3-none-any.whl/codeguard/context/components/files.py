"""
File analysis components showing top files by various metrics.
"""

from typing import Any, Dict, List, Union

from rich.console import Console
from rich.table import Table

from ...core.components.base import AnalysisComponent
from ...core.runtime import get_default_console
from ..models import AnalysisResults

console = get_default_console()


def _smart_truncate_path(path: str, max_length: int = 50) -> str:
    """Smart truncation that uses maximum available space while preserving filename."""
    if len(path) <= max_length:
        return path

    # Split path into parts
    parts = path.split("/")
    if len(parts) <= 2:
        # Short path, just truncate from middle
        if len(path) > max_length:
            excess = len(path) - max_length + 3  # +3 for "..."
            start_keep = (len(path) - excess) // 2
            return path[:start_keep] + "..." + path[start_keep + excess :]
        return path

    filename = parts[-1]
    first_dir = parts[0] if parts else ""

    # Calculate minimum space needed: first_dir + "/" + "..." + "/" + filename
    min_space_needed = len(first_dir) + 1 + 3 + 1 + len(filename)  # = first_dir/.../filename

    if min_space_needed > max_length:
        # Even minimal truncation won't fit, need to truncate filename too
        available_for_filename = max_length - len(first_dir) - 5  # -5 for "/.../."
        if "." in filename and available_for_filename > 5:
            name_part, ext = filename.rsplit(".", 1)
            name_chars = available_for_filename - len(ext) - 1  # -1 for "."
            if name_chars > 0:
                return f"{first_dir}/.../{name_part[:name_chars]}.{ext}"
        return f"{first_dir}/.../{filename[:available_for_filename]}"

    # We have space to work with. Calculate how much middle path we can include
    available_for_middle = (
        max_length - len(first_dir) - len(filename) - 2
    )  # -2 for "/" at start and end

    if len(parts) == 3:
        # Simple case: first_dir/middle/filename
        middle = parts[1]
        if len(middle) <= available_for_middle:
            return path  # Original path fits
        else:
            # Truncate the middle directory
            chars_to_keep = available_for_middle - 3  # -3 for "..."
            if chars_to_keep > 0:
                return f"{first_dir}/{middle[:chars_to_keep]}.../{filename}"
            else:
                return f"{first_dir}/.../{filename}"

    # Multiple middle directories - try to fit as much as possible
    middle_parts = parts[1:-1]
    full_middle = "/".join(middle_parts)

    if len(full_middle) <= available_for_middle:
        return path  # Original path fits

    # Need to truncate middle path. Try to keep some of it
    if available_for_middle > 3:  # Room for "..."
        chars_to_keep = available_for_middle - 3
        return f"{first_dir}/{full_middle[:chars_to_keep]}.../{filename}"
    else:
        # No room for middle content, just use "..."
        return f"{first_dir}/.../{filename}"


class TopFilesContextComponent(AnalysisComponent):
    """Top files by context lines component."""

    name = "top_files_context"
    description = "Top files by AI context lines"
    default_params = {"limit": 10}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract top files by context lines."""
        validated_params = self.validate_params(params)
        limit = validated_params["limit"]

        all_files = []
        seen_files = set()

        # Extract file information from module contexts
        for module_name, module_context in results.module_contexts.items():
            if hasattr(module_context, "file_analyses"):
                for file_path, file_data in module_context.file_analyses.items():
                    if isinstance(file_data, dict):
                        # Create full path for the file
                        full_path = f"{module_name}/{file_path}" if module_name else file_path

                        # Skip if we've already seen this file
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        context_line_count = file_data.get("context_line_count", 0)
                        if context_line_count > 0:  # Only include files with context
                            all_files.append(
                                {
                                    "path": full_path,
                                    "lines": file_data.get("line_count", 0),
                                    "size_bytes": file_data.get("size_bytes", 0),
                                    "context_line_count": context_line_count,
                                    "language": file_data.get("language", "unknown"),
                                }
                            )

        # Sort by context lines
        all_files.sort(key=lambda x: x["context_line_count"], reverse=True)

        # Apply limit
        if limit is not None:
            top_files = all_files[:limit]
        else:
            top_files = all_files

        return {
            "data": {
                "files": top_files,
                "total_context_files": len(all_files),
            },
            "display": {
                "type": "table",
                "title": "📍 Top Files by Context Lines",
                "columns": [
                    {"name": "File", "style": "cyan", "width": 54},
                    {"name": "Lines", "style": "green", "width": 7},
                    {"name": "Size", "style": "yellow", "width": 10},
                    {"name": "Context Lines", "style": "purple", "width": 13},
                    {"name": "Language", "style": "blue", "width": 4},
                ],
                "row_mapping": {
                    "path": {"column": "File", "transform": "truncate_path"},
                    "lines": "Lines",
                    "size_bytes": {"column": "Size", "transform": "size_kb"},
                    "context_line_count": "Context Lines",
                    "language": "Language",
                },
                "transforms": {
                    "truncate_path": {"type": "truncate_path"},
                    "size_kb": {"type": "format", "format": "{size_kb:.1f}"},
                },
            },
        }


class TopFilesLinesComponent(AnalysisComponent):
    """Top files by lines of code component."""

    name = "top_files_lines"
    description = "Top files by lines of code"
    default_params = {"limit": 10}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract top files by lines of code."""
        validated_params = self.validate_params(params)
        limit = validated_params["limit"]

        all_files = []
        seen_files = set()

        # Extract file information from module contexts
        for module_name, module_context in results.module_contexts.items():
            if hasattr(module_context, "file_analyses"):
                for file_path, file_data in module_context.file_analyses.items():
                    if isinstance(file_data, dict):
                        # Create full path for the file
                        full_path = f"{module_name}/{file_path}" if module_name else file_path

                        # Skip if we've already seen this file
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        all_files.append(
                            {
                                "path": full_path,
                                "lines": file_data.get("line_count", 0),
                                "size_bytes": file_data.get("size_bytes", 0),
                                "complexity": file_data.get("complexity_score", 0.0),
                                "language": file_data.get("language", "unknown"),
                            }
                        )

        # Sort by lines of code
        all_files.sort(key=lambda x: x["lines"], reverse=True)

        # Apply limit
        if limit is not None:
            top_files = all_files[:limit]
        else:
            top_files = all_files

        return {
            "data": {"files": top_files},
            "display": {
                "type": "table",
                "title": "📄 Top Files by Lines of Code",
                "columns": [
                    {"name": "File", "style": "cyan", "width": 54},
                    {"name": "Lines", "style": "green", "width": 7},
                    {"name": "Size", "style": "yellow", "width": 10},
                    {"name": "Complexity", "style": "red", "width": 13},
                    {"name": "Language", "style": "blue", "width": 16},
                ],
                "row_mapping": {
                    "path": {"column": "File", "transform": "truncate_path"},
                    "lines": "Lines",
                    "size_bytes": {"column": "Size", "transform": "size_kb"},
                    "complexity": {"column": "Complexity", "transform": "complexity_format"},
                    "language": "Language",
                },
                "transforms": {
                    "truncate_path": {"type": "truncate_path"},
                    "size_kb": {"type": "format", "format": "{size_kb:.1f}"},
                    "complexity_format": {"type": "format", "format": "{complexity:.2f}"},
                },
            },
        }


class TopFilesComplexityComponent(AnalysisComponent):
    """Top files by complexity score component."""

    name = "top_files_complexity"
    description = "Top files by complexity score"
    default_params = {"limit": 10}

    async def extract(self, results: AnalysisResults, **params) -> Dict[str, Any]:
        """Extract top files by complexity."""
        validated_params = self.validate_params(params)
        limit = validated_params["limit"]

        all_files = []
        seen_files = set()

        # Extract file information from module contexts
        for module_name, module_context in results.module_contexts.items():
            if hasattr(module_context, "file_analyses"):
                for file_path, file_data in module_context.file_analyses.items():
                    if isinstance(file_data, dict):
                        # Create full path for the file
                        full_path = f"{module_name}/{file_path}" if module_name else file_path

                        # Skip if we've already seen this file
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        complexity = file_data.get("complexity_score", 0.0)
                        if complexity > 0:  # Only include files with actual complexity scores
                            size_bytes = file_data.get("size_bytes", 0)
                            all_files.append(
                                {
                                    "path": full_path,
                                    "lines": file_data.get("line_count", 0),
                                    "size_bytes": size_bytes,
                                    "size_kb": size_bytes / 1024,
                                    "complexity": complexity,
                                    "language": file_data.get("language", "unknown"),
                                }
                            )

        # Sort by complexity
        all_files.sort(key=lambda x: x["complexity"], reverse=True)

        # Apply limit
        if limit is not None:
            top_files = all_files[:limit]
        else:
            top_files = all_files

        return {
            "data": {"files": top_files},
            "display": {
                "type": "table",
                "title": "🧠 Top Files by Complexity Score",
                "columns": [
                    {"name": "File", "style": "cyan", "width": 54},
                    {"name": "Lines", "style": "green", "width": 7},
                    {"name": "Size", "style": "yellow", "width": 10},
                    {"name": "Complexity", "style": "red", "width": 13},
                    {"name": "Language", "style": "blue", "width": 16},
                ],
                "row_mapping": {
                    "path": {"column": "File", "transform": "truncate_path"},
                    "lines": "Lines",
                    "size_bytes": {"column": "Size", "transform": "size_kb"},
                    "complexity": {"column": "Complexity", "transform": "complexity_format"},
                    "language": "Language",
                },
                "transforms": {
                    "truncate_path": {"type": "format", "format": "{path}"},
                    "size_kb": {"type": "format", "format": "{size_kb:.1f}"},
                    "complexity_format": {"type": "format", "format": "{complexity:.2f}"},
                },
            },
        }
