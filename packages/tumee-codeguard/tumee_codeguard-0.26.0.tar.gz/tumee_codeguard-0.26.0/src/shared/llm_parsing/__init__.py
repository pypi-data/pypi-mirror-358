"""
Shared LLM parsing infrastructure for CodeGuard.

This system provides intelligent natural language parsing with multiple
fallback strategies, cost optimization, and provider flexibility.

The parsers are designed to be generic and reusable - specific parsing logic
(prompts, patterns, output schemas) should be provided by consuming projects.

Example usage:
    from src.shared.llm_parsing import create_parser, ModelSize, ParsedRule

    # Create parser with project-specific configuration
    parser = create_parser(
        model_size=ModelSize.SMALL,
        task_config={
            "prompt_template": "Parse this rule: {input}",
            "output_schema": {...},
            "regex_patterns": [...]
        }
    )

    result = await parser.parse("always use staging database")
"""

from .base import ParserBase
from .models import ModelSize, ParsedResult, ParsedRule, TaskConfig
from .parsers.factory import ParserFactory


def create_parser(
    model_size: ModelSize = ModelSize.SMALL, task_config: TaskConfig = None
) -> ParserBase:
    """Create the best available parser for the given model size and task."""
    return ParserFactory.create_parser(model_size, task_config)


__all__ = [
    "ModelSize",
    "ParsedResult",
    "ParsedRule",
    "TaskConfig",
    "ParserBase",
    "ParserFactory",
    "create_parser",
]
