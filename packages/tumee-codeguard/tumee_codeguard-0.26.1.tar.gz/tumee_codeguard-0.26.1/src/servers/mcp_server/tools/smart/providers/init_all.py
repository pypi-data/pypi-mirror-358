"""
Central Provider Initialization.

Initializes and registers all available task management providers.
Each provider is initialized independently and failures are logged but don't block others.
"""

import logging

logger = logging.getLogger(__name__)


def init_all_providers() -> None:
    """Initialize and register all available providers."""

    # Initialize Dart provider (fully implemented)
    try:
        from .dart import init_dart_provider

        init_dart_provider()
    except Exception as e:
        logger.error(f"Failed to initialize Dart provider: {e}")

    # Initialize GitHub provider (stub)
    try:
        from .github import init_github_provider

        init_github_provider()
    except Exception as e:
        logger.error(f"Failed to initialize GitHub provider: {e}")

    # Initialize Jira provider (stub)
    try:
        from .jira import init_jira_provider

        init_jira_provider()
    except Exception as e:
        logger.error(f"Failed to initialize Jira provider: {e}")

    # Initialize Linear provider (stub)
    try:
        from .linear import init_linear_provider

        init_linear_provider()
    except Exception as e:
        logger.error(f"Failed to initialize Linear provider: {e}")

    logger.info("Provider initialization completed")


def get_provider_config(provider_name: str):
    """Get configuration for a specific provider."""
    if provider_name == "dart":
        from .dart import create_dart_config

        return create_dart_config()
    elif provider_name == "github":
        from .github import create_github_config

        return create_github_config()
    elif provider_name == "jira":
        from .jira import create_jira_config

        return create_jira_config()
    elif provider_name == "linear":
        from .linear import create_linear_config

        return create_linear_config()
    else:
        logger.warning(f"Unknown provider: {provider_name}")
        return None
