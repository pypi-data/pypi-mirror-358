"""
Dart Provider Registration and Initialization.

Registers the Dart provider with the provider registry and handles
initialization with environment-based configuration.
"""

import logging
import os
from typing import Optional

from ..base import ProviderConfig
from ..registry import ProviderRegistry
from .provider import DartProvider

logger = logging.getLogger(__name__)


def init_dart_provider() -> bool:
    """
    Initialize and register the Dart provider.

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        # Register Dart provider with URL patterns
        ProviderRegistry.register_provider(
            provider_name="dart",
            provider_class=DartProvider,
            url_patterns=["itsdart.com", "app.itsdart.com", "dart://", "dart://"],
        )

        logger.info("Dart provider registered successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to register Dart provider: {e}")
        return False


def create_dart_config() -> Optional[ProviderConfig]:
    """
    Create Dart provider configuration from environment variables.

    Returns:
        ProviderConfig for Dart if DART_TOKEN available, None otherwise
    """
    dart_token = os.getenv("DART_TOKEN")

    if not dart_token:
        logger.warning("DART_TOKEN not found in environment variables")
        return None

    config = ProviderConfig(
        provider_name="dart",
        base_url="https://app.itsdart.com",
        authentication={"dart_token": dart_token},
        default_project=os.getenv("DART_DEFAULT_DARTBOARD"),  # Optional
        custom_fields={},
    )

    logger.info("Dart provider configuration created")
    return config


def get_dart_provider() -> Optional[DartProvider]:
    """
    Get a configured Dart provider instance.

    Returns:
        DartProvider instance if configuration available, None otherwise
    """
    config = create_dart_config()
    if not config:
        return None

    try:
        provider = DartProvider(config)
        logger.info("Dart provider instance created")
        return provider
    except Exception as e:
        logger.error(f"Failed to create Dart provider instance: {e}")
        return None
