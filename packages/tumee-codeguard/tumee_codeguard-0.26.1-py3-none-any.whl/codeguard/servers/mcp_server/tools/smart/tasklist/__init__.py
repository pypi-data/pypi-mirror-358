"""
Smart Tasklist Module.

Task extraction from thinking sessions and integration with
external todo/task management systems.
"""

# Export task extraction functionality
from .extraction import extract_tasks_from_thinking_session

# Export todo integration functionality
from .todo_integration import (
    format_tasks_for_display,
    preview_session_tasks,
)

__all__ = [
    "extract_tasks_from_thinking_session",
    "preview_session_tasks",
    "format_tasks_for_display",
]
