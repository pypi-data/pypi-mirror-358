"""
GitHub Provider Registration and Initialization.

Registers the GitHub provider with the provider registry and handles
initialization with environment-based configuration.
"""

import logging
import os
from typing import Optional

from ..base import ProviderConfig
from ..registry import ProviderRegistry
from .provider import GitHubProvider

logger = logging.getLogger(__name__)


def init_github_provider() -> bool:
    """
    Initialize and register the GitHub provider.

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        # Register GitHub provider with URL patterns
        ProviderRegistry.register_provider(
            provider_name="github",
            provider_class=GitHubProvider,
            url_patterns=[
                "github.com",
                "www.github.com",
                "github://",
            ],
        )

        logger.info("GitHub provider registered successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to register GitHub provider: {e}")
        return False


def create_github_config() -> Optional[ProviderConfig]:
    """
    Create GitHub provider configuration from environment variables.

    Required environment variables:
    - GITHUB_TOKEN: GitHub personal access token
    - GITHUB_DEFAULT_REPO: Default repository in 'owner/repo' format

    Returns:
        ProviderConfig for GitHub if credentials available, None otherwise
    """
    github_token = os.getenv("GITHUB_TOKEN")
    default_repo = os.getenv("GITHUB_DEFAULT_REPO")

    if not github_token:
        logger.warning("GITHUB_TOKEN not found in environment variables")
        return None

    if not default_repo:
        logger.warning("GITHUB_DEFAULT_REPO not found in environment variables")
        return None

    config = ProviderConfig(
        provider_name="github",
        base_url="https://api.github.com",
        authentication={"github_token": github_token},
        default_project=default_repo,
        custom_fields={},
    )

    logger.info(f"GitHub provider configuration created for repo: {default_repo}")
    return config


def get_github_provider() -> Optional[GitHubProvider]:
    """
    Get a configured GitHub provider instance.

    Returns:
        GitHubProvider instance if configuration available, None otherwise
    """
    config = create_github_config()
    if not config:
        return None

    try:
        provider = GitHubProvider(config)
        logger.info("GitHub provider instance created")
        return provider
    except Exception as e:
        logger.error(f"Failed to create GitHub provider instance: {e}")
        return None
