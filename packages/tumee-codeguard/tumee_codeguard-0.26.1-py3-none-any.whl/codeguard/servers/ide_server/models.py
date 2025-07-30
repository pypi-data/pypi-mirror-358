"""
Data models for IDE Server.

This module contains the core data structures used for IDE communication
and document state management.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class TextChange:
    """Represents a text change for delta updates"""

    startLine: int
    startChar: int
    endLine: int
    endChar: int
    newText: str


@dataclass
class WorkerDocument:
    """Document state maintained by worker"""

    fileName: str
    languageId: str
    content: str
    version: int
    lines: List[str]
    guardTags: List[Dict[str, Any]]
    linePermissions: List[Dict[str, Any]]
