"""
Abstract base class for all parsers in the shared parsing system.

This defines the common interface that all parser implementations must follow,
allowing consuming projects to use any parser interchangeably.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from .models import ModelSize, ParsedResult, TaskConfig

logger = logging.getLogger(__name__)


class ParserBase(ABC):
    """
    Abstract base class for all parser implementations.

    This class defines the common interface and shared functionality
    that all parsers must implement. Specific parsers (Regex, API, CLI)
    inherit from this and implement the parse_impl method.
    """

    def __init__(self, model_size: ModelSize, task_config: Optional[TaskConfig] = None):
        """
        Initialize the parser with model size and task configuration.

        Args:
            model_size: The model size to use for this parser
            task_config: Project-specific configuration for parsing logic
        """
        self.model_size = model_size
        self.task_config = task_config or TaskConfig()
        self.parser_name = self.__class__.__name__.replace("Parser", "").lower()

    async def parse(self, content: str, **kwargs) -> ParsedResult:
        """
        Main parsing method that handles validation and error handling.

        This method provides common functionality around the actual parsing:
        - Input validation
        - Error handling and logging
        - Confidence threshold checking
        - Fallback coordination

        Args:
            content: The text content to parse
            **kwargs: Additional parsing parameters

        Returns:
            ParsedResult with success status and parsed data
        """
        if not content or not content.strip():
            return ParsedResult(
                success=False,
                data={},
                confidence=0.0,
                parser_used=self.parser_name,
                error_message="Empty or whitespace-only content provided",
            )

        try:
            # Validate system prompt configuration
            self._validate_system_prompt_config()
            # Call the specific parser implementation
            result = await self.parse_impl(content.strip(), **kwargs)

            # Validate confidence threshold
            if result.confidence < self.task_config.confidence_threshold:
                if self.task_config.fallback_enabled:
                    logger.warning(
                        f"{self.parser_name} confidence {result.confidence:.2f} below threshold "
                        f"{self.task_config.confidence_threshold:.2f}, may need fallback"
                    )
                else:
                    return ParsedResult(
                        success=False,
                        data={},
                        confidence=result.confidence,
                        parser_used=self.parser_name,
                        error_message=f"Confidence {result.confidence:.2f} below threshold {self.task_config.confidence_threshold:.2f}",
                    )

            # Validate result structure
            if not result.is_valid():
                # Provide more detailed error information for debugging
                error_details = []
                if not result.success:
                    error_details.append("success=False")
                if not isinstance(result.data, dict):
                    error_details.append(f"data is {type(result.data).__name__}, not dict")
                if not (0.0 <= result.confidence <= 1.0):
                    error_details.append(f"confidence={result.confidence} not in [0.0, 1.0]")
                if not bool(result.parser_used):
                    error_details.append("parser_used is empty")

                error_message = (
                    f"Parser returned invalid result structure: {', '.join(error_details)}"
                )
                logger.debug(
                    f"Invalid result details: success={result.success}, data_type={type(result.data)}, confidence={result.confidence}, parser_used='{result.parser_used}'"
                )

                return ParsedResult(
                    success=False,
                    data={},
                    confidence=0.0,
                    parser_used=self.parser_name,
                    error_message=error_message,
                )

            logger.debug(
                f"{self.parser_name} successfully parsed content with confidence {result.confidence:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"{self.parser_name} parsing failed: {str(e)}")
            return ParsedResult(
                success=False,
                data={},
                confidence=0.0,
                parser_used=self.parser_name,
                error_message=str(e),
            )

    @abstractmethod
    async def parse_impl(self, content: str, **kwargs) -> ParsedResult:
        """
        Actual parsing implementation that subclasses must provide.

        This method contains the specific parsing logic for each parser type:
        - RegexParser: Pattern matching and extraction
        - APIParser: LLM API calls and response processing
        - ClaudeCliParser: CLI command execution and result parsing

        Args:
            content: The cleaned, non-empty content to parse
            **kwargs: Additional parsing parameters

        Returns:
            ParsedResult with the parsing results

        Raises:
            Exception: Any parsing errors should be raised and will be
                      caught by the base parse() method
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this parser is available for use.

        This allows parsers to check for their dependencies:
        - RegexParser: Always available
        - APIParser: Check for API keys and network connectivity
        - ClaudeCliParser: Check for CLI installation

        Returns:
            True if the parser can be used, False otherwise
        """
        pass

    def get_cost_estimate(self, content: str) -> float:
        """
        Estimate the cost of parsing this content with this parser.

        This allows the factory to make cost-aware decisions about
        which parser to use. Base implementation returns 0.0 (free).

        Args:
            content: The content to be parsed

        Returns:
            Estimated cost in USD, or 0.0 for free parsers
        """
        return 0.0

    def supports_system_prompts(self) -> bool:
        """
        Check if this parser supports system prompt configuration.

        Returns:
            True if the parser can handle system prompts, False otherwise
        """
        return False  # Override in subclasses that support system prompts

    def _validate_system_prompt_config(self) -> None:
        """
        Validate system prompt configuration for parsers that support it.

        Raises:
            NotImplementedError: If system prompt is configured but not supported
            ValueError: If system prompt mode is invalid
        """
        if not self.task_config.system_prompt:
            return  # No system prompt configured, nothing to validate

        if not self.supports_system_prompts():
            raise NotImplementedError(
                f"{self.parser_name} parser does not support system prompts yet"
            )

        valid_modes = ["set", "append"]
        if self.task_config.system_prompt_mode not in valid_modes:
            raise ValueError(
                f"Invalid system_prompt_mode '{self.task_config.system_prompt_mode}'. "
                f"Must be one of: {valid_modes}"
            )

    def get_capabilities(self) -> dict:
        """
        Return information about this parser's capabilities.

        This helps the factory make informed decisions about parser selection.

        Returns:
            Dictionary with capability information
        """
        return {
            "name": self.parser_name,
            "model_size": self.model_size.value,
            "available": self.is_available(),
            "cost_per_request": self.get_cost_estimate("sample text"),
            "supports_structured_output": False,  # Override in subclasses
            "supports_confidence_scoring": True,
            "supports_system_prompts": self.supports_system_prompts(),
            "max_content_length": None,  # Override in subclasses if applicable
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(model_size={self.model_size.value})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model_size={self.model_size!r}, available={self.is_available()})"
