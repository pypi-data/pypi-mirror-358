"""
Core types for the event-driven payload modification system.

This module contains shared types and enums to avoid circular imports
between event_manager, payload_context, and other components.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Protocol


class EventType(Enum):
    """Supported event types for payload modification."""

    # Request flow events
    REQUEST_RECEIVED = "request_received"  # Raw request from client
    REQUEST_PROCESSED = "request_processed"  # After initial processing
    REQUEST_UPSTREAM = "request_upstream"  # Before sending to upstream

    # Response flow events
    RESPONSE_RECEIVED = "response_received"  # Raw response from upstream
    RESPONSE_PROCESSED = "response_processed"  # After processing/streaming
    RESPONSE_CLIENT = "response_client"  # Before sending to client

    # Tool call events
    TOOL_CALL_PRE = "tool_call_pre"  # Before tool execution
    TOOL_CALL_POST = "tool_call_post"  # After tool execution
    TOOL_RESULT_PRE = "tool_result_pre"  # Before tool result processing


@dataclass
class ProcessorConfig:
    """Configuration for a payload processor."""

    priority: int = 100  # Lower numbers = higher priority
    enabled: bool = True
    conditions: Optional[Dict[str, Any]] = None  # Conditional execution criteria


class PayloadProcessor(Protocol):
    """Protocol for payload processors that can modify intercepted data."""

    async def process(self, event_type: EventType, payload: "PayloadContext") -> "PayloadContext":
        """
        Process and potentially modify payload data.

        Args:
            event_type: The type of event being processed
            payload: The payload context containing request/response data

        Returns:
            Modified payload context (can return the same instance)
        """
        ...

    def get_config(self) -> ProcessorConfig:
        """Get processor configuration."""
        ...


@dataclass
class EventSubscription:
    """Represents a subscription to an event type."""

    processor: PayloadProcessor
    config: ProcessorConfig
    processor_name: str
