"""
Parser factory for intelligent parser selection.

This factory automatically selects the best available parser based on:
- Provider availability (API keys, CLI tools)
- Cost considerations
- Model size requirements
- Task complexity
- User preferences
"""

import logging
import os
from typing import Dict, List, Optional, Tuple

from ..base import ParserBase
from ..models import ModelSize, TaskConfig
from .api_parser import APIParser
from .claude_cli_parser import ClaudeCliParser
from .regex_parser import RegexParser

logger = logging.getLogger(__name__)


class ParserFactory:
    """
    Factory for creating and selecting the best available parser.

    The factory uses intelligent selection logic to choose parsers based on:
    1. Availability (dependencies, API keys, etc.)
    2. Cost optimization (prefer cheaper options for simple tasks)
    3. Reliability (fallback chain)
    4. User preferences (environment configuration)
    """

    # Default priority order (can be overridden by environment)
    DEFAULT_PRIORITY = ["claude-cli", "api", "regex"]

    @classmethod
    def create_parser(
        cls,
        model_size: ModelSize = ModelSize.SMALL,
        task_config: Optional[TaskConfig] = None,
        preferred_provider: Optional[str] = None,
        priority_order: Optional[List[str]] = None,
    ) -> ParserBase:
        """
        Create the best available parser for the given requirements.

        Args:
            model_size: Required model size (affects cost and capability)
            task_config: Task-specific configuration
            preferred_provider: Force a specific provider (None for auto-select)
            priority_order: Custom priority order for parser selection

        Returns:
            Best available parser instance

        Raises:
            ValueError: If no parsers are available
        """
        # Get priority order from environment or use default
        if priority_order is None:
            env_priority = os.getenv("CODEGUARD_PARSER_PRIORITY")
            if env_priority:
                priority_order = [p.strip() for p in env_priority.split(",")]
            else:
                priority_order = cls.DEFAULT_PRIORITY.copy()

        # If specific provider requested, try it first
        if preferred_provider:
            parser = cls._create_specific_parser(preferred_provider, model_size, task_config)
            if parser and parser.is_available():
                logger.info(f"Using preferred parser: {preferred_provider}")
                return parser
            else:
                logger.warning(f"Preferred parser {preferred_provider} not available, falling back")

        # Try parsers in priority order
        for parser_type in priority_order:
            parser = cls._create_specific_parser(parser_type, model_size, task_config)
            if parser and parser.is_available():
                logger.info(f"Selected parser: {parser_type} ({parser.__class__.__name__})")
                return parser

        # If nothing else works, try regex as absolute fallback
        regex_parser = RegexParser(model_size, task_config)
        if regex_parser.is_available():
            logger.warning("All preferred parsers unavailable, using regex fallback")
            return regex_parser

        raise ValueError(
            "No parsers are available - this should never happen as regex is always available"
        )

    @classmethod
    def _create_specific_parser(
        cls, parser_type: str, model_size: ModelSize, task_config: Optional[TaskConfig]
    ) -> Optional[ParserBase]:
        """Create a specific parser type."""
        try:
            if parser_type.lower() in ["claude-cli", "claude_cli", "cli"]:
                return ClaudeCliParser(model_size, task_config)
            elif parser_type.lower() in ["api", "llm", "openai", "anthropic", "google"]:
                # For API, try to detect the best provider
                provider = None
                if parser_type.lower() in ["openai", "anthropic", "google"]:
                    provider = parser_type.lower()
                return APIParser(model_size, task_config, provider)
            elif parser_type.lower() in ["regex", "fallback"]:
                return RegexParser(model_size, task_config)
            else:
                logger.warning(f"Unknown parser type: {parser_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to create {parser_type} parser: {e}")
            return None

    @classmethod
    def get_available_parsers(
        cls, model_size: ModelSize = ModelSize.SMALL, task_config: Optional[TaskConfig] = None
    ) -> List[Tuple[str, ParserBase]]:
        """
        Get all available parsers with their capabilities.

        Args:
            model_size: Model size to test
            task_config: Task configuration to test

        Returns:
            List of (parser_name, parser_instance) tuples for available parsers
        """
        available = []

        # Test Claude CLI
        try:
            claude_cli = ClaudeCliParser(model_size, task_config)
            if claude_cli.is_available():
                available.append(("claude-cli", claude_cli))
        except Exception as e:
            logger.debug(f"Claude CLI not available: {e}")

        # Test API parsers (each provider)
        for provider in ["anthropic", "openai", "google"]:
            try:
                api_parser = APIParser(model_size, task_config, provider)
                if api_parser.is_available():
                    available.append((f"api-{provider}", api_parser))
            except Exception as e:
                logger.debug(f"API parser {provider} not available: {e}")

        # Regex is always available
        try:
            regex_parser = RegexParser(model_size, task_config)
            available.append(("regex", regex_parser))
        except Exception as e:
            logger.error(f"Regex parser failed (should never happen): {e}")

        return available

    @classmethod
    def get_capabilities_report(
        cls, model_size: ModelSize = ModelSize.SMALL, task_config: Optional[TaskConfig] = None
    ) -> Dict[str, Dict]:
        """
        Generate a comprehensive capabilities report for all parsers.

        Args:
            model_size: Model size to test
            task_config: Task configuration to test

        Returns:
            Dictionary mapping parser names to their capabilities
        """
        report = {}
        available_parsers = cls.get_available_parsers(model_size, task_config)

        for parser_name, parser in available_parsers:
            try:
                capabilities = parser.get_capabilities()
                capabilities["selection_priority"] = cls._get_selection_priority(parser_name)
                report[parser_name] = capabilities
            except Exception as e:
                logger.error(f"Failed to get capabilities for {parser_name}: {e}")
                report[parser_name] = {"error": str(e), "available": False}

        return report

    @classmethod
    def _get_selection_priority(cls, parser_name: str) -> int:
        """Get the selection priority for a parser (lower = higher priority)."""
        # Get priority order from environment or use default
        env_priority = os.getenv("CODEGUARD_PARSER_PRIORITY")
        if env_priority:
            priority_order = [p.strip() for p in env_priority.split(",")]
        else:
            priority_order = cls.DEFAULT_PRIORITY.copy()

        # Find base parser type
        base_type = parser_name.split("-")[0]  # "api-openai" -> "api"

        try:
            return priority_order.index(base_type)
        except ValueError:
            return 999  # Unknown parsers get lowest priority

    @classmethod
    def estimate_costs(
        cls,
        content: str,
        model_size: ModelSize = ModelSize.SMALL,
        task_config: Optional[TaskConfig] = None,
    ) -> Dict[str, float]:
        """
        Estimate parsing costs for all available parsers.

        Args:
            content: Content to be parsed
            model_size: Model size requirement
            task_config: Task configuration

        Returns:
            Dictionary mapping parser names to estimated costs in USD
        """
        costs = {}
        available_parsers = cls.get_available_parsers(model_size, task_config)

        for parser_name, parser in available_parsers:
            try:
                cost = parser.get_cost_estimate(content)
                costs[parser_name] = cost
            except Exception as e:
                logger.error(f"Failed to estimate cost for {parser_name}: {e}")
                costs[parser_name] = float("inf")  # Unknown cost

        return costs

    @classmethod
    def select_cheapest_available(
        cls,
        content: str,
        model_size: ModelSize = ModelSize.SMALL,
        task_config: Optional[TaskConfig] = None,
        max_cost: float = 0.01,  # Default max cost: 1 cent
    ) -> Optional[ParserBase]:
        """
        Select the cheapest available parser within cost constraints.

        Args:
            content: Content to be parsed
            model_size: Model size requirement
            task_config: Task configuration
            max_cost: Maximum acceptable cost in USD

        Returns:
            Cheapest parser within cost constraints, or None if all too expensive
        """
        available_parsers = cls.get_available_parsers(model_size, task_config)

        cheapest_parser = None
        cheapest_cost = float("inf")

        for parser_name, parser in available_parsers:
            try:
                cost = parser.get_cost_estimate(content)
                if cost <= max_cost and cost < cheapest_cost:
                    cheapest_cost = cost
                    cheapest_parser = parser
            except Exception as e:
                logger.error(f"Failed to evaluate {parser_name} for cost selection: {e}")

        if cheapest_parser:
            logger.info(
                f"Selected cheapest parser: {cheapest_parser.__class__.__name__} (${cheapest_cost:.4f})"
            )

        return cheapest_parser

    @classmethod
    def diagnose_availability(cls) -> Dict[str, Dict]:
        """
        Diagnose why parsers are or aren't available.

        Returns:
            Diagnostic information for troubleshooting parser availability
        """
        diagnostics = {}

        # Check Claude CLI
        claude_cli = ClaudeCliParser(ModelSize.SMALL)
        diagnostics["claude-cli"] = {
            "available": claude_cli.is_available(),
            "cli_path": claude_cli.claude_path,
            "requirements": ["Claude CLI installed", "Valid Claude account"],
            "env_vars": [],
        }

        # Check API providers
        for provider in ["openai", "anthropic", "google"]:
            api_parser = APIParser(ModelSize.SMALL, provider=provider)
            api_key_env = f"{provider.upper()}_API_KEY"
            base_url_env = f"{provider.upper()}_BASE_URL"

            diagnostics[f"api-{provider}"] = {
                "available": api_parser.is_available(),
                "api_key_set": bool(os.getenv(api_key_env)),
                "base_url": api_parser.base_url,
                "requirements": [f"{api_key_env} environment variable", "Internet connectivity"],
                "env_vars": [api_key_env, base_url_env],
            }

        # Regex is always available
        regex_parser = RegexParser(ModelSize.SMALL)
        diagnostics["regex"] = {
            "available": regex_parser.is_available(),
            "requirements": ["None - always available"],
            "env_vars": [],
        }

        return diagnostics
