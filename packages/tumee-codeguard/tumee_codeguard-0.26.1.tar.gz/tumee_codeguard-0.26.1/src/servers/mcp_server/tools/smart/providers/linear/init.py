"""
Linear Provider Registration and Initialization.

Registers the Linear provider with the provider registry and handles
initialization with environment-based configuration.
"""

import logging
import os
from typing import Optional

from ..base import ProviderConfig
from ..registry import ProviderRegistry
from .provider import LinearProvider

logger = logging.getLogger(__name__)


def init_linear_provider() -> bool:
    """
    Initialize and register the Linear provider.

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        # Register Linear provider with URL patterns
        ProviderRegistry.register_provider(
            provider_name="linear",
            provider_class=LinearProvider,
            url_patterns=[
                "linear.app",
                "www.linear.app",
                "linear://",
            ],
        )

        logger.info("Linear provider registered successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to register Linear provider: {e}")
        return False


def create_linear_config() -> Optional[ProviderConfig]:
    """
    Create Linear provider configuration from environment variables.

    Required environment variables:
    - LINEAR_TOKEN: Linear API key

    Optional environment variables:
    - LINEAR_DEFAULT_TEAM: Default Linear team ID

    Returns:
        ProviderConfig for Linear if credentials available, None otherwise
    """
    linear_token = os.getenv("LINEAR_TOKEN")
    default_team = os.getenv("LINEAR_DEFAULT_TEAM")

    if not linear_token:
        logger.warning("LINEAR_TOKEN not found in environment variables")
        return None

    config = ProviderConfig(
        provider_name="linear",
        base_url="https://api.linear.app/graphql",
        authentication={"linear_token": linear_token},
        default_project=default_team,  # Team ID for Linear
        custom_fields={},
    )

    if default_team:
        logger.info(f"Linear provider configuration created for team: {default_team}")
    else:
        logger.info("Linear provider configuration created (no default team)")

    return config


def get_linear_provider() -> Optional[LinearProvider]:
    """
    Get a configured Linear provider instance.

    Returns:
        LinearProvider instance if configuration available, None otherwise
    """
    config = create_linear_config()
    if not config:
        return None

    try:
        provider = LinearProvider(config)
        logger.info("Linear provider instance created")
        return provider
    except Exception as e:
        logger.error(f"Failed to create Linear provider instance: {e}")
        return None
