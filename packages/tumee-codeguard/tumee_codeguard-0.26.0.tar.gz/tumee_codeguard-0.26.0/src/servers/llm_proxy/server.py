"""
Main aiohttp server for LLM proxy with SSL support and route handling.
"""

import asyncio
import json
import logging
import ssl
import time
import weakref
from typing import Dict, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout, web
from aiohttp.client_exceptions import ClientConnectionResetError
from aiohttp.web_request import Request
from aiohttp.web_response import Response, StreamResponse

from .content_manager import ContentManager
from .event_manager import EventManager
from .interceptor_types import EventType
from .request_interceptor import RequestInterceptor
from .response_streamer import ResponseStreamer
from .streamable_response import StreamableResponseHandler
from .tool_interceptor import ToolInterceptor
from .upstream_client import UpstreamClient


class LLMProxyServer:
    """
    Main aiohttp-based LLM proxy server.

    Provides transparent interception of LLM API requests with:
    - SSL/TLS termination
    - Request/response modification
    - SSE streaming support
    - Tool call interception
    """

    def __init__(self, config: dict, shutdown_event: Optional[asyncio.Event] = None):
        self.config = config
        self.shutdown_event = shutdown_event
        self.logger = logging.getLogger(__name__)

        # Track active SSE connections for proper shutdown
        self.active_sse_connections = weakref.WeakSet()

        # Model prefix to provider mapping for dynamic routing
        self.model_routing = {
            "claude-*": "anthropic",
            "gpt-*": "openai",
            "text-davinci*": "openai",
            "text-curie*": "openai",
            "text-babbage*": "openai",
            "text-ada*": "openai",
            "gemini-*": "google",
            "mistral-*": "mistral",
            "llama*": "huggingface",
            "bert*": "huggingface",
            "*-instruct": "huggingface",
        }

        # Initialize event manager first
        self.event_manager = EventManager()

        # Initialize components with shutdown event and event manager
        self.request_interceptor = RequestInterceptor(config, self.event_manager)
        self.response_streamer = ResponseStreamer(config, shutdown_event, self.event_manager)
        self.streamable_handler = StreamableResponseHandler(config)
        self.upstream_client = UpstreamClient(config)
        self.content_manager = ContentManager(config)
        self.tool_interceptor = ToolInterceptor(config, self.event_manager)

        # Register built-in processors
        self._register_built_in_processors()

        # Discover and register chat commands
        self._discover_chat_commands()

        # Create aiohttp application
        self.app = web.Application()
        self._setup_routes()
        self._setup_middleware()
        self._setup_shutdown_handler()

    def _register_built_in_processors(self):
        """Register built-in payload processors with the event manager."""
        try:
            from .processors import get_built_in_processors

            built_in_processors = get_built_in_processors()

            for name, processor_class in built_in_processors.items():
                try:
                    # Create processor instance with default config
                    processor = processor_class()

                    # Register for appropriate events based on processor type
                    if name == "urgent_notes":
                        events = [EventType.REQUEST_RECEIVED, EventType.RESPONSE_CLIENT]
                    elif name == "hook_interceptor":
                        events = [EventType.REQUEST_RECEIVED]

                        # Hook interceptor will automatically receive hooks from global registry
                    else:
                        # Default to request events for unknown processors
                        events = [EventType.REQUEST_RECEIVED]

                    self.event_manager.register_processor(name, processor, events)
                    self.logger.info(f"Registered built-in processor: {name}")

                except Exception as e:
                    self.logger.error(f"Failed to register processor {name}: {e}", exc_info=True)

        except Exception as e:
            self.logger.error(f"Failed to load built-in processors: {e}", exc_info=True)

    def _discover_chat_commands(self) -> None:
        """Discover and register chat commands using the decorator system."""
        try:
            from ...shared.chat.discovery import ensure_commands_discovered

            ensure_commands_discovered()
            self.logger.info("Chat command discovery completed")
        except Exception as e:
            self.logger.error(f"Failed to discover chat commands: {e}", exc_info=True)

    def _match_wildcard_pattern(self, pattern: str, text: str) -> bool:
        """
        Match wildcard pattern against text. Supports * as wildcard.

        Args:
            pattern: Pattern with * wildcards (e.g., "claude-*", "*-instruct", "a*b")
            text: Text to match against

        Returns:
            True if pattern matches text
        """
        import re

        # Convert wildcard pattern to regex
        # Escape special regex chars except *
        escaped = re.escape(pattern)
        # Replace escaped \* with regex .*
        regex_pattern = escaped.replace(r"\*", ".*")
        # Anchor the pattern to match full string
        regex_pattern = f"^{regex_pattern}$"
        return bool(re.match(regex_pattern, text, re.IGNORECASE))

    def _detect_provider_from_model(self, model: str) -> str:
        """
        Detect provider from model name using wildcard patterns.

        Args:
            model: Model name

        Returns:
            Provider name (defaults to "openai" if no match)
        """
        for pattern, provider in self.model_routing.items():
            if self._match_wildcard_pattern(pattern, model):
                return provider

        # Default fallback
        return "openai"

    def _setup_routes(self):
        """Configure HTTP routes for the proxy server."""
        self.app.router.add_post("/v1/messages", self.handle_streamable_request)
        self.app.router.add_post("/v1/chat/completions", self.handle_streamable_request)
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_get("/status", self.status_check)
        self.app.router.add_get("/connections", self.connection_stats)
        self.app.router.add_post("/connections/reset", self.reset_connections)

        # Catch-all for other API endpoints
        self.app.router.add_route("*", "/{path:.*}", self.handle_passthrough)

    def _setup_middleware(self):
        """Configure middleware for logging and error handling."""
        self.app.middlewares.append(self._error_middleware)
        self.app.middlewares.append(self._logging_middleware)

    def _setup_shutdown_handler(self):
        """Configure shutdown handler for graceful SSE connection closure."""
        self.app.on_shutdown.append(self._shutdown_sse_connections)

    @web.middleware
    async def _error_middleware(self, request: Request, handler):
        """Handle errors gracefully with fallback to passthrough."""
        try:
            return await handler(request)
        except web.HTTPNotFound:
            # Don't log 404s as errors - they're expected for unknown routes
            self.logger.debug(f"404 Not Found: {request.method} {request.path}")
            # Fallback to direct passthrough for unknown routes
            return await self._passthrough_request(request)
        except Exception as e:
            self.logger.error(f"Proxy error: {e}", exc_info=True)
            # Fallback to direct passthrough
            return await self._passthrough_request(request)

    @web.middleware
    async def _logging_middleware(self, request: Request, handler):
        """Log requests for debugging and monitoring."""
        # Only log important endpoints to reduce noise
        if request.path.startswith(("/v1/", "/health", "/status", "/connections")):
            self.logger.debug(f"{request.method} {request.path} from {request.remote}")
        response = await handler(request)
        # Only log response status for errors or important endpoints
        if response.status >= 400 or request.path.startswith(
            ("/v1/", "/health", "/status", "/connections")
        ):
            self.logger.debug(f"Response {response.status} for {request.path}")
        return response

    async def _shutdown_sse_connections(self, app):
        """Gracefully close all active SSE connections during shutdown."""
        self.logger.info("Closing active SSE connections for graceful shutdown...")

        # Get a copy of the connections to avoid modification during iteration
        connections_to_close = list(self.active_sse_connections)

        for connection in connections_to_close:
            try:
                # Send a final close event to the client
                close_event = 'event: close\ndata: {"type": "server_shutdown"}\n\n'
                await connection.write(close_event.encode())

                # Properly end the SSE stream
                await connection.write_eof()
                self.logger.debug("Closed SSE connection")

            except Exception as e:
                # Ignore errors when closing connections (client may have already disconnected)
                self.logger.debug(f"Error closing SSE connection: {e}")

        self.logger.info(f"Closed {len(connections_to_close)} SSE connections")

    async def handle_streamable_request(self, request: Request) -> StreamResponse:
        """
        Unified handler for all LLM API requests with streamable HTTP support.

        This handler implements the streamable HTTP pattern:
        1. Start as uncommitted StreamResponse
        2. Process through hook system
        3. Dynamically choose response type (JSON/SSE) based on hooks and request
        4. Support for Anthropic and OpenAI endpoints
        """
        try:
            # Check content type
            content_type_raw = request.headers.get("content-type", "")
            if isinstance(content_type_raw, bytes):
                content_type = content_type_raw.decode("utf-8", errors="ignore").lower()
            else:
                content_type = str(content_type_raw).lower()

            if "application/json" not in content_type:
                # Non-JSON request - use passthrough
                self.logger.info(
                    f"Non-JSON request with content-type: {content_type}, using passthrough"
                )
                return await self._passthrough_request(request)

            # Parse JSON request
            try:
                request_data = await request.json()
            except Exception as json_error:
                self.logger.error(f"JSON parsing error: {json_error}, using passthrough")
                return await self._passthrough_request(request)

            # Validate model parameter
            model = request_data.get("model", "")
            if not model:
                return web.json_response(
                    {
                        "error": {
                            "type": "invalid_request",
                            "message": "Model parameter is required",
                        }
                    },
                    status=400,
                )

            # Detect provider and process request
            provider = self._detect_provider_from_model(model)

            # Handle different endpoint formats
            if request.path == "/v1/chat/completions":
                # Convert OpenAI format to Anthropic format if needed
                modified_request = await self.request_interceptor.process_openai_request(
                    request_data
                )
            else:
                # Standard Anthropic messages endpoint
                modified_request = await self.request_interceptor.process_request(
                    request_data, provider
                )

            # Extract hook results
            hook_action = modified_request.get("_hook_action")
            hook_response = modified_request.get("_hook_response")
            hook_sse_events = modified_request.get("_hook_sse_events")

            # Handle hook results using streamable response handler
            if hook_action in ("block", "respond_json", "respond_stream", "respond_hybrid"):
                self.logger.info(f"Hook intercepted request with action: {hook_action}")

                # Clean hook metadata from request
                for key in ["_hook_action", "_hook_response", "_hook_sse_events", "_hook_message"]:
                    modified_request.pop(key, None)

                # Create appropriate hook result for streamable handler
                from .processors.hook_types import HookResult

                hook_result = HookResult(
                    action=hook_action, response_data=hook_response, sse_events=hook_sse_events
                )

                return await self.streamable_handler.handle_hook_result(
                    hook_result, request, request_data, provider
                )

            elif hook_action == "modify":
                # Clean metadata and continue with modified request
                modified_request.pop("_hook_action", None)
                modified_request.pop("_hook_message", None)
                self.logger.info("Request modified by hook, forwarding to LLM")

            elif hook_action == "continue":
                # Clean metadata and continue normally
                modified_request.pop("_hook_action", None)
                modified_request.pop("_hook_message", None)
                self.logger.info("Request continued by hook, forwarding to LLM")

            # Forward to upstream API
            upstream_url = self._get_upstream_url_for_endpoint(request.path, model)
            upstream_response = await self.upstream_client.send_request(
                url=upstream_url,
                data=modified_request,
                headers=dict(request.headers),
            )

            # Handle streaming vs non-streaming responses
            if modified_request.get("stream", False):
                return await self._handle_streaming_response(upstream_response, request)
            else:
                return await self._handle_non_streaming_response(upstream_response, request)

        except ClientConnectionResetError as e:
            self.logger.info(f"Client disconnected during streamable request: {e}")
            return await self._passthrough_request(request)
        except Exception as e:
            self.logger.error(
                f"Error in streamable request handler: {e}, using passthrough", exc_info=True
            )
            return await self._passthrough_request(request)

    def _get_upstream_url_for_endpoint(self, endpoint_path: str, model: str) -> str:
        """Get upstream URL based on endpoint path and model."""
        if endpoint_path == "/v1/chat/completions":
            # OpenAI-style endpoint
            provider = self._detect_provider_from_model(model)
            if provider == "anthropic":
                return f"{self.config['upstream']['anthropic']['base_url']}/v1/messages"
            else:
                return f"{self.config['upstream'].get(provider, self.config['upstream']['openai'])['base_url']}/v1/chat/completions"
        else:
            # Anthropic messages endpoint
            return f"{self.config['upstream']['anthropic']['base_url']}/v1/messages"

    async def _handle_streaming_response(
        self, upstream_response, original_request: Request
    ) -> StreamResponse:
        """
        Handle SSE streaming responses with proper event boundary preservation.
        """
        # Create streaming response with proper SSE headers
        response = StreamResponse(
            status=upstream_response.status,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "Transfer-Encoding": "chunked",  # Ensure chunked encoding
            },
        )

        await response.prepare(original_request)

        # Track this SSE connection for proper shutdown
        self.active_sse_connections.add(response)

        try:
            # Stream response through our processing pipeline with shutdown checking
            # Get hook interceptor for mid-stream injection
            hook_interceptor = None
            for name, processor in self.event_manager.get_registered_processors().items():
                if hasattr(processor, "register_hook"):
                    hook_interceptor = processor
                    break

            async for processed_chunk in self.response_streamer.stream_response(
                upstream_response, self.tool_interceptor, self.content_manager, hook_interceptor
            ):
                # Check shutdown event before writing each chunk
                if self.shutdown_event and self.shutdown_event.is_set():
                    self.logger.info("Server streaming interrupted by shutdown signal")
                    # Send a final event to close the connection properly
                    try:
                        final_event = 'event: close\ndata: {"type": "connection_closing"}\n\n'
                        await response.write(final_event.encode())
                    except Exception:
                        pass  # Ignore errors when closing
                    break

                # Ensure chunk is written immediately
                await response.write(processed_chunk)
                # Force flush to client (important for real-time streaming)
                if hasattr(response, "drain"):
                    await response.drain()

        except aiohttp.ClientConnectionResetError as e:
            self.logger.info(f"Client disconnected during streaming: {e}")
        except Exception as e:
            self.logger.error(f"Streaming error: {e}", exc_info=True)
            # Send error event and close
            try:
                error_event = f'event: error\ndata: {{"error": "Proxy streaming error"}}\n\n'
                await response.write(error_event.encode())
            except ClientConnectionResetError:
                self.logger.info("Client disconnected while sending error event")

        finally:
            # Always remove connection from tracking when done
            self.active_sse_connections.discard(response)
            try:
                await response.write_eof()
            except ClientConnectionResetError:
                # Expected when client disconnects
                pass

        return response

    async def _handle_non_streaming_response(
        self, upstream_response, original_request: Request
    ) -> Response:
        """
        Handle non-streaming JSON responses.
        """
        response_data = await upstream_response.json()

        # Process response through content manager
        processed_data = await self.content_manager.process_response(response_data)

        return web.json_response(
            processed_data,
            status=upstream_response.status,
            headers={"Access-Control-Allow-Origin": "*"},
        )

    async def _handle_local_streaming_response(
        self, sse_events: list, original_request: Request
    ) -> StreamResponse:
        """
        Handle streaming responses for locally generated content (e.g., urgent commands).

        Args:
            sse_events: List of SSE event strings to stream
            original_request: Original client request

        Returns:
            StreamResponse with proper SSE formatting
        """
        # Create streaming response with proper SSE headers
        response = StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "Transfer-Encoding": "chunked",  # Ensure chunked encoding
            },
        )

        await response.prepare(original_request)

        # Track this SSE connection for proper shutdown
        self.active_sse_connections.add(response)

        try:
            # Stream each SSE event
            for event_str in sse_events:
                # Check shutdown event before writing each chunk
                if self.shutdown_event and self.shutdown_event.is_set():
                    self.logger.info("Local streaming interrupted by shutdown signal")
                    break

                # Write SSE event
                await response.write(event_str.encode())

                # Force flush to client (important for real-time streaming)
                if hasattr(response, "drain"):
                    await response.drain()

        except aiohttp.ClientConnectionResetError as e:
            self.logger.info(f"Client disconnected during local streaming: {e}")
        except Exception as e:
            self.logger.error(f"Local streaming error: {e}", exc_info=True)
        finally:
            # Remove from active connections
            try:
                self.active_sse_connections.discard(response)
            except Exception:
                pass  # Ignore errors when cleaning up

        return response

    async def handle_passthrough(self, request: Request) -> StreamResponse:
        """
        Handle unknown endpoints with direct passthrough.
        """
        self.logger.info(f"Passthrough: {request.method} {request.path}")
        return await self._passthrough_request(request)

    async def _passthrough_request(self, request: Request) -> StreamResponse:
        """
        Pass request directly to upstream without modification.

        Used as fallback when interception fails.
        """
        try:
            # Passthrough request directly to upstream
            request_body = await request.read()
            upstream_url = self._get_upstream_url_from_request(request)

            # Forward request directly
            upstream_response = await self.upstream_client.send_raw_request(
                method=request.method,
                url=f"{upstream_url}{request.path_qs}",
                data=request_body,
                headers=dict(request.headers),
            )

            # Create response with same status and filtered headers
            # Filter headers to remove compression headers since aiohttp auto-decompresses
            filtered_headers = self._filter_response_headers(dict(upstream_response.headers))
            response = StreamResponse(status=upstream_response.status, headers=filtered_headers)

            await response.prepare(request)

            # Stream response data
            async for chunk in upstream_response.content.iter_chunked(8192):
                await response.write(chunk)

            await response.write_eof()
            return response

        except ClientConnectionResetError as e:
            # Expected error when client disconnects during response - just log at info level
            self.logger.info(f"Client disconnected during passthrough: {e}")
            return web.Response(text="Client disconnected", status=499)
        except Exception as e:
            self.logger.error(f"Passthrough error: {e}", exc_info=True)
            return web.Response(text=f"Proxy error: {str(e)}", status=500)

    def _filter_response_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Filter response headers to remove compression headers when aiohttp auto-decompresses.

        aiohttp automatically decompresses gzipped responses when reading them,
        but leaves the Content-Encoding header intact. This causes a mismatch
        where clients receive 'Content-Encoding: gzip' but uncompressed content.

        Args:
            headers: Original response headers from upstream

        Returns:
            Filtered headers with compression headers removed
        """
        filtered_headers = dict(headers)

        # Remove compression-related headers since aiohttp auto-decompresses
        compression_headers = {
            "content-encoding",
            "content-length",  # Length changes after decompression
        }

        for header in list(filtered_headers.keys()):
            if header.lower() in compression_headers:
                del filtered_headers[header]
                self.logger.debug(f"Removed {header} header (content auto-decompressed)")

        return filtered_headers

    def _get_upstream_url(self, model: str) -> str:
        """Determine upstream API URL based on model."""
        if "claude" in model.lower():
            return self.config["upstream"]["anthropic"]["base_url"]
        elif "gpt" in model.lower() or "openai" in model.lower():
            return self.config["upstream"]["openai"]["base_url"]
        else:
            # Default to Anthropic
            return self.config["upstream"]["anthropic"]["base_url"]

    def _get_upstream_url_from_request(self, request: Request) -> str:
        """Determine upstream URL from request path and headers."""
        # Simple heuristic - can be improved based on routing rules
        if "anthropic" in request.headers.get("user-agent", "").lower():
            return self.config["upstream"]["anthropic"]["base_url"]
        elif "openai" in request.headers.get("user-agent", "").lower():
            return self.config["upstream"]["openai"]["base_url"]
        else:
            return self.config["upstream"]["anthropic"]["base_url"]

    async def health_check(self, request: Request) -> Response:
        """Basic health check endpoint."""
        return web.json_response({"status": "healthy", "service": "llm-proxy", "version": "1.0.0"})

    async def status_check(self, request: Request) -> Response:
        """Detailed status check with component health."""
        status = {
            "server": "running",
            "components": {
                "request_interceptor": "ready",
                "response_streamer": "ready",
                "upstream_client": "ready",
                "content_manager": "ready",
                "tool_interceptor": "ready",
            },
            "upstreams": {},
        }

        # Check upstream connectivity
        try:
            anthropic_healthy = await self.upstream_client.health_check(
                self.config["upstream"]["anthropic"]["base_url"]
            )
            status["upstreams"]["anthropic"] = "healthy" if anthropic_healthy else "unhealthy"
        except Exception:
            status["upstreams"]["anthropic"] = "error"

        return web.json_response(status)

    async def connection_stats(self, request: Request) -> Response:
        """Detailed connection pool and circuit breaker statistics."""
        try:
            stats = self.upstream_client.get_connection_stats()

            # Add SSE connection tracking info
            stats["sse_connections"] = {
                "active_count": len(self.active_sse_connections),
            }

            # Add current timestamp for monitoring
            stats["timestamp"] = time.time()

            return web.json_response(stats)
        except Exception as e:
            self.logger.error(f"Error getting connection stats: {e}", exc_info=True)
            return web.json_response({"error": str(e)}, status=500)

    async def reset_connections(self, request: Request) -> Response:
        """Reset connection pool and circuit breaker state."""
        try:
            # Force session renewal
            self.upstream_client.force_session_renewal()

            # Reset adaptive timeout
            self.upstream_client.reset_adaptive_timeout()

            # Reset circuit breaker state (if accessible)
            if hasattr(self.upstream_client, "_connection_errors"):
                self.upstream_client._connection_errors = 0
                self.upstream_client._circuit_breaker_open = False
                self.upstream_client._circuit_breaker_open_time = 0

            self.logger.info("Connection pool and circuit breaker state reset via API")

            return web.json_response(
                {
                    "status": "success",
                    "message": "Connection pool reset, session renewal scheduled",
                    "timestamp": time.time(),
                }
            )
        except Exception as e:
            self.logger.error(f"Error resetting connections: {e}", exc_info=True)
            return web.json_response({"error": str(e)}, status=500)

    async def start_server(
        self,
        host: str = "localhost",
        port: int = 8080,
        ssl_context: Optional[ssl.SSLContext] = None,
    ):
        """
        Start the aiohttp server.

        Args:
            host: Server host address
            port: Server port
            ssl_context: SSL context for HTTPS (optional)
        """
        self.logger.info(f"Starting LLM proxy server on {host}:{port}")

        # Create and start the server with graceful shutdown timeout
        runner = web.AppRunner(self.app, handle_signals=False)
        await runner.setup()

        site = web.TCPSite(
            runner, host=host, port=port, ssl_context=ssl_context, shutdown_timeout=2.0
        )

        await site.start()
        self.logger.info(f"LLM proxy server started on {host}:{port}")

        return runner

    async def cleanup(self):
        """Cleanup server resources."""
        await self.upstream_client.cleanup()
        self.logger.info("LLM proxy server cleaned up")


def create_ssl_context(cert_file: str, key_file: str) -> ssl.SSLContext:
    """
    Create SSL context for HTTPS server.

    Args:
        cert_file: Path to SSL certificate file
        key_file: Path to SSL private key file

    Returns:
        Configured SSL context
    """
    from pathlib import Path

    # Expand ~ and resolve paths
    cert_path = Path(cert_file).expanduser().resolve()
    key_path = Path(key_file).expanduser().resolve()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(str(cert_path), str(key_path))
    return ssl_context
