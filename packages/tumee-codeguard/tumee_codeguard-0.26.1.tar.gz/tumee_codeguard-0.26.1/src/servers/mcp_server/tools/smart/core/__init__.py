"""
Smart Core Module.

Core data structures, session management, caching, and utilities
for the smart planning system.
"""

# Export cache utilities
from .cache import get_cache

# Export core data structures
from .data_models import (
    TASK_TYPES,
    PlanningSession,
    StickyNote,
    Task,
    TaskStatus,
    dict_to_session,
    dict_to_sticky_note,
    dict_to_task,
    session_to_dict,
    sticky_note_to_dict,
    task_to_dict,
)

# Export session management
from .session_manager import (
    get_or_create_session,
    get_session,
    get_session_stats,
    save_session_to_cache,
    sync_memory_with_cache,
    update_session_tool_call_count,
)

# Export shared utilities
from .utils import (
    cleanup_old_sessions,
    clear_complete_session,
    is_session_clearable,
)

__all__ = [
    # Data models
    "Task",
    "TaskStatus",
    "StickyNote",
    "PlanningSession",
    "task_to_dict",
    "dict_to_task",
    "sticky_note_to_dict",
    "dict_to_sticky_note",
    "session_to_dict",
    "dict_to_session",
    "TASK_TYPES",
    # Session management
    "get_session",
    "get_or_create_session",
    "update_session_tool_call_count",
    "save_session_to_cache",
    "sync_memory_with_cache",
    "get_session_stats",
    # Cache
    "get_cache",
    # Utils
    "clear_complete_session",
    "is_session_clearable",
    "cleanup_old_sessions",
]
