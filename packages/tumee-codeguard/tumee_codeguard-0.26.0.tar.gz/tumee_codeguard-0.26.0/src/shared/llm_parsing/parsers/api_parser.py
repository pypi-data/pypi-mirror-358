"""
API-based LLM parser implementation.

This parser provides intelligent parsing by calling LLM APIs (OpenAI, Anthropic, Google).
It uses configurable prompts and supports structured output via JSON schemas.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

import aiohttp

from ..base import ParserBase
from ..models import ModelSize, ParsedResult, TaskConfig

logger = logging.getLogger(__name__)


class APIParser(ParserBase):
    """
    LLM API-based parser with support for multiple providers.

    This parser calls external LLM APIs to perform intelligent parsing.
    Consuming projects configure it by providing prompts and output schemas.

    Supported providers:
    - OpenAI (GPT models)
    - Anthropic (Claude models)
    - Google (Gemini models)
    - Custom (any OpenAI-compatible API)

    Configuration is loaded from environment variables and config files.
    """

    # Default model mappings (can be overridden in config)
    DEFAULT_MODELS = {
        "openai": {
            ModelSize.SMALL: "gpt-3.5-turbo",
            ModelSize.MEDIUM: "gpt-4",
            ModelSize.LARGE: "gpt-4-turbo",
        },
        "anthropic": {
            ModelSize.SMALL: "claude-3-haiku-20240307",
            ModelSize.MEDIUM: "claude-3-sonnet-20240229",
            ModelSize.LARGE: "claude-3-opus-20240229",
        },
        "google": {
            ModelSize.SMALL: "gemini-1.5-flash",
            ModelSize.MEDIUM: "gemini-1.5-pro",
            ModelSize.LARGE: "gemini-1.5-pro",
        },
    }

    # Default base URLs
    DEFAULT_BASE_URLS = {
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com",
        "google": "https://generativelanguage.googleapis.com/v1",
    }

    def __init__(
        self,
        model_size: ModelSize,
        task_config: Optional[TaskConfig] = None,
        provider: Optional[str] = None,
    ):
        super().__init__(model_size, task_config)
        self.provider = provider or self._detect_best_provider()
        self.session: Optional[aiohttp.ClientSession] = None

        # Load provider configuration
        self._load_provider_config()

    def _detect_best_provider(self) -> str:
        """Detect the best available provider based on API keys."""
        # Check for API keys in order of preference
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("GOOGLE_API_KEY"):
            return "google"
        else:
            return "openai"  # Default, will fail gracefully if no key

    def _load_provider_config(self):
        """Load provider-specific configuration."""
        # Get base URL (environment override or default)
        base_url_env = f"{self.provider.upper()}_BASE_URL"
        self.base_url = os.getenv(base_url_env, self.DEFAULT_BASE_URLS.get(self.provider))

        # Get API key
        api_key_env = f"{self.provider.upper()}_API_KEY"
        self.api_key = os.getenv(api_key_env)

        # Get model name for this size
        self.model = self.DEFAULT_MODELS.get(self.provider, {}).get(
            self.model_size, "gpt-3.5-turbo"
        )

        # Set provider-specific headers
        self.headers = {"User-Agent": "CodeGuard-Parser/1.0"}
        if self.provider == "openai":
            self.headers["Authorization"] = f"Bearer {self.api_key}"
            self.headers["Content-Type"] = "application/json"
        elif self.provider == "anthropic":
            self.headers["x-api-key"] = self.api_key
            self.headers["Content-Type"] = "application/json"
            self.headers["anthropic-version"] = "2023-06-01"
        elif self.provider == "google":
            # Google uses API key in URL params
            self.headers["Content-Type"] = "application/json"

    async def parse_impl(self, content: str, **kwargs) -> ParsedResult:
        """
        Parse content using LLM API.

        Args:
            content: Text content to parse
            **kwargs: Additional parameters (custom prompt, schema, etc.)

        Returns:
            ParsedResult with LLM-parsed data
        """
        if not self.api_key and self.provider != "google":
            return ParsedResult(
                success=False,
                data={},
                confidence=0.0,
                parser_used=self.parser_name,
                model_used=self.model,
                error_message=f"No API key configured for {self.provider}",
            )

        # Build prompt from template
        prompt = self._build_prompt(content, **kwargs)

        try:
            # Make API call
            response_data = await self._call_api(prompt)

            # Parse response
            parsed_data = self._parse_response(response_data)

            # Calculate confidence (from LLM or estimate)
            confidence = parsed_data.get("confidence", 0.8)  # Default confidence

            # Remove confidence from data if it exists
            if "confidence" in parsed_data:
                del parsed_data["confidence"]

            return ParsedResult(
                success=True,
                data=parsed_data,
                confidence=confidence,
                parser_used=self.parser_name,
                model_used=self.model,
                raw_response=(
                    json.dumps(response_data)
                    if isinstance(response_data, dict)
                    else str(response_data)
                ),
            )

        except Exception as e:
            logger.error(f"API parsing failed for {self.provider}: {e}")
            return ParsedResult(
                success=False,
                data={},
                confidence=0.0,
                parser_used=self.parser_name,
                model_used=self.model,
                error_message=str(e),
            )

    def _build_prompt(self, content: str, **kwargs) -> str:
        """Build the prompt for the LLM."""
        # Use custom prompt if provided, otherwise use task config
        custom_prompt = kwargs.get("custom_prompt")
        if custom_prompt:
            return custom_prompt.format(input=content)

        if not self.task_config.prompt_template:
            # Default prompt for generic parsing
            return f"""Parse this text and extract structured information: "{content}"

Return a JSON object with the extracted data. Include a "confidence" field (0.0-1.0) indicating how confident you are in the parsing."""

        # Use configured prompt template
        prompt = self.task_config.prompt_template.format(input=content)

        # Add system prompt if configured
        if self.task_config.system_prompt:
            prompt = f"{self.task_config.system_prompt}\n\n{prompt}"

        # Add schema instruction if configured
        if self.task_config.output_schema:
            schema_str = json.dumps(self.task_config.output_schema, indent=2)
            prompt += f"\n\nReturn JSON matching this schema:\n{schema_str}"

        return prompt

    async def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Make the actual API call to the LLM provider."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)

        if self.provider == "openai":
            return await self._call_openai_api(prompt)
        elif self.provider == "anthropic":
            return await self._call_anthropic_api(prompt)
        elif self.provider == "google":
            return await self._call_google_api(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API."""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Low temperature for consistent parsing
            "max_tokens": 1000,
        }

        async with self.session.post(url, headers=self.headers, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"OpenAI API error {response.status}: {error_text}")

            data = await response.json()
            return data

    async def _call_anthropic_api(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic API."""
        url = f"{self.base_url}/v1/messages"
        payload = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with self.session.post(url, headers=self.headers, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Anthropic API error {response.status}: {error_text}")

            data = await response.json()
            return data

    async def _call_google_api(self, prompt: str) -> Dict[str, Any]:
        """Call Google API."""
        # Google API uses API key in URL
        url = f"{self.base_url}/models/{self.model}:generateContent"
        if self.api_key:
            url += f"?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1000},
        }

        async with self.session.post(url, headers=self.headers, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Google API error {response.status}: {error_text}")

            data = await response.json()
            return data

    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the LLM response to extract structured data."""
        # Extract content based on provider
        if self.provider == "openai":
            content = response_data["choices"][0]["message"]["content"]
        elif self.provider == "anthropic":
            content = response_data["content"][0]["text"]
        elif self.provider == "google":
            content = response_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        # Try to parse as JSON
        try:
            parsed_data = json.loads(content.strip())
            if isinstance(parsed_data, dict):
                return parsed_data
            else:
                return {"parsed_content": parsed_data}
        except json.JSONDecodeError:
            # If not valid JSON, return as text
            return {"parsed_content": content.strip()}

    def is_available(self) -> bool:
        """Check if API parser is available."""
        return (
            bool(self.api_key) or self.provider == "google"
        )  # Google can work without key in some cases

    def get_cost_estimate(self, content: str) -> float:
        """Estimate API call cost (rough approximation)."""
        # Rough cost estimates per 1K tokens (2024 pricing)
        cost_per_1k = {
            "gpt-3.5-turbo": 0.001,
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "claude-3-haiku-20240307": 0.00025,
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-opus-20240229": 0.015,
            "gemini-1.5-flash": 0.0001,
            "gemini-1.5-pro": 0.002,
        }

        # Estimate tokens (rough: 4 chars per token)
        estimated_tokens = len(content) / 4 + 200  # Add overhead for prompt
        cost_multiplier = cost_per_1k.get(self.model, 0.001)

        return (estimated_tokens / 1000) * cost_multiplier

    def get_capabilities(self) -> dict:
        """Return API parser capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update(
            {
                "supports_structured_output": True,
                "max_content_length": 100000,  # Most APIs support ~100K tokens
                "provider": self.provider,
                "model": self.model,
                "estimated_cost_per_request": self.get_cost_estimate("sample text"),
                "supports_json_schema": True,
                "requires_internet": True,
            }
        )
        return capabilities

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close session."""
        if self.session:
            await self.session.close()
            self.session = None
