"""
Content management system for boilerplate injection and filtering.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class ContentManager:
    """
    Manages content injection, filtering, and optimization.

    Responsibilities:
    - Boilerplate text injection and removal
    - Content filtering and sanitization
    - Context size optimization
    - Response content processing
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Content processing configuration
        self.enable_injection = config.get("content", {}).get("injection", {}).get("enabled", True)
        self.enable_filtering = config.get("content", {}).get("filtering", {}).get("enabled", True)

        # Boilerplate patterns
        self.boilerplate_patterns = self._load_boilerplate_patterns()

        # Content filters
        self.content_filters = config.get("content", {}).get("filters", [])

        # Response processing settings
        self.strip_metadata = (
            config.get("content", {}).get("response", {}).get("strip_metadata", False)
        )
        self.normalize_whitespace = (
            config.get("content", {}).get("response", {}).get("normalize_whitespace", True)
        )

    def _load_boilerplate_patterns(self) -> Dict[str, Dict[str, str]]:
        """
        Load boilerplate patterns for injection and removal.

        Returns:
            Dictionary of boilerplate patterns
        """
        return {
            "codeguard_header": {
                "inject": """
🔒 CodeGuard Session Active

This conversation is being monitored by CodeGuard LLM Proxy for:
- Tool call interception and logging
- Content filtering and optimization
- Security monitoring and compliance

All actions are logged for audit purposes.
---
                """.strip(),
                "remove_patterns": [
                    r"🔒 CodeGuard Session Active.*?---",
                    r"This conversation is being monitored.*?audit purposes\.",
                ],
            },
            "debug_footer": {
                "inject": """
---
🔧 Debug Info: Request processed by CodeGuard LLM Proxy
                """.strip(),
                "remove_patterns": [
                    r"---\s*🔧 Debug Info:.*?CodeGuard LLM Proxy",
                ],
            },
            "safety_disclaimer": {
                "inject": """
⚠️ Safety Notice: This response has been processed through CodeGuard filters.
                """.strip(),
                "remove_patterns": [
                    r"⚠️ Safety Notice:.*?CodeGuard filters\.",
                ],
            },
        }

    async def inject_boilerplate(
        self, content: str, injection_type: str = "codeguard_header"
    ) -> str:
        """
        Inject boilerplate content into text.

        Args:
            content: Original content
            injection_type: Type of boilerplate to inject

        Returns:
            Content with boilerplate injected
        """
        if not self.enable_injection:
            return content

        try:
            pattern_config = self.boilerplate_patterns.get(injection_type, {})
            inject_text = pattern_config.get("inject", "")

            if not inject_text:
                return content

            # Inject at appropriate position based on type
            if injection_type.endswith("_header"):
                return f"{inject_text}\n\n{content}"
            elif injection_type.endswith("_footer"):
                return f"{content}\n\n{inject_text}"
            else:
                # Default to header injection
                return f"{inject_text}\n\n{content}"

        except Exception as e:
            self.logger.error(f"Boilerplate injection error: {e}", exc_info=True)
            return content

    async def remove_boilerplate(self, content: str, removal_type: Optional[str] = None) -> str:
        """
        Remove boilerplate content from text.

        Args:
            content: Content with boilerplate
            removal_type: Specific boilerplate type to remove (None for all)

        Returns:
            Content with boilerplate removed
        """
        if not self.enable_filtering:
            return content

        try:
            modified_content = content

            # Determine which patterns to remove
            patterns_to_check = []
            if removal_type:
                pattern_config = self.boilerplate_patterns.get(removal_type, {})
                patterns_to_check.extend(pattern_config.get("remove_patterns", []))
            else:
                # Remove all known boilerplate patterns
                for pattern_config in self.boilerplate_patterns.values():
                    patterns_to_check.extend(pattern_config.get("remove_patterns", []))

            # Apply removal patterns
            for pattern in patterns_to_check:
                modified_content = re.sub(
                    pattern, "", modified_content, flags=re.DOTALL | re.MULTILINE
                )

            # Clean up extra whitespace
            if self.normalize_whitespace:
                modified_content = self._normalize_whitespace(modified_content)

            return modified_content

        except Exception as e:
            self.logger.error(f"Boilerplate removal error: {e}", exc_info=True)
            return content

    async def filter_response_content(self, content: str) -> str:
        """
        Apply content filters to response content.

        Args:
            content: Original response content

        Returns:
            Filtered response content
        """
        if not self.enable_filtering:
            return content

        try:
            filtered_content = content

            # Apply configured content filters
            for filter_config in self.content_filters:
                if filter_config.get("enabled", True):
                    filtered_content = await self._apply_content_filter(
                        filtered_content, filter_config
                    )

            # Apply built-in safety filters
            filtered_content = await self._apply_safety_filters(filtered_content)

            return filtered_content

        except Exception as e:
            self.logger.error(f"Response content filtering error: {e}", exc_info=True)
            return content

    async def _apply_content_filter(self, content: str, filter_config: Dict[str, Any]) -> str:
        """
        Apply a single content filter.

        Args:
            content: Content to filter
            filter_config: Filter configuration

        Returns:
            Filtered content
        """
        filter_type = filter_config.get("type", "pattern")

        if filter_type == "pattern":
            pattern = filter_config.get("pattern", "")
            action = filter_config.get("action", "remove")
            replacement = filter_config.get("replacement", "")

            if action == "remove":
                content = re.sub(pattern, "", content, flags=re.DOTALL | re.MULTILINE)
            elif action == "replace":
                content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.MULTILINE)
            elif action == "redact":
                content = re.sub(pattern, "[REDACTED]", content, flags=re.DOTALL | re.MULTILINE)

        elif filter_type == "length_limit":
            max_length = filter_config.get("max_length", 10000)
            if len(content) > max_length:
                content = content[: max_length - 20] + "\n\n[Content truncated]"

        elif filter_type == "word_filter":
            blocked_words = filter_config.get("blocked_words", [])
            for word in blocked_words:
                content = re.sub(re.escape(word), "[FILTERED]", content, flags=re.IGNORECASE)

        return content

    async def _apply_safety_filters(self, content: str) -> str:
        """
        Apply built-in safety filters to content.

        Args:
            content: Content to filter

        Returns:
            Safety-filtered content
        """
        # Filter sensitive information patterns
        sensitive_patterns = [
            # API keys and tokens
            (r'(api[_-]?key|token|secret)["\s]*[:=]["\s]*([a-zA-Z0-9_-]{20,})', r"\1: [REDACTED]"),
            # Email addresses (partial redaction)
            (r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", r"\1@[REDACTED]"),
            # IP addresses (partial redaction)
            (r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}", r"\1[REDACTED]"),
            # Credit card numbers
            (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CARD-REDACTED]"),
            # Social security numbers
            (r"\b\d{3}-?\d{2}-?\d{4}\b", "[SSN-REDACTED]"),
        ]

        filtered_content = content
        for pattern, replacement in sensitive_patterns:
            filtered_content = re.sub(pattern, replacement, filtered_content, flags=re.IGNORECASE)

        return filtered_content

    async def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process complete response data through content management.

        Args:
            response_data: Response data from upstream API

        Returns:
            Processed response data
        """
        try:
            processed_data = response_data.copy()

            # Process content in response
            if "content" in processed_data:
                content_blocks = processed_data["content"]
                if isinstance(content_blocks, list):
                    for i, block in enumerate(content_blocks):
                        if isinstance(block, dict) and "text" in block:
                            original_text = block["text"]
                            filtered_text = await self.filter_response_content(original_text)
                            processed_data["content"][i]["text"] = filtered_text

                elif isinstance(content_blocks, str):
                    processed_data["content"] = await self.filter_response_content(content_blocks)

            # Strip metadata if configured
            if self.strip_metadata:
                processed_data = await self._strip_response_metadata(processed_data)

            return processed_data

        except Exception as e:
            self.logger.error(f"Response processing error: {e}", exc_info=True)
            return response_data

    async def _strip_response_metadata(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strip metadata from response data.

        Args:
            response_data: Response data with metadata

        Returns:
            Response data without metadata
        """
        # Remove proxy-specific metadata
        metadata_keys = ["usage", "model", "stop_reason", "stop_sequence"]

        stripped_data = response_data.copy()
        for key in metadata_keys:
            if key in stripped_data and self._should_strip_metadata_key(key):
                del stripped_data[key]

        return stripped_data

    def _should_strip_metadata_key(self, key: str) -> bool:
        """
        Determine if a metadata key should be stripped.

        Args:
            key: Metadata key name

        Returns:
            True if key should be stripped
        """
        # Keep essential metadata, strip optional metadata
        essential_keys = ["content", "role", "type"]
        return key not in essential_keys

    def _normalize_whitespace(self, content: str) -> str:
        """
        Normalize whitespace in content.

        Args:
            content: Content with irregular whitespace

        Returns:
            Content with normalized whitespace
        """
        # Remove excessive newlines
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Remove trailing whitespace from lines
        content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

        # Remove leading/trailing whitespace from entire content
        content = content.strip()

        return content

    async def optimize_context_for_model(self, content: str, model: str) -> str:
        """
        Optimize content for specific model constraints.

        Args:
            content: Content to optimize
            model: Target model name

        Returns:
            Optimized content
        """
        try:
            # Model-specific optimizations
            if "claude" in model.lower():
                return await self._optimize_for_claude(content)
            elif "gpt" in model.lower():
                return await self._optimize_for_gpt(content)
            else:
                return content

        except Exception as e:
            self.logger.error(f"Model optimization error: {e}", exc_info=True)
            return content

    async def _optimize_for_claude(self, content: str) -> str:
        """
        Optimize content for Claude models.

        Args:
            content: Content to optimize

        Returns:
            Claude-optimized content
        """
        # Claude handles long context well, minimal optimization needed
        return content

    async def _optimize_for_gpt(self, content: str) -> str:
        """
        Optimize content for GPT models.

        Args:
            content: Content to optimize

        Returns:
            GPT-optimized content
        """
        # GPT models benefit from more aggressive context optimization
        # Truncate very long sections
        max_section_length = 5000

        if len(content) > max_section_length:
            content = (
                content[: max_section_length - 50] + "\n\n[Content truncated for optimization]"
            )

        return content

    def get_content_statistics(self) -> Dict[str, Any]:
        """
        Get content processing statistics.

        Returns:
            Dictionary with content processing statistics
        """
        return {
            "injection_enabled": self.enable_injection,
            "filtering_enabled": self.enable_filtering,
            "boilerplate_patterns": len(self.boilerplate_patterns),
            "content_filters": len(self.content_filters),
            "configuration": {
                "strip_metadata": self.strip_metadata,
                "normalize_whitespace": self.normalize_whitespace,
            },
        }
