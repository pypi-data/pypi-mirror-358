"""
Core classes and data structures for smart planning system.

This module contains the fundamental data structures used by all smart planning tools,
including tasks, sticky notes, sessions, and enums.
"""

import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class TaskStatus(Enum):
    """Status of a task in the planning system."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class StickyNote:
    """
    A persistent context reminder that appears in tool responses.

    Sticky notes help maintain important context across tool calls,
    ensuring the LLM doesn't forget critical information.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    category: str = "general"  # general, warning, setup, cleanup, process
    priority: int = 1  # 1-5, higher = more important
    created_at: datetime = field(default_factory=datetime.now)
    show_every_n_calls: int = 1  # Show every N tool calls
    calls_since_shown: int = 0
    active: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)  # When to show
    snoozed_until: Optional[datetime] = None  # Snooze feature
    snooze_call_count: int = 0  # Snooze for N calls


@dataclass
class Task:
    """
    Represents a task/thought with rich metadata and analysis.

    Tasks are the core unit of the planning system, representing
    individual thoughts or work items with complexity scoring,
    dependencies, and classification.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    number: int = 0
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    status: TaskStatus = TaskStatus.PENDING

    # Algorithmic scoring
    complexity_score: float = 0.0
    priority_score: float = 1.0
    parallelizable: bool = True

    # Pattern detection
    keywords: Set[str] = field(default_factory=set)
    task_type: Optional[str] = None  # analyze, create, fetch, process, verify, plan

    # Revision tracking (sequential thinking compatibility)
    is_revision: bool = False
    revises_task_id: Optional[str] = None
    revision_count: int = 0

    # Branching support
    branch_id: Optional[str] = None
    branch_depth: int = 0

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class PlanningSession:
    """
    A planning session containing tasks, notes, and analysis.

    This is the main container for all planning data, providing
    both sequential thinking compatibility and enhanced features.
    """

    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    tasks: Dict[str, Task] = field(default_factory=dict)

    # Thinking chain (sequential thinking compatibility)
    thought_sequence: List[str] = field(default_factory=list)
    current_thought_number: int = 0
    total_thoughts_estimate: int = 5

    # Graph structure for dependency analysis
    dependency_graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    reverse_graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))

    # Execution state
    ready_queue: List[str] = field(default_factory=list)
    blocked_tasks: Set[str] = field(default_factory=set)
    completed_tasks: Set[str] = field(default_factory=set)

    # Pattern library (learned heuristics)
    common_patterns: Dict[str, List[str]] = field(default_factory=dict)

    # Metrics
    total_revisions: int = 0
    parallel_opportunities: int = 0

    # Sticky context notes
    sticky_notes: Dict[str, StickyNote] = field(default_factory=dict)
    tool_call_count: int = 0

    # Last update tracking
    last_updated: datetime = field(default_factory=datetime.now)

    # Task extraction cache (for consistent preview/export)
    extracted_task_cache: Optional[List[Task]] = None
    cache_thinking_session_hash: Optional[str] = None

    # Internal todo storage (replaces external MCP calls)
    extracted_todos: List[Dict[str, Any]] = field(default_factory=list)


# Utility functions for working with dataclasses


def task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert Task to dictionary for serialization."""
    task_dict = asdict(task)
    # Convert sets to lists for JSON serialization
    task_dict["keywords"] = list(task.keywords)
    task_dict["dependencies"] = list(task.dependencies)
    task_dict["status"] = task.status.value
    # Convert datetime objects
    task_dict["created_at"] = task.created_at.isoformat()
    if task.completed_at:
        task_dict["completed_at"] = task.completed_at.isoformat()
    return task_dict


def dict_to_task(task_dict: Dict[str, Any]) -> Task:
    """Convert dictionary to Task object."""
    # Handle status enum
    if "status" in task_dict:
        task_dict["status"] = TaskStatus(task_dict["status"])

    # Convert lists back to sets
    if "keywords" in task_dict:
        task_dict["keywords"] = set(task_dict["keywords"])
    if "dependencies" in task_dict:
        task_dict["dependencies"] = set(task_dict["dependencies"])

    # Convert datetime strings back to datetime objects
    if "created_at" in task_dict and isinstance(task_dict["created_at"], str):
        task_dict["created_at"] = datetime.fromisoformat(task_dict["created_at"])
    if "completed_at" in task_dict and task_dict["completed_at"]:
        task_dict["completed_at"] = datetime.fromisoformat(task_dict["completed_at"])

    return Task(**task_dict)


def sticky_note_to_dict(note: StickyNote) -> Dict[str, Any]:
    """Convert StickyNote to dictionary for serialization."""
    note_dict = asdict(note)
    note_dict["created_at"] = note.created_at.isoformat()
    if note.snoozed_until:
        note_dict["snoozed_until"] = note.snoozed_until.isoformat()
    return note_dict


def dict_to_sticky_note(note_dict: Dict[str, Any]) -> StickyNote:
    """Convert dictionary to StickyNote object."""
    if "created_at" in note_dict and isinstance(note_dict["created_at"], str):
        note_dict["created_at"] = datetime.fromisoformat(note_dict["created_at"])
    if "snoozed_until" in note_dict and note_dict["snoozed_until"]:
        note_dict["snoozed_until"] = datetime.fromisoformat(note_dict["snoozed_until"])

    return StickyNote(**note_dict)


def session_to_dict(session: PlanningSession) -> Dict[str, Any]:
    """Convert PlanningSession to dictionary for serialization."""
    session_dict = {
        "session_id": session.session_id,
        "created_at": session.created_at.isoformat(),
        "last_updated": session.last_updated.isoformat(),
        "tasks": {tid: task_to_dict(task) for tid, task in session.tasks.items()},
        "thought_sequence": session.thought_sequence,
        "current_thought_number": session.current_thought_number,
        "total_thoughts_estimate": session.total_thoughts_estimate,
        "dependency_graph": {k: list(v) for k, v in session.dependency_graph.items()},
        "reverse_graph": {k: list(v) for k, v in session.reverse_graph.items()},
        "ready_queue": session.ready_queue,
        "blocked_tasks": list(session.blocked_tasks),
        "completed_tasks": list(session.completed_tasks),
        "common_patterns": session.common_patterns,
        "total_revisions": session.total_revisions,
        "parallel_opportunities": session.parallel_opportunities,
        "sticky_notes": {
            nid: sticky_note_to_dict(note) for nid, note in session.sticky_notes.items()
        },
        "tool_call_count": session.tool_call_count,
        "extracted_task_cache": (
            [task_to_dict(task) for task in session.extracted_task_cache]
            if session.extracted_task_cache
            else None
        ),
        "cache_thinking_session_hash": session.cache_thinking_session_hash,
        "extracted_todos": session.extracted_todos,
    }

    return session_dict


def dict_to_session(session_dict: Dict[str, Any]) -> PlanningSession:
    """Convert dictionary to PlanningSession object."""
    # Create session with basic fields
    session = PlanningSession(session_id=session_dict["session_id"])
    session.created_at = datetime.fromisoformat(session_dict["created_at"])
    session.last_updated = datetime.fromisoformat(
        session_dict.get("last_updated", session_dict["created_at"])
    )

    # Reconstruct tasks
    for tid, task_dict in session_dict["tasks"].items():
        session.tasks[tid] = dict_to_task(task_dict)

    # Reconstruct other fields
    session.thought_sequence = session_dict["thought_sequence"]
    session.current_thought_number = session_dict["current_thought_number"]
    session.total_thoughts_estimate = session_dict["total_thoughts_estimate"]
    session.dependency_graph = defaultdict(
        set, {k: set(v) for k, v in session_dict["dependency_graph"].items()}
    )
    session.reverse_graph = defaultdict(
        set, {k: set(v) for k, v in session_dict["reverse_graph"].items()}
    )
    session.ready_queue = session_dict["ready_queue"]
    session.blocked_tasks = set(session_dict["blocked_tasks"])
    session.completed_tasks = set(session_dict["completed_tasks"])
    session.common_patterns = session_dict["common_patterns"]
    session.total_revisions = session_dict["total_revisions"]
    session.parallel_opportunities = session_dict["parallel_opportunities"]
    session.tool_call_count = session_dict["tool_call_count"]

    # Reconstruct sticky notes
    for nid, note_dict in session_dict["sticky_notes"].items():
        session.sticky_notes[nid] = dict_to_sticky_note(note_dict)

    # Reconstruct task cache
    if session_dict.get("extracted_task_cache"):
        session.extracted_task_cache = [
            dict_to_task(task_dict) for task_dict in session_dict["extracted_task_cache"]
        ]
    session.cache_thinking_session_hash = session_dict.get("cache_thinking_session_hash")

    # Reconstruct extracted todos
    session.extracted_todos = session_dict.get("extracted_todos", [])

    return session


# Constants for the planning system
DEFAULT_TTL_SECONDS = 7 * 24 * 60 * 60  # 1 week
CONTEXT_GROWTH_THRESHOLD = 1000  # Tokens
MAX_COMPLEXITY_THRESHOLD = 0.7  # When to suggest decomposition
MAX_PARALLEL_BATCH_SIZE = 3  # Optimal parallel execution batch size

# Task type classifications
TASK_TYPES = {
    "analyze": ["analyze", "evaluate", "assess", "examine", "study", "review"],
    "create": ["create", "build", "make", "generate", "produce", "develop"],
    "fetch": ["fetch", "get", "retrieve", "find", "search", "collect"],
    "process": ["process", "transform", "convert", "parse", "format", "clean"],
    "verify": ["verify", "check", "validate", "test", "confirm", "ensure"],
    "plan": ["plan", "organize", "structure", "outline", "design", "prepare"],
}

# Sticky note categories
NOTE_CATEGORIES = {
    "general": "General reminders and context",
    "warning": "Important warnings or constraints",
    "setup": "Prerequisites or setup steps",
    "cleanup": "Post-task cleanup reminders",
    "process": "Process or methodology reminders",
}

# Security-related keywords for smart planning
SECURITY_KEYWORDS = [
    "password",
    "secret",
    "key",
    "token",
    "auth",
    "credential",
    "api_key",
    "private",
    "sensitive",
    "encrypted",
    "decrypt",
]

# File patterns that suggest sensitive operations
SENSITIVE_FILE_PATTERNS = [
    ".env",
    "secret",
    "password",
    "key",
    "credential",
    "config",
    "settings",
    "auth",
    "token",
    "private",
]
