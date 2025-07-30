"""
Hook system types for flexible message interception and streamable responses.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


class HookResponse:
    """Constants for hook callback return actions."""

    CONTINUE = "continue"  # Continue with original request to LLM
    MODIFY = "modify"  # Modify request and send to LLM
    BLOCK = "block"  # Don't send to LLM, return local response

    # New streamable response types
    RESPOND_JSON = "respond_json"  # Return immediate JSON response
    RESPOND_STREAM = "respond_stream"  # Return streaming SSE response
    RESPOND_HYBRID = "respond_hybrid"  # Dynamic decision based on request


@dataclass
class HookResult:
    """
    Result returned by hook callbacks to control request flow and response type.

    Attributes:
        action: One of HookResponse constants (CONTINUE, MODIFY, BLOCK, RESPOND_JSON, RESPOND_STREAM, RESPOND_HYBRID)
        response_data: For response actions - the local response to return
        modified_request: For MODIFY action - request modifications to apply
        message: Optional status/debug message
        sse_events: For streaming responses - list of SSE event strings
        force_stream: For RESPOND_HYBRID - force streaming regardless of request
    """

    action: str
    response_data: Optional[Dict[str, Any]] = None
    modified_request: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    sse_events: Optional[list] = None
    force_stream: Optional[bool] = None

    def __post_init__(self):
        """Validate the hook result configuration."""
        valid_actions = (
            HookResponse.CONTINUE,
            HookResponse.MODIFY,
            HookResponse.BLOCK,
            HookResponse.RESPOND_JSON,
            HookResponse.RESPOND_STREAM,
            HookResponse.RESPOND_HYBRID,
        )
        if self.action not in valid_actions:
            raise ValueError(f"Invalid hook action: {self.action}")

        # Response actions require response_data
        response_actions = (
            HookResponse.BLOCK,
            HookResponse.RESPOND_JSON,
            HookResponse.RESPOND_STREAM,
            HookResponse.RESPOND_HYBRID,
        )
        if self.action in response_actions and not self.response_data:
            raise ValueError(f"{self.action} action requires response_data")

        if self.action == HookResponse.MODIFY and not self.modified_request:
            raise ValueError("MODIFY action requires modified_request")

        if self.action == HookResponse.RESPOND_STREAM and not self.sse_events:
            raise ValueError("RESPOND_STREAM action requires sse_events")


def create_continue_result(message: Optional[str] = None) -> HookResult:
    """Create a CONTINUE hook result."""
    return HookResult(action=HookResponse.CONTINUE, message=message)


def create_modify_result(
    modified_request: Dict[str, Any], message: Optional[str] = None
) -> HookResult:
    """Create a MODIFY hook result."""
    return HookResult(
        action=HookResponse.MODIFY, modified_request=modified_request, message=message
    )


def create_block_result(response_data: Dict[str, Any], message: Optional[str] = None) -> HookResult:
    """Create a BLOCK hook result."""
    return HookResult(action=HookResponse.BLOCK, response_data=response_data, message=message)


def create_json_response_result(
    response_data: Dict[str, Any], message: Optional[str] = None
) -> HookResult:
    """Create a RESPOND_JSON hook result."""
    return HookResult(
        action=HookResponse.RESPOND_JSON, response_data=response_data, message=message
    )


def create_stream_response_result(
    response_data: Dict[str, Any], sse_events: list, message: Optional[str] = None
) -> HookResult:
    """Create a RESPOND_STREAM hook result."""
    return HookResult(
        action=HookResponse.RESPOND_STREAM,
        response_data=response_data,
        sse_events=sse_events,
        message=message,
    )


def create_hybrid_response_result(
    response_data: Dict[str, Any],
    sse_events: Optional[list] = None,
    force_stream: Optional[bool] = None,
    message: Optional[str] = None,
) -> HookResult:
    """Create a RESPOND_HYBRID hook result."""
    return HookResult(
        action=HookResponse.RESPOND_HYBRID,
        response_data=response_data,
        sse_events=sse_events,
        force_stream=force_stream,
        message=message,
    )
