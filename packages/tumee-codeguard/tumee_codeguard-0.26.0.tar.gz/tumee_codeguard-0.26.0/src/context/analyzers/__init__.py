"""
Context Analysis Components

This module provides analyzers that integrate with existing CodeGuard infrastructure
to perform static analysis, dependency tracking, and hierarchical scanning.

Components:
- static_analyzer.py: Integrates with tree_sitter_parser for AST analysis
- dependency_analyzer.py: Builds import/export graphs using fs_walker patterns
- breadth_scanner.py: Leverages get_context_files_breadth_first for structure analysis
"""

from .breadth_scanner import BreadthFirstScanner
from .dependency_analyzer import DependencyAnalyzer
from .static_analyzer import StaticAnalyzer

__all__ = [
    "StaticAnalyzer",
    "DependencyAnalyzer",
    "BreadthFirstScanner",
]
