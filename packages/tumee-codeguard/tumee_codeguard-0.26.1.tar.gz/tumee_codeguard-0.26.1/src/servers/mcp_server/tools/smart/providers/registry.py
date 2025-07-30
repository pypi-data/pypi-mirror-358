"""
Provider registry for managing task provider implementations.

Central registry that manages available task providers and provides
factory methods for creating provider instances based on URLs or
explicit provider names.
"""

import logging
from typing import Dict, Optional, Type

from .base import ProviderConfig, TaskProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry for task provider implementations."""

    _providers: Dict[str, Type[TaskProvider]] = {}
    _url_patterns: Dict[str, str] = {}  # URL patterns -> provider names

    @classmethod
    def register_provider(
        cls,
        provider_name: str,
        provider_class: Type[TaskProvider],
        url_patterns: Optional[list] = None,
    ) -> None:
        """
        Register a task provider implementation.

        Args:
            provider_name: Unique name for the provider
            provider_class: TaskProvider implementation class
            url_patterns: List of URL patterns this provider handles
        """
        cls._providers[provider_name] = provider_class

        if url_patterns:
            for pattern in url_patterns:
                cls._url_patterns[pattern] = provider_name

        logger.info(f"Registered task provider: {provider_name}")

    @classmethod
    def get_provider_class(cls, provider_name: str) -> Optional[Type[TaskProvider]]:
        """Get provider class by name."""
        return cls._providers.get(provider_name)

    @classmethod
    def detect_provider_from_url(cls, url_or_id: str) -> Optional[str]:
        """
        Detect provider from URL or task ID.

        Args:
            url_or_id: Task URL, ID, or provider-specific reference

        Returns:
            Provider name if detected, None otherwise
        """
        url_lower = url_or_id.lower()

        for pattern, provider_name in cls._url_patterns.items():
            if pattern in url_lower:
                return provider_name

        return None

    @classmethod
    def list_providers(cls) -> list:
        """List all registered provider names."""
        return list(cls._providers.keys())

    @classmethod
    def create_provider(cls, provider_name: str, config: ProviderConfig) -> Optional[TaskProvider]:
        """
        Create a provider instance.

        Args:
            provider_name: Name of the provider to create
            config: Provider configuration

        Returns:
            TaskProvider instance or None if provider not found
        """
        provider_class = cls.get_provider_class(provider_name)
        if not provider_class:
            logger.error(f"Unknown provider: {provider_name}")
            return None

        try:
            return provider_class(config)
        except Exception as e:
            logger.error(f"Failed to create provider {provider_name}: {e}")
            return None


def get_provider(
    provider_name: Optional[str] = None,
    url_or_id: Optional[str] = None,
    config: Optional[ProviderConfig] = None,
) -> Optional[TaskProvider]:
    """
    Get a provider instance by name or URL detection.

    Args:
        provider_name: Explicit provider name
        url_or_id: URL or ID to detect provider from
        config: Provider configuration (required for creation)

    Returns:
        TaskProvider instance or None
    """
    if not config:
        logger.error("Provider config is required")
        return None

    # Try explicit provider name first
    if provider_name:
        return ProviderRegistry.create_provider(provider_name, config)

    # Try to detect from URL
    if url_or_id:
        detected_provider = ProviderRegistry.detect_provider_from_url(url_or_id)
        if detected_provider:
            return ProviderRegistry.create_provider(detected_provider, config)

    logger.warning("Could not determine provider")
    return None
