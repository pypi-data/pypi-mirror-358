"""
Type definitions for unified parsing.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from tree_sitter import Node, Tree

from ..types import GuardTag, PermissionRange


@dataclass
class LineContext:
    """Context information for a single line."""

    line_number: int  # 1-based
    text: str
    node_type: str = "unknown"
    language_id: str = "text"
    is_empty: bool = False
    has_guard_tag: bool = False


@dataclass
class UnifiedParseResult:
    """Result of unified document parsing containing all extracted information."""

    # Core tree-sitter data (existing)
    tree: Optional[Tree]
    root_node: Optional[Node]
    language_id: str
    success: bool
    content: str
    error_message: Optional[str] = None

    # Guard tags extracted during parsing
    guard_tags: List[GuardTag] = field(default_factory=list)
    permission_ranges: List[PermissionRange] = field(default_factory=list)

    # Metrics calculated during parsing
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[Dict[str, Any]] = field(default_factory=list)
    exports: List[Dict[str, Any]] = field(default_factory=list)

    # Tree-sitter metrics
    total_nodes: int = 0
    named_nodes: int = 0
    max_depth: int = 0
    function_count: int = 0
    class_count: int = 0
    complexity_score: float = 0.0

    # Line-by-line analysis
    line_contexts: Dict[int, LineContext] = field(default_factory=dict)

    # Parse metrics
    line_count: int = 0
    byte_count: int = 0
