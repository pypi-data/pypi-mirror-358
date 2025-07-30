"""
CodeGuard-specific parsing configurations for LLM parsing system.

This module provides shared parsing configurations that are used by multiple
MCP tools (urgent_notes, smart_planning) to maintain consistency across
the CodeGuard toolset.
"""

from typing import Any, Dict

from .....shared.llm_parsing.models import TaskConfig
from .....shared.llm_parsing.parsers.regex_parser import CommonExtractors


class CodeGuardParsingConfig:
    """
    Centralized parsing configuration for CodeGuard MCP tools.

    This ensures consistent category mappings, priority mappings, and
    extractor configurations across urgent_notes and smart_planning.
    """

    # Category mappings for CodeGuard context
    CATEGORY_MAPPINGS = {
        "database": "setup",
        "db": "setup",
        "environment": "setup",
        "env": "setup",
        "config": "setup",
        "commit": "security",
        "push": "security",
        "api": "security",
        "secret": "security",
        "key": "security",
        "test": "process",
        "build": "process",
        "deploy": "process",
    }

    # Priority mappings for CodeGuard context
    PRIORITY_MAPPINGS = {
        "critical": 5,
        "urgent": 4,
        "important": 3,
        "medium": 2,
        "low": 1,
    }

    # Common regex patterns for CodeGuard tools
    URGENT_NOTE_PATTERNS = [
        {
            "name": "priority_keywords",
            "pattern": r"\b(critical|urgent|important|medium|low)\b",
            "extractor": "extract_priority_from_keywords",
            "flags": "re.IGNORECASE",
        },
        {
            "name": "category_keywords",
            "pattern": r"\b(database|db|environment|env|config|commit|push|api|secret|key|test|build|deploy)\b",
            "extractor": "extract_category_from_keywords",
            "flags": "re.IGNORECASE",
        },
        {
            "name": "duration_hours",
            "pattern": r"(\d+)\s*h(?:ours?)?",
            "extractor": "extract_hours",
            "flags": "re.IGNORECASE",
        },
    ]

    # Smart planning specific patterns
    SMART_PLANNING_PATTERNS = [
        {
            "name": "task_complexity",
            "pattern": r"\b(simple|medium|complex|very complex)\b",
            "extractor": "extract_complexity_level",
            "flags": "re.IGNORECASE",
        },
        {
            "name": "dependency_keywords",
            "pattern": r"\b(depends on|requires|needs|after|before)\b",
            "extractor": "extract_dependencies",
            "flags": "re.IGNORECASE",
        },
    ] + URGENT_NOTE_PATTERNS  # Include urgent note patterns too

    @classmethod
    def get_urgent_notes_task_config(cls) -> TaskConfig:
        """Get TaskConfig for urgent notes parsing."""
        return TaskConfig(
            regex_patterns=cls.URGENT_NOTE_PATTERNS,
            category_mappings=cls.CATEGORY_MAPPINGS,
            priority_mappings=cls.PRIORITY_MAPPINGS,
            confidence_threshold=0.6,
            fallback_enabled=True,
        )

    @classmethod
    def get_smart_planning_task_config(cls) -> TaskConfig:
        """Get TaskConfig for smart planning parsing."""
        return TaskConfig(
            regex_patterns=cls.SMART_PLANNING_PATTERNS,
            category_mappings=cls.CATEGORY_MAPPINGS,
            priority_mappings=cls.PRIORITY_MAPPINGS,
            custom_mappings={
                "complexity_levels": {"simple": 1, "medium": 2, "complex": 3, "very complex": 4}
            },
            confidence_threshold=0.7,
            fallback_enabled=True,
        )

    @classmethod
    def get_extractors(cls) -> Dict[str, Any]:
        """Get all extractors needed for CodeGuard parsing."""
        return {
            "extract_priority_from_keywords": CommonExtractors.extract_priority_from_keywords,
            "extract_category_from_keywords": CommonExtractors.extract_category_from_keywords,
            "extract_hours": CommonExtractors.extract_hours,
            "extract_complexity_level": cls._extract_complexity_level,
            "extract_dependencies": cls._extract_dependencies,
        }

    @staticmethod
    def _extract_complexity_level(matches, content, complexity_mappings=None):
        """Extract complexity level from matches."""
        if not matches:
            return 2  # Default medium

        complexity = matches[0].lower()
        mappings = complexity_mappings or {
            "simple": 1,
            "medium": 2,
            "complex": 3,
            "very complex": 4,
        }
        return mappings.get(complexity, 2)

    @staticmethod
    def _extract_dependencies(matches, content, dependency_mappings=None):
        """Extract dependency indicators from matches."""
        if not matches:
            return []

        # Simple dependency detection - could be enhanced
        return [match.lower() for match in matches]
