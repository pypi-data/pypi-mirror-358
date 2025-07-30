"""
Streamable HTTP response handler that dynamically chooses response type.

This module implements the core of the Streamable HTTP protocol by allowing
responses to start as standard HTTP and upgrade to SSE streaming as needed.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response, StreamResponse

from .processors.hook_types import HookResponse, HookResult


class StreamableResponseHandler:
    """
    Handler for streamable HTTP responses that can dynamically upgrade to SSE.

    This class implements the core Streamable HTTP pattern where:
    1. All responses start as StreamResponse (uncommitted)
    2. Hook results determine the final response type
    3. Automatic conversion between JSON and SSE formats
    4. Backward compatibility with existing hook patterns
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def handle_hook_result(
        self,
        hook_result: HookResult,
        original_request: Request,
        request_data: Dict[str, Any],
        provider: str,
    ) -> StreamResponse:
        """
        Handle hook result by creating appropriate response type.

        Args:
            hook_result: Result from hook processing
            original_request: Original HTTP request
            request_data: Parsed request JSON

        Returns:
            StreamResponse with appropriate content
        """
        try:
            # Determine if client wants streaming
            client_wants_stream = request_data.get("stream", False)

            self.logger.debug(
                f"Streamable response: action={hook_result.action}, stream={client_wants_stream}"
            )

            # Handle different hook actions
            if hook_result.action == HookResponse.RESPOND_JSON:
                return await self._create_json_response(hook_result.response_data, original_request)

            elif hook_result.action == HookResponse.RESPOND_STREAM:
                return await self._create_sse_response(
                    hook_result.sse_events or [], original_request
                )

            elif hook_result.action == HookResponse.RESPOND_HYBRID:
                # Dynamic decision based on request and hook preferences
                should_stream = (
                    client_wants_stream or hook_result.force_stream or bool(hook_result.sse_events)
                )

                if should_stream:
                    # Generate SSE events if not provided
                    sse_events = hook_result.sse_events or []
                    if not sse_events:
                        sse_events = self._convert_response_to_sse(
                            hook_result.response_data, provider
                        )
                    return await self._create_sse_response(sse_events, original_request)
                else:
                    return await self._create_json_response(
                        hook_result.response_data, original_request
                    )

            elif hook_result.action == HookResponse.BLOCK:
                # Block request and return local response
                if client_wants_stream:
                    # Convert response to SSE events
                    sse_events = self._convert_response_to_sse(hook_result.response_data, provider)
                    return await self._create_sse_response(sse_events, original_request)
                else:
                    return await self._create_json_response(
                        hook_result.response_data, original_request
                    )

            else:
                # CONTINUE, MODIFY - should not reach here in normal flow
                raise ValueError(
                    f"Unexpected hook action for response handling: {hook_result.action}"
                )

        except Exception as e:
            self.logger.error(f"Error handling hook result: {e}", exc_info=True)
            return await self._create_error_response(str(e), original_request)

    async def _create_json_response(
        self, response_data: Dict[str, Any], original_request: Request
    ) -> Union[StreamResponse, Response]:
        """Create a standard JSON response."""
        try:
            # Use web.json_response (sets Content-Type automatically, no duplicate header)
            response = web.json_response(
                response_data,
                status=200,
                headers={"Access-Control-Allow-Origin": "*"},
            )

            self.logger.debug("Created JSON response")
            return response

        except Exception as e:
            self.logger.error(f"Error creating JSON response: {e}", exc_info=True)
            return await self._create_error_response(str(e), original_request)

    async def _create_sse_response(
        self, sse_events: List[str], original_request: Request
    ) -> StreamResponse:
        """Create a streaming SSE response."""
        try:
            # Create streaming response with SSE headers
            response = StreamResponse(
                status=200,
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "X-Accel-Buffering": "no",  # Disable nginx buffering
                    "Transfer-Encoding": "chunked",
                },
            )

            await response.prepare(original_request)

            # Stream each SSE event
            for event_str in sse_events:
                await response.write(event_str.encode("utf-8"))

                # Force flush for real-time streaming
                if hasattr(response, "drain"):
                    await response.drain()

            # Properly close the stream
            await response.write_eof()

            self.logger.debug(f"Created SSE response with {len(sse_events)} events")
            return response

        except Exception as e:
            self.logger.error(f"Error creating SSE response: {e}", exc_info=True)
            return await self._create_error_response(str(e), original_request)

    def _convert_response_to_sse(self, response_data: Dict[str, Any], provider: str) -> List[str]:
        """
        Convert a JSON response to SSE events in the appropriate provider format.

        Args:
            response_data: JSON response data
            provider: Provider type (anthropic, openai, etc.)

        Returns:
            List of SSE event strings
        """
        try:
            if provider == "openai":
                return self._convert_to_openai_sse(response_data)
            else:
                return self._convert_to_anthropic_sse(response_data)

        except Exception as e:
            self.logger.error(f"Error converting response to SSE: {e}", exc_info=True)
            # Return simple error event
            error_event = f'event: error\\ndata: {{"type": "error", "error": "Response conversion failed"}}\\n\\n'
            return [error_event]

    def _convert_to_openai_sse(self, response_data: Dict[str, Any]) -> List[str]:
        """Convert response to OpenAI SSE format."""
        try:
            import json

            sse_events = []

            # Extract content from either OpenAI choices or direct content
            content_text = ""
            if "choices" in response_data and response_data["choices"]:
                content_text = response_data["choices"][0].get("message", {}).get("content", "")
            elif "content" in response_data:
                # Handle direct content
                content_text = response_data["content"]

            # Create OpenAI streaming chunk
            chunk_data = {
                "id": response_data.get("id", "local-response"),
                "object": "chat.completion.chunk",
                "created": 1234567890,  # timestamp
                "model": response_data.get("model", "local-hook"),
                "choices": [
                    {"index": 0, "delta": {"content": content_text}, "finish_reason": "stop"}
                ],
            }

            sse_events.append(f"data: {json.dumps(chunk_data)}\\n\\n")
            sse_events.append("data: [DONE]\\n\\n")

            return sse_events

        except Exception as e:
            self.logger.error(f"Error converting to OpenAI SSE: {e}", exc_info=True)
            return [f'data: {{"error": "OpenAI SSE conversion failed"}}\\n\\n']

    def _convert_to_anthropic_sse(self, response_data: Dict[str, Any]) -> List[str]:
        """Convert response to Anthropic SSE format."""
        try:
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

            # Extract content for streaming - handle both OpenAI and Anthropic formats
            content_blocks = response_data.get("content", [])

            # If no content blocks, check for OpenAI format
            if not content_blocks and "choices" in response_data:
                choices = response_data.get("choices", [])
                if choices and "message" in choices[0]:
                    message_content = choices[0]["message"].get("content", "")
                    if message_content:
                        content_blocks = [{"type": "text", "text": message_content}]
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
            self.logger.error(f"Error converting response to SSE: {e}", exc_info=True)
            # Return simple error event
            error_event = f'event: error\ndata: {{"type": "error", "error": "Response conversion failed"}}\n\n'
            return [error_event]

    async def _create_error_response(
        self, error_message: str, original_request: Request
    ) -> StreamResponse:
        """Create an error response."""
        error_data = {"type": "error", "error": {"type": "proxy_error", "message": error_message}}

        return web.json_response(
            error_data, status=500, headers={"Access-Control-Allow-Origin": "*"}
        )
