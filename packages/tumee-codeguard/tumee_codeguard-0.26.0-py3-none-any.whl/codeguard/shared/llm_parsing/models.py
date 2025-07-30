"""
Core data models for the shared LLM parsing system.

These models define the interface between parsers and consuming projects,
allowing for flexible configuration while maintaining type safety.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ModelSize(Enum):
    """
    Model size abstraction for cost optimization.

    This allows consuming projects to request parsing power appropriate
    to their task complexity without needing to know specific model names.
    """

    SMALL = "small"  # Fast, cheap parsing tasks (Haiku, GPT-3.5, Gemini Flash)
    MEDIUM = "medium"  # Reasoning, smart planning (Sonnet, GPT-4, Gemini Pro)
    LARGE = "large"  # Complex analysis, high accuracy (Opus, GPT-4-turbo, Gemini Ultra)


@dataclass
class TaskConfig:
    """
    Configuration for a specific parsing task.

    This allows consuming projects to define their own parsing logic
    while leveraging the shared parser infrastructure.
    """

    # LLM-specific configuration
    prompt_template: Optional[str] = None  # Template with {input} placeholder
    output_schema: Optional[Dict[str, Any]] = None  # JSON schema for validation
    system_prompt: Optional[str] = None  # System-level instructions
    system_prompt_mode: str = "set"  # "set" (replace) or "append" (add to existing)
    response_format: Optional[str] = (
        None  # "json" or "text" - controls LLM output format. None="json"
    )

    # Regex-specific configuration
    regex_patterns: Optional[List[Dict[str, Any]]] = None  # Pattern definitions

    # Extractor configuration - business logic mappings
    category_mappings: Optional[Dict[str, str]] = None  # keyword -> category mappings
    priority_mappings: Optional[Dict[str, int]] = None  # keyword -> priority mappings
    custom_mappings: Optional[Dict[str, Dict[str, Any]]] = None  # Additional mappings

    # General configuration
    confidence_threshold: float = 0.7  # Minimum confidence to accept result
    fallback_enabled: bool = True  # Allow fallback to simpler parsers

    # Quality assurance
    validation_rules: Optional[List[str]] = None  # Custom validation functions
    post_processing: Optional[str] = None  # Post-processing function name


@dataclass
class ParsedResult:
    """
    Generic result structure for all parsers.

    This provides a standardized interface while allowing projects
    to define their own result data structures in the 'data' field.
    """

    success: bool  # Whether parsing succeeded
    data: Dict[str, Any]  # Project-specific parsed data
    confidence: float  # Parser confidence (0.0-1.0)
    parser_used: str  # Which parser generated this result
    model_used: Optional[str] = None  # Specific model name if LLM was used
    error_message: Optional[str] = None  # Error details if parsing failed
    raw_response: Optional[str] = None  # Raw parser response for debugging

    def is_valid(self) -> bool:
        """Check if this result meets basic validity requirements."""
        return (
            self.success
            and isinstance(self.data, dict)
            and 0.0 <= self.confidence <= 1.0
            and bool(self.parser_used)
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Convenience method to access parsed data."""
        return self.data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "data": self.data,
            "confidence": self.confidence,
            "parser_used": self.parser_used,
            "model_used": self.model_used,
            "error_message": self.error_message,
        }

    def __str__(self) -> str:
        if self.success:
            return f"ParsedResult(success=True, confidence={self.confidence:.2f}, parser={self.parser_used})"
        else:
            return f"ParsedResult(success=False, error='{self.error_message}', parser={self.parser_used})"


# For backward compatibility - projects can use ParsedRule as an alias
ParsedRule = ParsedResult
