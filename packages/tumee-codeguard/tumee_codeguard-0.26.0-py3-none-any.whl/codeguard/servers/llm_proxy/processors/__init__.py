"""
Payload processors for the event-driven modification system.

This module provides the base interfaces and built-in processors
for modifying intercepted LLM payloads.
"""

import logging
from typing import Dict, List, Type

from ..interceptor_types import PayloadProcessor, ProcessorConfig


def get_built_in_processors() -> Dict[str, Type[PayloadProcessor]]:
    """
    Get all built-in payload processors.

    Returns:
        Dictionary mapping processor names to their classes
    """
    processors = {}

    try:
        from .hook_interceptor import HookInterceptor

        processors["hook_interceptor"] = HookInterceptor
    except ImportError as e:
        logging.getLogger(__name__).warning(f"Could not load HookInterceptor: {e}")

    # Add other built-in processors here as they are implemented
    # from .security_processor import SecurityProcessor
    # processors["security"] = SecurityProcessor

    return processors


def load_processor_from_config(processor_config: Dict) -> PayloadProcessor:
    """
    Load a processor instance from configuration.

    Args:
        processor_config: Configuration dictionary with processor settings

    Returns:
        Initialized processor instance

    Example config:
        {
            "type": "urgent_notes",
            "config": {
                "priority": 50,
                "enabled": True
            }
        }
    """
    processor_type = processor_config.get("type")
    if not processor_type:
        raise ValueError("Processor config must specify 'type'")

    built_in_processors = get_built_in_processors()
    if processor_type not in built_in_processors:
        raise ValueError(f"Unknown processor type: {processor_type}")

    processor_class = built_in_processors[processor_type]
    config_dict = processor_config.get("config", {})

    # Create processor instance with config
    return processor_class(**config_dict)


class BaseProcessor:
    """
    Base class for payload processors with common functionality.

    Provides default implementations and utilities that most
    processors can use.
    """

    def __init__(self, priority: int = 100, enabled: bool = True, **kwargs):
        self.priority = priority
        self.enabled = enabled
        self.logger = logging.getLogger(self.__class__.__name__)

        # Store any additional config
        self.config_data = kwargs

    def get_config(self) -> ProcessorConfig:
        """Get processor configuration."""
        return ProcessorConfig(
            priority=self.priority,
            enabled=self.enabled,
            conditions=self.config_data.get("conditions"),
        )

    async def process(self, event_type, payload):
        """
        Default process implementation - subclasses should override.

        This base implementation just logs the event and returns
        the payload unchanged.
        """
        self.logger.debug(f"Processing {event_type.value} event")
        return payload


# Re-export key interfaces for convenience
__all__ = [
    "PayloadProcessor",
    "ProcessorConfig",
    "BaseProcessor",
    "get_built_in_processors",
    "load_processor_from_config",
]
