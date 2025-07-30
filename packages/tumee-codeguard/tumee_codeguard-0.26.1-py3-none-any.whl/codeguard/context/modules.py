"""
Module utility functions for CodeGuard context analysis.

This module provides utility functions for working with module contexts,
language detection, and analysis results.
"""

from typing import Any, Dict

from ..core.language.config import get_language_display_name
from .models import AnalysisResults, ModuleContext


def calculate_primary_language(file_analyses: Dict[str, Dict[str, Any]]) -> str:
    """
    Calculate the primary language for a module based on file analyses.

    Args:
        file_analyses: Dictionary of file path -> file analysis data

    Returns:
        Primary language identifier (before display formatting)
    """
    if not file_analyses:
        return "unknown"

    # Count languages by file count
    language_counts = {}

    for file_path, file_data in file_analyses.items():
        if isinstance(file_data, dict):
            language = file_data.get("language", "unknown")
            language_counts[language] = language_counts.get(language, 0) + 1

    if not language_counts:
        return "unknown"

    # Return the language with the most files
    return max(language_counts.items(), key=lambda x: x[1])[0]


def get_module_primary_language_display(analysis_results: AnalysisResults, module_name: str) -> str:
    """
    Get the display-formatted primary language for a module from analysis results.

    Args:
        analysis_results: The analysis results containing module contexts
        module_name: Name of the module

    Returns:
        Display-formatted language name (e.g., "Python", "JavaScript", "Mixed")
    """
    try:
        if module_name not in analysis_results.module_contexts:
            return "Mixed"

        module_context = analysis_results.module_contexts[module_name]

        # Handle both ModuleContext objects and dict representations
        if hasattr(module_context, "primary_language"):
            primary_language = module_context.primary_language
        elif isinstance(module_context, dict):
            primary_language = module_context.get("primary_language", "unknown")
        else:
            return "Mixed"

        return get_language_display_name(primary_language)

    except Exception:
        return "Mixed"


def get_module_primary_language_from_dict(module_name: str, result_dict: Dict[str, Any]) -> str:
    """
    Get the primary language from a dict representation of analysis results.

    Args:
        module_name: Name of the module
        result_dict: Dictionary representation of analysis results

    Returns:
        Display-formatted language name (e.g., "Python", "JavaScript", "Mixed")
    """
    try:
        # Get module contexts from metadata
        metadata = result_dict.get("metadata", {})
        module_contexts = metadata.get("module_contexts", {})

        if module_name not in module_contexts:
            return "Mixed"

        module_context = module_contexts[module_name]
        if not isinstance(module_context, dict):
            return "Mixed"

        # Get the stored primary language and format it for display
        primary_language = module_context.get("primary_language", "unknown")
        return get_language_display_name(primary_language)

    except Exception:
        return "Mixed"
