"""
CodeGuard Context Scanner Module

Intelligent code context management system that maintains fresh, multi-resolution
context of entire codebases for LLM consumption. Features distributed caching,
incremental updates, and hierarchical analysis.

Key Components:
- scanner.py: Main context scanning engine
- models.py: Data structures and enums
- cache_integration.py: Integration with existing cache system
"""

from .models import AnalysisMode, ChangeImpact, FileChange, ModuleMetadata
from .scanner import CodeGuardContextScanner

__all__ = [
    "CodeGuardContextScanner",
    "AnalysisMode",
    "ChangeImpact",
    "FileChange",
    "ModuleMetadata",
]
