"""
Regex-based parser implementation.

This parser provides fast, deterministic parsing using configurable
regular expression patterns. It serves as the reliable fallback option
when LLM-based parsers are unavailable or fail.
"""

import logging
import re
from typing import Any, Callable, Dict, List, Optional

from ..base import ParserBase
from ..models import ModelSize, ParsedResult, TaskConfig

# File-global logger accessible to static methods
logger = logging.getLogger(__name__)


class RegexParser(ParserBase):
    """
    Regex-based parser that uses configurable patterns to extract structured data.

    This parser is always available and serves as the fallback option.
    Consuming projects configure it by providing regex patterns and extraction logic.

    Example task_config.regex_patterns:
    [
        {
            "name": "duration_hours",
            "pattern": r"(\\d+)\\s*h(?:ours?)?",
            "extractor": "extract_hours",
            "flags": "re.IGNORECASE"
        },
        {
            "name": "priority_keywords",
            "pattern": r"\b(critical|urgent|important|low)\b",
            "extractor": "extract_priority",
            "flags": "re.IGNORECASE"
        }
    ]
    """

    def __init__(self, model_size: ModelSize, task_config: Optional[TaskConfig] = None):
        super().__init__(model_size, task_config)
        self._compiled_patterns = {}
        self._prepare_patterns()

    def _prepare_patterns(self):
        """Compile regex patterns for better performance."""
        if not self.task_config.regex_patterns:
            return

        for pattern_config in self.task_config.regex_patterns:
            name = pattern_config.get("name")
            pattern = pattern_config.get("pattern")
            flags_str = pattern_config.get("flags", "")

            if not name or not pattern:
                logger.warning(f"Skipping invalid regex pattern config: {pattern_config}")
                continue

            # Parse flags
            flags = 0
            if "re.IGNORECASE" in flags_str or "re.I" in flags_str:
                flags |= re.IGNORECASE
            if "re.MULTILINE" in flags_str or "re.M" in flags_str:
                flags |= re.MULTILINE
            if "re.DOTALL" in flags_str or "re.S" in flags_str:
                flags |= re.DOTALL

            try:
                compiled_pattern = re.compile(pattern, flags)
                self._compiled_patterns[name] = {
                    "pattern": compiled_pattern,
                    "extractor": pattern_config.get("extractor"),
                    "config": pattern_config,
                }
            except re.error as e:
                logger.error(f"Failed to compile regex pattern '{pattern}': {e}")

    async def parse_impl(self, content: str, **kwargs) -> ParsedResult:
        """
        Parse content using configured regex patterns.

        Args:
            content: Text content to parse
            **kwargs: Additional parameters (extractors, context, etc.)

        Returns:
            ParsedResult with extracted data
        """
        if not self.task_config.regex_patterns:
            return ParsedResult(
                success=False,
                data={},
                confidence=0.0,
                parser_used=self.parser_name,
                error_message="No regex patterns configured",
            )

        extracted_data = {}
        total_matches = 0

        # Get custom extractors and mappings from kwargs
        extractors = kwargs.get("extractors", {})
        category_mappings = kwargs.get("category_mappings", self.task_config.category_mappings)
        priority_mappings = kwargs.get("priority_mappings", self.task_config.priority_mappings)
        custom_mappings = kwargs.get("custom_mappings", self.task_config.custom_mappings or {})

        for name, pattern_info in self._compiled_patterns.items():
            pattern = pattern_info["pattern"]
            extractor_name = pattern_info["extractor"]

            # Find all matches
            matches = pattern.findall(content)
            if matches:
                total_matches += len(matches)

                # Apply extractor if provided
                if extractor_name and extractor_name in extractors:
                    try:
                        extractor_func = extractors[extractor_name]

                        # Pass appropriate mappings to extractors that support them
                        if extractor_name == "extract_category_from_keywords":
                            extracted_value = extractor_func(matches, content, category_mappings)
                        elif extractor_name == "extract_priority_from_keywords":
                            extracted_value = extractor_func(matches, content, priority_mappings)
                        else:
                            # For other extractors, pass custom mappings if available
                            if extractor_name in custom_mappings:
                                extracted_value = extractor_func(
                                    matches, content, custom_mappings[extractor_name]
                                )
                            else:
                                extracted_value = extractor_func(matches, content)

                        extracted_data[name] = extracted_value
                    except Exception as e:
                        logger.warning(f"Extractor {extractor_name} failed: {e}")
                        extracted_data[name] = matches
                else:
                    # Use raw matches if no extractor
                    extracted_data[name] = matches[0] if len(matches) == 1 else matches

        # Calculate confidence based on how many patterns matched
        total_patterns = len(self._compiled_patterns)
        patterns_matched = len([k for k, v in extracted_data.items() if v])
        confidence = patterns_matched / total_patterns if total_patterns > 0 else 0.0

        # Boost confidence if we have multiple matches
        if total_matches > patterns_matched:
            confidence = min(1.0, confidence + (total_matches - patterns_matched) * 0.1)

        return ParsedResult(
            success=bool(extracted_data),
            data=extracted_data,
            confidence=confidence,
            parser_used=self.parser_name,
            raw_response=f"Matched {patterns_matched}/{total_patterns} patterns with {total_matches} total matches",
        )

    def is_available(self) -> bool:
        """Regex parser is always available."""
        return True

    def get_cost_estimate(self, content: str) -> float:
        """Regex parsing is free."""
        return 0.0

    def get_capabilities(self) -> dict:
        """Return regex parser capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "supports_structured_output": True,
                "max_content_length": None,  # No limit for regex
                "patterns_configured": len(self._compiled_patterns),
                "deterministic": True,
                "offline_capable": True,
            }
        )
        return capabilities


# Common extractor functions that consuming projects can use
class CommonExtractors:
    """
    Collection of common extraction functions for regex parsing.

    Consuming projects can use these or provide their own custom extractors.
    """

    @staticmethod
    def extract_hours(matches: List[str], content: str) -> Optional[int]:
        """Extract hours from duration patterns."""
        try:
            return int(matches[0]) if matches else None
        except (ValueError, IndexError):
            return None

    @staticmethod
    def extract_priority_from_keywords(
        matches: List[str], content: str, priority_mappings: Optional[Dict[str, int]] = None
    ) -> int:
        """Extract priority level from keyword matches."""
        if not matches:
            return 2  # Default medium priority

        keyword = matches[0].lower()

        # Use provided mappings - no default mappings here
        if not priority_mappings:
            return 2  # Default medium priority if no mappings provided

        priority_map = priority_mappings
        return priority_map.get(keyword, 2)

    @staticmethod
    def extract_category_from_keywords(
        matches: List[str], content: str, category_mappings: Optional[Dict[str, str]] = None
    ) -> str:
        """Extract category from keyword matches."""
        if not matches:
            return "general"

        keyword = matches[0].lower()

        # Use provided mappings from consuming project
        # No default mappings - business logic should come from configuration
        if not category_mappings:
            logger.warning(
                "No category_mappings provided to extract_category_from_keywords - using default 'general'"
            )
            return "general"

        return category_mappings.get(keyword, "general")

    @staticmethod
    def extract_boolean_flag(matches: List[str], content: str) -> bool:
        """Extract boolean value from yes/no, true/false patterns."""
        if not matches:
            return False

        value = matches[0].lower()
        return value in {"yes", "true", "1", "on", "enable", "enabled"}

    @staticmethod
    def extract_clean_content(matches: List[str], content: str) -> str:
        """Remove matched patterns from content to get clean text."""
        clean_content = content
        for match in matches:
            clean_content = clean_content.replace(match, "").strip()

        # Clean up multiple spaces
        clean_content = re.sub(r"\s+", " ", clean_content).strip()
        return clean_content
