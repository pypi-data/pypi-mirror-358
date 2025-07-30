"""
Core types for the parsing module - platform agnostic
Exact port of VSCode src/core/types.ts
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from .interfaces import (
    ICacheManager,
    ICoreConfiguration,
    IDocument,
    IExtensionContext,
    IFileSystemAccess,
    ISecurityManager,
    ITextLine,
)


# Shared exceptions
class SecurityError(Exception):
    """Raised when filesystem access violates security boundaries."""

    pass


@dataclass
class ScopeBoundary:
    """Represents a scope boundary in the document"""

    startLine: int
    endLine: int
    type: str


@dataclass
class IParsingConfig:
    """Configuration interface for parsing behavior"""

    enablePerformanceMonitoring: Optional[bool] = None
    maxFileSize: Optional[int] = None
    chunkSize: Optional[int] = None


@dataclass
class ParseResult:
    """Result of parsing a document with tree-sitter"""

    tree: Any  # Tree type from tree-sitter
    languageId: str
    success: bool
    error: Optional[str] = None


@dataclass
class NodePosition:
    """Node position information"""

    row: int
    column: int


@dataclass
class NodeBoundaries:
    """Node boundaries information"""

    startLine: int
    endLine: int
    startColumn: int
    endColumn: int


# Default permissions for AI and human targets
# These are used when no guard tags are present
DEFAULT_PERMISSIONS = {
    "ai": "r",  # AI has read-only access by default
    "human": "w",  # Human has write access by default
}

# Type for permission values
PermissionValue = Literal["r", "w", "n"]

# Type for permission targets
PermissionTarget = Literal["ai", "human"]


@dataclass
class GuardTag:
    """Guard tag information"""

    lineNumber: int
    identifier: Optional[str] = None
    scope: Optional[str] = None
    lineCount: Optional[int] = None
    addScopes: Optional[List[str]] = None
    removeScopes: Optional[List[str]] = None
    scopeStart: Optional[int] = None
    scopeEnd: Optional[int] = None
    # Store the actual permissions for each target
    aiPermission: Optional[Literal["r", "w", "n", "contextWrite"]] = None
    humanPermission: Optional[Literal["r", "w", "n", "contextWrite"]] = None
    # Track if permissions are context-based
    aiIsContext: Optional[bool] = None
    humanIsContext: Optional[bool] = None


@dataclass
class PermissionRange:
    """Range-based permission information for multiple consecutive lines"""

    start_line: int
    end_line: int
    permissions: Dict[str, str]  # e.g., { 'ai': 'w', 'human': 'r' }
    isContext: Dict[str, bool]  # e.g., { 'ai': True, 'human': False }
    identifier: Optional[str] = None

    def contains_line(self, line_number: int) -> bool:
        """Check if this range contains the given line number."""
        return self.start_line <= line_number <= self.end_line

    def can_extend(
        self,
        line: int,
        permissions: Dict[str, str],
        isContext: Dict[str, bool],
        identifier: Optional[str],
    ) -> bool:
        """Check if this range can be extended with the given line."""
        return (
            line == self.end_line + 1  # Must be contiguous
            and self.permissions == permissions
            and self.isContext == isContext
            and self.identifier == identifier
        )

    def extend_to(self, line: int) -> None:
        """Extend this range to include the given line."""
        if line > self.end_line:
            self.end_line = line

    def get_line_permission(self, line_number: int) -> Dict[str, Any]:
        """Get permission info for a specific line within this range."""
        if not self.contains_line(line_number):
            raise ValueError(f"Line {line_number} not in range {self.start_line}-{self.end_line}")

        return {
            "line": line_number,
            "permissions": self.permissions,
            "isContext": self.isContext,
            "identifier": self.identifier,
        }


@dataclass
class GuardStackEntry:
    """Stack entry for guard processing - contains complete permission state"""

    permissions: Dict[str, str]  # e.g., { 'ai': 'w', 'human': 'r' }
    isContext: Dict[str, bool]  # e.g., { 'ai': True, 'human': False }
    startLine: int
    endLine: int
    isLineLimited: bool
    sourceGuard: Optional[GuardTag] = None  # The guard that triggered this state change


@dataclass
class ContextFileInfo:
    """Enhanced context file info with hierarchical level tracking"""

    path: str
    relative_path: str
    level: int  # Absolute level from root (0, 1, 2, 3...)
    root_path: str  # Which registered root this came from
    rule: str
    filter_reason: str
    metadata: Optional[Dict] = None


def calculate_absolute_level(file_path: Path, root_path: Path) -> int:
    """
    Calculate absolute level from root regardless of traversal direction.

    Level 0: Root directory itself
    Level 1: Direct children of root
    Level 2: Second level directories/files
    Level 3+: Deeper levels

    Args:
        file_path: Path to calculate level for
        root_path: Registered root path

    Returns:
        int: Absolute level from root (0-based), -1 if outside root
    """
    try:
        relative = file_path.relative_to(root_path)
        if str(relative) == ".":  # Root itself
            return 0
        # For files, level is based on containing directory
        # For directories, level is based on depth
        return len(relative.parts) - (1 if file_path.is_file() else 0)
    except ValueError:
        return -1  # Outside root boundaries
