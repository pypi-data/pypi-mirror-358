"""
Jira Provider Registration and Initialization.

Registers the Jira provider with the provider registry and handles
initialization with environment-based configuration.
"""

import logging
import os
from typing import Optional

from ..base import ProviderConfig
from ..registry import ProviderRegistry
from .provider import JiraProvider

logger = logging.getLogger(__name__)


def init_jira_provider() -> bool:
    """
    Initialize and register the Jira provider.

    Returns:
        True if initialization successful, False otherwise
    """
    try:
        # Register Jira provider with URL patterns
        ProviderRegistry.register_provider(
            provider_name="jira",
            provider_class=JiraProvider,
            url_patterns=[
                ".atlassian.net",
                "atlassian.net",
                "jira://",
            ],
        )

        logger.info("Jira provider registered successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to register Jira provider: {e}")
        return False


def create_jira_config() -> Optional[ProviderConfig]:
    """
    Create Jira provider configuration from environment variables.

    Required environment variables:
    - JIRA_TOKEN: Jira API token
    - JIRA_EMAIL: Email address associated with Jira account
    - JIRA_BASE_URL: Base URL for Jira instance (e.g., https://company.atlassian.net)
    - JIRA_DEFAULT_PROJECT: Default Jira project key

    Returns:
        ProviderConfig for Jira if credentials available, None otherwise
    """
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_base_url = os.getenv("JIRA_BASE_URL")
    default_project = os.getenv("JIRA_DEFAULT_PROJECT")

    if not jira_token:
        logger.warning("JIRA_TOKEN not found in environment variables")
        return None

    if not jira_email:
        logger.warning("JIRA_EMAIL not found in environment variables")
        return None

    if not jira_base_url:
        logger.warning("JIRA_BASE_URL not found in environment variables")
        return None

    if not default_project:
        logger.warning("JIRA_DEFAULT_PROJECT not found in environment variables")
        return None

    config = ProviderConfig(
        provider_name="jira",
        base_url=jira_base_url,
        authentication={"jira_token": jira_token, "email": jira_email},
        default_project=default_project,
        custom_fields={},
    )

    logger.info(f"Jira provider configuration created for project: {default_project}")
    return config


def get_jira_provider() -> Optional[JiraProvider]:
    """
    Get a configured Jira provider instance.

    Returns:
        JiraProvider instance if configuration available, None otherwise
    """
    config = create_jira_config()
    if not config:
        return None

    try:
        provider = JiraProvider(config)
        logger.info("Jira provider instance created")
        return provider
    except Exception as e:
        logger.error(f"Failed to create Jira provider instance: {e}")
        return None
