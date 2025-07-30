"""
Generic hook interceptor for flexible message prefix handling.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from ....core.infrastructure.hook_registry import get_hook_registry
from ..interceptor_types import EventType, ProcessorConfig
from ..payload_context import PayloadContext
from .hook_types import HookResponse


class HookInterceptor:
    """
    Generic interceptor that supports registering callbacks for message prefixes.

    This interceptor allows plugins to register for specific message prefixes
    (like "urgent:", "debug:", "help:") and control whether requests continue
    to the LLM, get modified, or are blocked entirely.
    """

    def __init__(self, priority: int = 10):  # High priority to intercept early
        self.priority = priority
        self.enabled = True
        self.logger = logging.getLogger(__name__)

        # Registered hooks: prefix -> callback
        self.hooks: Dict[str, Callable] = {}

        # Hook statistics
        self.hook_stats: Dict[str, Dict[str, int]] = {}

        # Register with core hook registry to receive existing hooks
        hook_registry = get_hook_registry()
        hook_registry.register_interceptor(self)

    def get_config(self) -> ProcessorConfig:
        """Get processor configuration."""
        return ProcessorConfig(
            priority=self.priority, enabled=self.enabled, conditions=None  # Process all requests
        )

    def register_hook(self, prefix: str, callback: Callable) -> None:
        """
        Register a hook callback for messages starting with the given prefix.

        Args:
            prefix: Message prefix to match (e.g., "urgent:", "debug:")
            callback: Async function with signature:
                     async def callback(message: str, payload: PayloadContext) -> HookResult
        """
        if prefix in self.hooks:
            self.logger.warning(f"Overriding existing hook for prefix: {prefix}")

        self.hooks[prefix] = callback
        self.hook_stats[prefix] = {"calls": 0, "blocks": 0, "modifies": 0, "continues": 0}
        self.logger.info(f"Registered hook for prefix: {prefix}")

    def unregister_hook(self, prefix: str) -> bool:
        """
        Unregister a hook for the given prefix.

        Args:
            prefix: Message prefix to unregister

        Returns:
            True if hook was found and removed
        """
        if prefix in self.hooks:
            del self.hooks[prefix]
            del self.hook_stats[prefix]
            self.logger.info(f"Unregistered hook for prefix: {prefix}")
            return True
        return False

    def get_registered_hooks(self) -> List[str]:
        """Get list of all registered hook prefixes."""
        return list(self.hooks.keys())

    def get_hook_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all hooks."""
        return self.hook_stats.copy()

    async def process(self, event_type: EventType, payload: PayloadContext) -> PayloadContext:
        """
        Process payload and check for registered hooks.

        Args:
            event_type: Type of event being processed
            payload: PayloadContext containing request/response data

        Returns:
            Modified PayloadContext with hook actions applied
        """
        try:
            if event_type == EventType.REQUEST_RECEIVED:
                return await self._process_request(payload)
            else:
                # Pass through other event types
                return payload

        except Exception as e:
            self.logger.error(f"Error in hook interceptor: {e}", exc_info=True)
            return payload

    async def _process_request(self, payload: PayloadContext) -> PayloadContext:
        """
        Process incoming request for hook prefixes.

        Args:
            payload: PayloadContext with request data

        Returns:
            Modified PayloadContext with hook actions applied
        """
        # Extract the last user message
        message_text = self._extract_last_user_message(payload)
        if not message_text:
            return payload

        # Check all registered hooks
        for prefix, callback in self.hooks.items():
            # Only process if message starts with prefix and ends with completion marker "*"
            if message_text.strip().lower().startswith(
                prefix.lower()
            ) and message_text.strip().endswith("*"):
                self.logger.info(f"Hook triggered for prefix: {prefix}")

                try:
                    # Strip the completion marker and execute the hook callback
                    clean_message = message_text.strip().rstrip("*").strip()
                    result = await callback(clean_message, payload)

                    # Update statistics
                    self.hook_stats[prefix]["calls"] += 1

                    # Apply the hook result
                    if result.action in (
                        HookResponse.BLOCK,
                        HookResponse.RESPOND_JSON,
                        HookResponse.RESPOND_STREAM,
                        HookResponse.RESPOND_HYBRID,
                    ):
                        self.hook_stats[prefix]["blocks"] += 1

                        # Store hook metadata in request data for server access
                        if payload.request_data is None:
                            payload.request_data = {}

                        payload.request_data["_hook_action"] = result.action
                        payload.request_data["_hook_response"] = result.response_data
                        payload.request_data["_hook_message"] = result.message

                        # Handle SSE events for streaming responses
                        if result.sse_events:
                            payload.request_data["_hook_sse_events"] = result.sse_events
                        # Note: SSE events will be generated by streamable handler with provider awareness

                        self.logger.info(
                            f"Hook {prefix} returned response with action {result.action}: {result.message}"
                        )

                    elif result.action == HookResponse.MODIFY:
                        self.hook_stats[prefix]["modifies"] += 1

                        # Store hook metadata in request data
                        if payload.request_data is None:
                            payload.request_data = {}

                        payload.request_data["_hook_action"] = "modify"
                        payload.request_data["_hook_message"] = result.message

                        # Apply modifications to request data
                        if result.modified_request:
                            payload.request_data.update(result.modified_request)

                        self.logger.info(f"Hook {prefix} modified request: {result.message}")

                    elif result.action == HookResponse.CONTINUE:
                        self.hook_stats[prefix]["continues"] += 1

                        # Store hook metadata in request data
                        if payload.request_data is None:
                            payload.request_data = {}

                        payload.request_data["_hook_action"] = "continue"
                        payload.request_data["_hook_message"] = result.message

                        self.logger.info(f"Hook {prefix} continued request: {result.message}")

                    # Only process the first matching hook
                    break

                except Exception as e:
                    self.logger.error(f"Error executing hook {prefix}: {e}", exc_info=True)
                    # Continue with normal processing on hook error
                    continue

        return payload

    def _extract_last_user_message(self, payload: PayloadContext) -> Optional[str]:
        """
        Extract the text content of the last user message from the payload.

        Args:
            payload: PayloadContext to extract message from

        Returns:
            Text content of last user message or None
        """
        messages = payload.get_messages()
        if not messages:
            return None

        # Find the last user message
        last_user_message = None
        for message in reversed(messages):
            if message.get("role") == "user":
                last_user_message = message
                break

        if not last_user_message:
            return None

        content = last_user_message.get("content", "")

        # Handle both string and list content formats
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # For structured content, look for the actual user input
            # Skip system-reminder blocks and look for short, command-like text
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "").strip()

                    # Skip system reminders, conversation summaries, and multiline text
                    if (
                        text.startswith("<system-reminder>")
                        or text.startswith("Please write")
                        or text.startswith("User:")
                        or "\n" in text.strip()
                    ):
                        continue

                    # Return single-line text (likely actual user input)
                    if text:
                        return text

        return None

    def _generate_sse_events_for_response(self, response_data: Dict[str, Any]) -> List[str]:
        """
        Generate SSE events for a response data structure.

        Args:
            response_data: Response data to convert to SSE events

        Returns:
            List of SSE event strings
        """
        try:
            import json

            sse_events = []

            # Generate message_start event
            message_start_data = {
                "type": "message_start",
                "message": {
                    "id": response_data.get("id", "local-response"),
                    "type": "message",
                    "role": "assistant",
                    "content": [],
                    "model": response_data.get("model", "local-hook"),
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": response_data.get("usage", {"input_tokens": 0, "output_tokens": 0}),
                },
            }
            sse_events.append(f"event: message_start\ndata: {json.dumps(message_start_data)}\n\n")

            # Extract content for streaming
            content_blocks = response_data.get("content", [])
            for i, content_block in enumerate(content_blocks):
                if content_block.get("type") == "text":
                    text_content = content_block.get("text", "")

                    # Content block start
                    start_data = {
                        "type": "content_block_start",
                        "index": i,
                        "content_block": {"type": "text", "text": ""},
                    }
                    sse_events.append(
                        f"event: content_block_start\ndata: {json.dumps(start_data)}\n\n"
                    )

                    # Content block delta
                    delta_data = {
                        "type": "content_block_delta",
                        "index": i,
                        "delta": {"type": "text_delta", "text": text_content},
                    }
                    sse_events.append(
                        f"event: content_block_delta\ndata: {json.dumps(delta_data)}\n\n"
                    )

                    # Content block stop
                    stop_data = {"type": "content_block_stop", "index": i}
                    sse_events.append(
                        f"event: content_block_stop\ndata: {json.dumps(stop_data)}\n\n"
                    )

            # Message delta with usage
            if "usage" in response_data:
                delta_data = {
                    "type": "message_delta",
                    "delta": {"stop_reason": response_data.get("stop_reason", "end_turn")},
                    "usage": response_data["usage"],
                }
                sse_events.append(f"event: message_delta\ndata: {json.dumps(delta_data)}\n\n")

            # Message stop
            stop_data = {"type": "message_stop"}
            sse_events.append(f"event: message_stop\ndata: {json.dumps(stop_data)}\n\n")

            return sse_events

        except Exception as e:
            self.logger.error(f"Error generating SSE events: {e}", exc_info=True)
            # Return simple error event
            error_event = f'event: error\ndata: {{"type": "error", "error": "Response conversion failed"}}\n\n'
            return [error_event]

    async def clear_statistics(self) -> None:
        """Clear all hook statistics."""
        for prefix in self.hook_stats:
            self.hook_stats[prefix] = {"calls": 0, "blocks": 0, "modifies": 0, "continues": 0}
        self.logger.info("Cleared hook statistics")

    def __str__(self) -> str:
        """String representation for debugging."""
        return f"HookInterceptor(hooks={list(self.hooks.keys())}, enabled={self.enabled})"
