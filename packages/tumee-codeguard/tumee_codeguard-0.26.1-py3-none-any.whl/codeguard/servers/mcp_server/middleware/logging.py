"""
Request logging middleware for MCP server.

This module provides ASGI middleware for detailed logging of MCP message requests
with debug-level controls and graceful error handling.
"""

import asyncio
import json
import logging
from datetime import datetime


class RequestLoggingMiddleware:
    """ASGI middleware to log detailed message content for /messages requests"""

    def __init__(self, app, shutdown_event=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.shutdown_event = shutdown_event

    async def __call__(self, scope, receive, send):
        try:
            # Only do detailed logging for /messages/ if we're in debug mode
            if scope["type"] == "http" and scope["path"].endswith("/messages/"):
                # If not in debug mode, just pass through
                if not self.logger.isEnabledFor(logging.DEBUG):
                    return await self.app(scope, receive, send)

                # Debug mode: capture and log detailed request information
                body_parts = []
                messages = []

                async def capture_receive():
                    while True:
                        try:
                            message = await receive()
                            messages.append(message)
                            if message["type"] == "http.request" and "body" in message:
                                body_parts.append(message["body"])
                                if not message.get("more_body", False):
                                    break
                            elif message["type"] == "http.disconnect":
                                break
                        except (asyncio.CancelledError, ConnectionError):
                            # Client disconnected, return disconnect message
                            return {"type": "http.disconnect"}
                    return message

                # Capture all messages first
                try:
                    await capture_receive()
                except (asyncio.CancelledError, ConnectionError):
                    # Client disconnected during capture, pass through to app
                    return await self.app(scope, receive, send)
                except Exception:
                    # If capture fails, continue without logging
                    return await self.app(scope, receive, send)

                # Create a new receive function that replays the captured messages
                message_iter = iter(messages)

                async def replay_receive():
                    try:
                        return next(message_iter)
                    except StopIteration:
                        # This shouldn't happen in normal operation
                        return {"type": "http.disconnect"}

                # Log the request (only in debug mode)
                try:
                    await self._log_request(scope, body_parts)
                except (asyncio.CancelledError, ConnectionError):
                    # Ignore cancellation and connection errors during shutdown
                    pass
                except Exception as e:
                    self.logger.debug(f"Logging error: {e}")

                # Continue with the app using the replayed messages
                try:
                    return await self.app(scope, replay_receive, send)
                except (asyncio.CancelledError, KeyboardInterrupt):
                    # Graceful shutdown - don't log as error
                    return
                except Exception as e:
                    # Suppress client disconnect errors to reduce noise
                    error_msg = str(e).lower()
                    if any(
                        term in error_msg
                        for term in [
                            "client",
                            "disconnect",
                            "connection",
                            "broken pipe",
                            "reset",
                            "http.response",
                        ]
                    ):
                        # Log at debug level only
                        self.logger.debug(f"Client connection error (suppressed): {e}")
                        return
                    else:
                        # Re-raise other errors
                        raise
            else:
                return await self.app(scope, receive, send)
        except RuntimeError as e:
            # Handle various ASGI/MCP errors specifically
            error_msg = str(e).lower()
            if "received request before initialization was complete" in error_msg:
                self.logger.debug(
                    "Client disconnected before MCP initialization completed (expected)"
                )
                return
            elif (
                "unexpected asgi message" in error_msg
                and "after response already completed" in error_msg
            ):
                self.logger.debug("Client disconnected after response completed (expected)")
                return
            elif "http.response" in error_msg and (
                "completed" in error_msg or "already" in error_msg
            ):
                self.logger.debug("ASGI response error due to client disconnect (expected)")
                return
            elif "expected asgi message" in error_msg and "http.response.body" in error_msg:
                # Only suppress if we're actually shutting down
                if self.shutdown_event and self.shutdown_event.is_set():
                    self.logger.debug("ASGI response flow error during shutdown (expected)")
                    return
                else:
                    raise
            elif "asgi callable returned without completing response" in error_msg:
                # Only suppress if we're actually shutting down
                if self.shutdown_event and self.shutdown_event.is_set():
                    self.logger.debug("ASGI incomplete response during shutdown (expected)")
                    return
                else:
                    raise
            else:
                raise
        except ExceptionGroup as eg:
            # Handle nested exception groups from MCP/SSE disconnects
            mcp_disconnect_patterns = [
                "received request before initialization was complete",
                "client disconnected",
                "connection closed",
                "sse connection closed",
                "task group cancelled",
                "unhandled errors in a taskgroup",
            ]

            # Check if all exceptions are disconnect-related
            is_expected_disconnect = all(
                any(pattern in str(exc).lower() for pattern in mcp_disconnect_patterns)
                for exc in eg.exceptions
            )

            if is_expected_disconnect:
                self.logger.debug(
                    f"Expected client disconnect during SSE handshake: {len(eg.exceptions)} exceptions"
                )
                return
            else:
                # Re-raise if there are unexpected exceptions
                raise
        except (asyncio.CancelledError, KeyboardInterrupt):
            # Graceful shutdown - don't log as error
            return
        except Exception as e:
            # Suppress common shutdown-related errors
            error_msg = str(e).lower()
            suppression_patterns = [
                "client",
                "disconnect",
                "connection",
                "broken pipe",
                "reset",
                "http.response",
                "asgi",
                # Add MCP-specific patterns
                "received request before initialization",
                "sse connection",
                "task group",
                "cancelled",
                "unhandled errors in a taskgroup",
            ]

            if any(pattern in error_msg for pattern in suppression_patterns):
                self.logger.debug(f"Connection error during shutdown (suppressed): {e}")
                return
            else:
                raise

    async def _log_request(self, scope, body_parts):
        """Log detailed request information"""
        try:
            # Get client information
            client = scope.get("client", ("unknown", "unknown"))
            client_host, client_port = client[0], client[1]

            # Get session ID from query string
            query_string = scope.get("query_string", b"").decode()
            session_id = "unknown"
            if "session_id=" in query_string:
                for param in query_string.split("&"):
                    if param.startswith("session_id="):
                        session_id = param.split("=", 1)[1]
                        break

            # Combine body parts (already captured)
            body = b"".join(body_parts)

            print(f"\n📨 MCP MESSAGE REQUEST:")
            print(f"   Timestamp: {datetime.now().isoformat()}")
            print(f"   Client: {client_host}:{client_port}")
            print(f"   Session ID: {session_id}")

            # Log HTTP headers only in debug mode
            if self.logger.isEnabledFor(logging.DEBUG):
                headers = scope.get("headers", [])
                print(f"   Headers:")
                for name, value in headers:
                    print(f"     {name.decode()}: {value.decode()}")

            # Log raw body
            print(f"   Body (raw): {body.decode('utf-8', errors='replace')}")

            if body:
                try:
                    body_str = body.decode("utf-8")

                    # Parse multiple JSON objects from the body
                    messages = []
                    decoder = json.JSONDecoder()
                    idx = 0
                    while idx < len(body_str):
                        remaining = body_str[idx:].lstrip()
                        if not remaining:
                            break
                        try:
                            obj, end_idx = decoder.raw_decode(remaining)
                            messages.append(obj)
                            idx += len(body_str[idx:]) - len(remaining) + end_idx
                        except json.JSONDecodeError:
                            break

                    # Log each message
                    if messages:
                        print(f"   Messages Found: {len(messages)}")
                        for i, message_data in enumerate(messages):
                            if len(messages) > 1:
                                print(f"   Message {i+1}:")
                                prefix = "     "
                            else:
                                prefix = "   "

                            print(f"{prefix}Type: {message_data.get('method', 'unknown')}")

                            # Log message details based on type
                            if "params" in message_data:
                                params = message_data["params"]
                                print(f"{prefix}Parameters:")
                                for key, value in params.items():
                                    if isinstance(value, str) and len(value) > 100:
                                        print(f"{prefix}  {key}: {value[:100]}... (truncated)")
                                    elif isinstance(value, (dict, list)):
                                        print(f"{prefix}  {key}: {json.dumps(value, indent=2)}")
                                    else:
                                        print(f"{prefix}  {key}: {value}")

                            if "id" in message_data:
                                print(f"{prefix}ID: {message_data['id']}")
                    else:
                        print(f"   No valid JSON messages found")

                except Exception as e:
                    print(f"   JSON Parse Error: {e}")

            print("   " + "=" * 60)

        except (asyncio.CancelledError, ConnectionError):
            # Suppress during shutdown
            pass
        except Exception as e:
            print(f"\n❌ Error logging message request: {e}")
            print("   " + "=" * 60)
