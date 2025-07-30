"""
Response streaming with proper SSE event boundary preservation.

This module handles the critical challenge of maintaining Server-Sent Events (SSE)
protocol compliance while processing streaming responses in real-time.
"""

import asyncio
import json
import logging
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

from aiohttp import ClientResponse

from .event_manager import EventManager
from .interceptor_types import EventType
from .payload_context import PayloadContext


class ResponseStreamer:
    """
    Handles SSE streaming responses with proper event boundary preservation.

    Key responsibilities:
    - Buffer chunks until complete SSE events
    - Parse and validate SSE event structure
    - Forward properly formatted events to client
    - Handle both streaming and non-streaming responses

    The critical challenge this solves is SSE chunk fragmentation where
    upstream responses can be split at arbitrary byte boundaries:

    Input chunks:  ["event: content_bl", "ock_delta\ndata: {\"type\":", "\"content_block_delta\"}\n\n"]
    Output events: ["event: content_block_delta\ndata: {\"type\":\"content_block_delta\"}\n\n"]
    """

    def __init__(
        self,
        config: Dict[str, Any],
        shutdown_event: Optional[asyncio.Event] = None,
        event_manager: Optional[EventManager] = None,
    ):
        self.config = config
        self.shutdown_event = shutdown_event
        self.event_manager = event_manager
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.enable_processing = config.get("streaming", {}).get("enable_processing", True)
        self.buffer_size = config.get("streaming", {}).get("buffer_size", 8192)
        self.max_event_size = config.get("streaming", {}).get("max_event_size", 65536)

        # SSE event parsing regex
        self.sse_event_pattern = re.compile(
            r"^(?:event:\s*([^\n]*)\n)?(?:data:\s*([^\n]*)\n)*\n", re.MULTILINE
        )

    async def stream_response(
        self,
        upstream_response: ClientResponse,
        tool_interceptor,
        content_manager,
        hook_interceptor=None,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream response with SSE event processing pipeline.

        Args:
            upstream_response: Response from upstream API
            tool_interceptor: Tool call processor
            content_manager: Content filter/manager

        Yields:
            Processed SSE event chunks
        """
        if not self.enable_processing:
            # Pass-through mode for debugging
            async for chunk in upstream_response.content.iter_chunked(self.buffer_size):
                yield chunk
            return

        # Initialize event processor
        event_processor = SSEEventProcessor(
            tool_interceptor=tool_interceptor,
            content_manager=content_manager,
            logger=self.logger,
            hook_interceptor=hook_interceptor,
        )

        try:
            # Process streaming response with shutdown checking
            async for chunk in upstream_response.content.iter_chunked(self.buffer_size):
                # Check shutdown event before processing each chunk
                if self.shutdown_event and self.shutdown_event.is_set():
                    self.logger.info("Streaming interrupted by shutdown signal")
                    break

                processed_events = await event_processor.process_chunk(chunk)

                # Yield each complete processed event
                for event_bytes in processed_events:
                    # Check shutdown again before yielding
                    if self.shutdown_event and self.shutdown_event.is_set():
                        self.logger.info("Streaming interrupted by shutdown signal during yield")
                        return
                    yield event_bytes

        except TimeoutError as e:
            self.logger.info(f"Streaming timeout: {e}")
            # Send error event
            error_event = self._create_error_event("Stream timeout")
            yield error_event.encode("utf-8")
        except Exception as e:
            self.logger.error(f"Streaming error: {e}", exc_info=True)
            # Send error event
            error_event = self._create_error_event(str(e))
            yield error_event.encode("utf-8")

        finally:
            # Flush any remaining buffered content
            final_events = await event_processor.flush()
            for event_bytes in final_events:
                yield event_bytes

            # Emit RESPONSE_CLIENT event for response cleaning
            if self.event_manager:
                # For streaming responses, we don't have a single response_data object
                # but we can still emit the event for processors that need to do cleanup
                payload = PayloadContext(
                    response_data={"type": "stream_complete"}, metadata={"stream_finished": True}
                )
                await self.event_manager.emit_event(EventType.RESPONSE_CLIENT, payload)

    def _create_error_event(self, error_message: str) -> str:
        """Create a properly formatted SSE error event."""
        error_data = {"type": "error", "error": {"message": error_message, "type": "proxy_error"}}
        return f"event: error\ndata: {json.dumps(error_data)}\n\n"


class SSEEventProcessor:
    """
    Core SSE event processing with stateful chunk buffering.

    This class solves the fundamental SSE streaming challenge:
    - SSE events have specific boundaries (\\n\\n)
    - Upstream chunks can fragment events at any byte
    - Must reconstruct complete events before processing
    - Must maintain exact SSE protocol compliance
    """

    def __init__(self, tool_interceptor, content_manager, logger, hook_interceptor=None):
        self.tool_interceptor = tool_interceptor
        self.content_manager = content_manager
        self.logger = logger
        self.hook_interceptor = hook_interceptor

        # Stateful buffers
        self.text_buffer = ""
        self.event_queue = []

        # Statistics
        self.chunks_processed = 0
        self.events_processed = 0
        self.bytes_processed = 0

    async def process_chunk(self, raw_chunk: bytes) -> List[bytes]:
        """
        Process a raw chunk and return complete SSE events.

        Args:
            raw_chunk: Raw bytes from upstream response

        Returns:
            List of complete SSE event byte strings
        """
        try:
            # Decode chunk to text
            chunk_text = raw_chunk.decode("utf-8", errors="replace")
            self.text_buffer += chunk_text

            self.chunks_processed += 1
            self.bytes_processed += len(raw_chunk)

            # Extract complete SSE events
            complete_events = []

            while "\n\n" in self.text_buffer:
                # Find next event boundary
                event_end = self.text_buffer.find("\n\n") + 2
                event_text = self.text_buffer[:event_end]
                self.text_buffer = self.text_buffer[event_end:]

                # Process the complete event
                if event_text.strip():
                    processed_event = await self._process_complete_event(event_text)
                    if processed_event:
                        complete_events.append(processed_event.encode("utf-8"))
                        self.events_processed += 1

                        # Check for mid-stream hook injection after each event
                        injected_events = await self._check_midstream_hooks(event_text)
                        for injected_event in injected_events:
                            complete_events.append(injected_event.encode("utf-8"))

            return complete_events

        except Exception as e:
            self.logger.error(f"Chunk processing error: {e}", exc_info=True)
            # Return original chunk on error to maintain stream
            return [raw_chunk]

    async def _process_complete_event(self, event_text: str) -> Optional[str]:
        """
        Process a complete SSE event through the interception pipeline.

        Args:
            event_text: Complete SSE event text

        Returns:
            Processed SSE event text or None to skip
        """
        try:
            # Parse SSE event structure
            event_type, event_data = self._parse_sse_event(event_text)

            if not event_data:
                # Pass through events without data unchanged
                return event_text

            # Process based on event type
            if event_type == "content_block_delta":
                return await self._process_content_delta(event_text, event_data)

            elif event_type == "content_block_start":
                return await self._process_content_start(event_text, event_data)

            elif event_type == "tool_use":
                return await self._process_tool_use(event_text, event_data)

            elif event_type == "message_start":
                return await self._process_message_start(event_text, event_data)

            elif event_type == "message_delta":
                return await self._process_message_delta(event_text, event_data)

            elif event_type == "message_stop":
                return await self._process_message_stop(event_text, event_data)

            else:
                # Pass through unknown event types unchanged
                self.logger.debug(f"Unknown event type: {event_type}")
                return event_text

        except Exception as e:
            self.logger.error(f"Event processing error: {e}", exc_info=True)
            # Return original event on error
            return event_text

    def _parse_sse_event(self, event_text: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Parse SSE event into type and JSON data.

        Args:
            event_text: Raw SSE event text

        Returns:
            Tuple of (event_type, parsed_data)
        """
        try:
            lines = event_text.strip().split("\n")
            event_type = None
            data_lines = []

            for line in lines:
                if line.startswith("event:"):
                    event_type = line[6:].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[5:].strip())

            if not data_lines:
                return event_type, None

            # Join multiple data lines and parse JSON
            data_json = "\n".join(data_lines)
            if data_json:
                parsed_data = json.loads(data_json)
                return event_type, parsed_data
            else:
                return event_type, None

        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON parse error in SSE event: {e}")
            return event_type, None
        except Exception as e:
            self.logger.error(f"SSE event parse error: {e}", exc_info=True)
            return None, None

    async def _process_content_delta(self, event_text: str, event_data: Dict[str, Any]) -> str:
        """
        Process content_block_delta events through content manager.

        These events contain streaming text content that may need filtering.
        """
        try:
            # Extract text content
            delta = event_data.get("delta", {})
            text_content = delta.get("text", "")

            if text_content:
                # Apply content filtering
                filtered_content = await self.content_manager.filter_response_content(text_content)

                # Rebuild event if content changed
                if filtered_content != text_content:
                    modified_data = event_data.copy()
                    modified_data["delta"]["text"] = filtered_content
                    return self._rebuild_sse_event("content_block_delta", modified_data)

            # Return original if no changes
            return event_text

        except Exception as e:
            self.logger.error(f"Content delta processing error: {e}", exc_info=True)
            return event_text

    async def _process_content_start(self, event_text: str, event_data: Dict[str, Any]) -> str:
        """Process content_block_start events."""
        # Usually no processing needed for start events
        return event_text

    async def _process_tool_use(self, event_text: str, event_data: Dict[str, Any]) -> Optional[str]:
        """
        Process tool_use events through tool interceptor.

        This enables tool call logging and optional blocking.
        """
        try:
            # Extract tool call information
            tool_name = event_data.get("name", "")
            tool_input = event_data.get("input", {})
            tool_id = event_data.get("id", "")

            # Log tool call
            await self.tool_interceptor.log_tool_call(
                {
                    "id": tool_id,
                    "name": tool_name,
                    "input": tool_input,
                    "timestamp": self._get_timestamp(),
                }
            )

            # Check if tool should be blocked
            should_block = await self.tool_interceptor.should_block_tool(tool_name, tool_input)

            if should_block:
                self.logger.warning(f"Blocking tool call: {tool_name}")
                # Return None to skip this event (effectively blocking the tool)
                return None

            # Allow tool call through
            return event_text

        except Exception as e:
            self.logger.error(f"Tool use processing error: {e}", exc_info=True)
            return event_text

    async def _process_message_start(self, event_text: str, event_data: Dict[str, Any]) -> str:
        """Process message_start events."""
        return event_text

    async def _process_message_delta(self, event_text: str, event_data: Dict[str, Any]) -> str:
        """Process message_delta events."""
        return event_text

    async def _process_message_stop(self, event_text: str, event_data: Dict[str, Any]) -> str:
        """Process message_stop events."""
        return event_text

    def _rebuild_sse_event(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """
        Rebuild SSE event from type and data.

        Args:
            event_type: SSE event type
            event_data: Event data dictionary

        Returns:
            Properly formatted SSE event string
        """
        data_json = json.dumps(event_data, separators=(",", ":"))
        return f"event: {event_type}\ndata: {data_json}\n\n"

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging."""
        from datetime import datetime

        return datetime.now().isoformat()

    async def flush(self) -> List[bytes]:
        """
        Flush any remaining buffered content as final events.

        Called when the stream ends to handle incomplete events.

        Returns:
            List of final event bytes
        """
        final_events = []

        if self.text_buffer.strip():
            # Log incomplete buffer for debugging
            self.logger.debug(f"Flushing incomplete buffer: {repr(self.text_buffer[:100])}")

            # Try to process as incomplete event
            if self.text_buffer.startswith("event:") or self.text_buffer.startswith("data:"):
                # Add missing event terminator
                complete_event = self.text_buffer + "\n\n"
                processed = await self._process_complete_event(complete_event)
                if processed:
                    final_events.append(processed.encode("utf-8"))

        # Log processing statistics
        self.logger.info(
            f"Stream processing complete: {self.chunks_processed} chunks, "
            f"{self.events_processed} events, {self.bytes_processed} bytes"
        )

        return final_events

    async def _check_midstream_hooks(self, event_text: str) -> List[str]:
        """
        Check if any hooks want to inject events mid-stream.

        Args:
            event_text: The current SSE event that was just processed

        Returns:
            List of additional SSE events to inject
        """
        injected_events = []

        if not self.hook_interceptor:
            return injected_events

        try:
            # Parse the current event to understand context
            event_type, event_data = self._parse_sse_event(event_text)

            # Check if any hooks want to inject based on this event
            # This is a simplified example - could be expanded with more sophisticated triggers
            if event_type == "content_block_delta":
                # Example: hook could inject notification events during content streaming
                # For now, this is a placeholder for future hook expansion
                pass

        except Exception as e:
            self.logger.error(f"Error checking mid-stream hooks: {e}", exc_info=True)

        return injected_events
