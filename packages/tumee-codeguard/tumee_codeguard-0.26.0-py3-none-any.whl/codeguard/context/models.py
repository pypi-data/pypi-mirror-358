"""
Data models and structures for the CodeGuard context scanner.

This module defines the core data structures used throughout the context
scanning system, including analysis modes, change tracking, and metadata.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.interfaces import IModuleContext


class AnalysisMode(Enum):
    """Analysis modes for context scanning."""

    FULL = "full"  # Analyze everything (default)
    INCREMENTAL = "incremental"  # Only changed files


class ChangeImpact(Enum):
    """Impact level of changes on the codebase."""

    LOCAL = "local"  # Changes only affect this module
    NEIGHBORS = "neighbors"  # Changes affect direct dependencies
    GLOBAL = "global"  # Changes affect entire project


class OutputLevel(Enum):
    """Different levels of output detail."""

    OVERVIEW = "overview"  # High-level summaries only
    STRUCTURE = "structure"  # File organization and dependencies
    API = "api"  # Public interfaces and exports
    IMPLEMENTATION = "implementation"  # Internal logic and algorithms
    DETAILED = "detailed"  # All functions, comments, identifiers
    FULL = "full"  # Complete AST and raw data
    CONTEXT = "context"  # Only show context-related information


@dataclass
class FileChange:
    """Represents a file change detected by the system."""

    path: str
    change_type: str  # added, modified, deleted
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    lines_changed: int = 0
    change_timestamp: datetime = field(default_factory=datetime.now)
    author: str = "unknown"
    commit_message: str = ""

    def __post_init__(self):
        """Ensure change_timestamp is a datetime object."""
        if isinstance(self.change_timestamp, str):
            self.change_timestamp = datetime.fromisoformat(self.change_timestamp)


@dataclass
class ChangeAnalysis:
    """Analysis of changes and their impact on the codebase."""

    files_changed: List[FileChange]
    modules_affected: Set[str]
    total_lines_changed: int = 0
    change_velocity: float = 0.0  # Changes per day for this module
    is_hotfix: bool = False  # Sudden change to stable code
    is_new_development: bool = False  # Lots of changes to new code
    api_changes: List[Dict[str, Any]] = field(default_factory=list)  # Public API changes
    impact_level: ChangeImpact = ChangeImpact.LOCAL
    propagation_needed: bool = False  # Should we update dependent modules?


@dataclass
class ModuleMetadata:
    """Metadata about a module for change tracking and analysis."""

    path: str
    last_analyzed: datetime = field(default_factory=datetime.now)
    last_changed: datetime = field(default_factory=datetime.now)
    file_hashes: Dict[str, str] = field(default_factory=dict)  # file -> hash
    total_files: int = 0
    total_lines: int = 0
    change_frequency: float = 0.0  # Average changes per day
    stability_score: float = 0.5  # 0-1, higher = more stable
    importance_score: float = 0.5  # 0-1, higher = more important
    is_new: bool = False  # Less than 30 days old
    dependent_modules: List[str] = field(default_factory=list)  # Who depends on us
    dependencies: List[str] = field(default_factory=list)  # Who we depend on

    def __post_init__(self):
        """Ensure datetime fields are properly typed."""
        if isinstance(self.last_analyzed, str):
            self.last_analyzed = datetime.fromisoformat(self.last_analyzed)
        if isinstance(self.last_changed, str):
            self.last_changed = datetime.fromisoformat(self.last_changed)


@dataclass
class IncrementalUpdate:
    """Result of an incremental context update."""

    updated_modules: List[str] = field(default_factory=list)
    propagated_modules: List[str] = field(
        default_factory=list
    )  # Modules updated due to dependencies
    skipped_modules: List[str] = field(default_factory=list)  # Modules that didn't need updates
    total_llm_calls: int = 0
    cache_hits: int = 0
    update_reason: str = ""
    elapsed_time: float = 0.0


@dataclass
class AIModuleMetadata:
    """Metadata about AI module data completeness and source."""

    owner_name: str
    model: str
    data_completeness: Dict[str, bool] = field(default_factory=dict)
    analysis_level: str = "unknown"
    last_analysis: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ModuleContext(IModuleContext):
    """Context information for a single module."""

    path: str
    module_summary: str = ""
    file_analyses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    api_catalog: Dict[str, Any] = field(default_factory=dict)
    callers: Dict[str, List[str]] = field(default_factory=dict)  # Who calls this module
    dependencies: Dict[str, List[str]] = field(default_factory=dict)  # What this module depends on
    complexity_score: float = 0.0
    primary_language: str = "unknown"  # Dominant language in this module
    ai_owned: Optional[AIModuleMetadata] = None  # AI ownership metadata if AI-owned
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Optional[ModuleMetadata] = None  # Module metadata for tracking and analysis

    def __post_init__(self):
        """Ensure datetime fields are properly typed."""
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ModuleContext to dictionary for caching."""
        # Serialize ai_owned AIModuleMetadata to dict if present
        ai_owned_dict = None
        if self.ai_owned:
            ai_owned_dict = {
                "owner_name": self.ai_owned.owner_name,
                "model": self.ai_owned.model,
                "data_completeness": self.ai_owned.data_completeness,
                "analysis_level": self.ai_owned.analysis_level,
                "last_analysis": self.ai_owned.last_analysis,
                "error_message": self.ai_owned.error_message,
            }

        # Serialize metadata ModuleMetadata to dict if present
        metadata_dict = None
        if self.metadata:
            metadata_dict = {
                "path": self.metadata.path,
                "last_analyzed": self.metadata.last_analyzed.isoformat(),
                "last_changed": self.metadata.last_changed.isoformat(),
                "file_hashes": self.metadata.file_hashes,
                "total_files": self.metadata.total_files,
                "total_lines": self.metadata.total_lines,
                "change_frequency": self.metadata.change_frequency,
                "stability_score": self.metadata.stability_score,
                "importance_score": self.metadata.importance_score,
                "is_new": self.metadata.is_new,
                "dependent_modules": self.metadata.dependent_modules,
                "dependencies": self.metadata.dependencies,
            }

        return {
            "path": self.path,
            "module_summary": self.module_summary,
            "file_analyses": self.file_analyses,
            "api_catalog": self.api_catalog,
            "callers": self.callers,
            "dependencies": self.dependencies,
            "complexity_score": self.complexity_score,
            "primary_language": self.primary_language,
            "ai_owned": ai_owned_dict,
            "last_updated": self.last_updated.isoformat(),
            "metadata": metadata_dict,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModuleContext":
        """Reconstruct ModuleContext from cached dictionary."""
        data = data.copy()  # Don't modify original

        # Handle datetime deserialization
        if "last_updated" in data and isinstance(data["last_updated"], str):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])

        # Handle AIModuleMetadata deserialization
        if "ai_owned" in data and data["ai_owned"] is not None:
            if isinstance(data["ai_owned"], dict):
                data["ai_owned"] = AIModuleMetadata(**data["ai_owned"])

        # Handle ModuleMetadata deserialization
        if "metadata" in data and data["metadata"] is not None:
            if isinstance(data["metadata"], dict):
                metadata_data = data["metadata"].copy()
                # Handle datetime fields in metadata
                if "last_analyzed" in metadata_data and isinstance(
                    metadata_data["last_analyzed"], str
                ):
                    metadata_data["last_analyzed"] = datetime.fromisoformat(
                        metadata_data["last_analyzed"]
                    )
                if "last_changed" in metadata_data and isinstance(
                    metadata_data["last_changed"], str
                ):
                    metadata_data["last_changed"] = datetime.fromisoformat(
                        metadata_data["last_changed"]
                    )
                data["metadata"] = ModuleMetadata(**metadata_data)

        return cls(**data)


@dataclass
class ProjectSummary:
    """High-level project analysis summary."""

    project_overview: str = ""
    architecture_overview: str = ""
    key_patterns: List[str] = field(default_factory=list)
    tech_stack: Dict[str, Any] = field(default_factory=dict)
    module_count: int = 0
    total_files: int = 0
    total_lines: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    analysis_mode: AnalysisMode = AnalysisMode.FULL

    def __post_init__(self):
        """Ensure datetime fields are properly typed."""
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)


@dataclass
class AnalysisResults:
    """Complete analysis results for a project."""

    project_summary: ProjectSummary
    breadth_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    module_contexts: Dict[str, ModuleContext] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_modules_analyzed(self) -> int:
        """Number of modules with detailed analysis."""
        return len(self.module_contexts)

    @property
    def total_breadth_modules(self) -> int:
        """Number of modules with breadth-first summaries."""
        return len(self.breadth_summaries)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AnalysisResults to dictionary format for display purposes.

        Returns:
            Dictionary representation compatible with existing display functions
        """
        return {
            "project_overview": {
                "total_files": self.project_summary.total_files,
                "module_count": self.project_summary.module_count,
                "structure_summary": self.project_summary.project_overview,
            },
            "modules": {
                module_path: {
                    "file_count": (
                        len(context.file_analyses) if hasattr(context, "file_analyses") else 0
                    ),
                    "importance_score": (
                        context.complexity_score if hasattr(context, "complexity_score") else 0.0
                    ),
                }
                for module_path, context in self.module_contexts.items()
            },
            "performance_metrics": {
                "total_time_seconds": self.metadata.get("analysis_time_seconds", 0.0),
                "cache_hits": self.metadata.get("modules_from_cache", 0),
                "fresh_analysis": self.metadata.get("modules_analyzed_fresh", 0),
                "files_from_cache": self.metadata.get("files_from_cache", 0),
                "files_analyzed": self.metadata.get("files_analyzed_fresh", 0),
                "cache_efficiency": self.metadata.get("cache_efficiency", 0.0),
                "llm_calls_made": 0,  # TODO: Add LLM call tracking
            },
            "metadata": {
                **self.metadata,
                # Include module contexts for detailed file analysis
                "module_contexts": {
                    module_path: (context.to_dict() if hasattr(context, "to_dict") else context)
                    for module_path, context in self.module_contexts.items()
                },
            },
        }


# Cache key patterns for integration with existing cache system
CACHE_KEY_PATTERNS = {
    "breadth": "context:breadth:{path}",
    "module": "context:module:{path}",
    "project": "context:project:{key}",
    "metadata": "context:metadata:{path}",
    "dependencies": "context:deps:{path}",
}


def make_cache_key(pattern_type: str, **kwargs) -> str:
    """Generate cache key using predefined patterns."""
    if pattern_type not in CACHE_KEY_PATTERNS:
        raise ValueError(f"Unknown cache key pattern: {pattern_type}")

    return CACHE_KEY_PATTERNS[pattern_type].format(**kwargs)


# Default thresholds and constants
DEFAULT_THRESHOLDS = {
    "hotfix_days": 30,  # Code unchanged for 30+ days = hotfix if changed
    "new_code_days": 7,  # Code created within 7 days = new development
    "significant_lines": 50,  # 50+ lines changed = significant
    "max_breadth_depth": 3,  # Maximum depth for breadth-first scanning
    "cache_ttl_seconds": 600,  # 10 minutes default cache TTL
    "max_file_size_mb": 10,  # Skip files larger than 10MB
}
