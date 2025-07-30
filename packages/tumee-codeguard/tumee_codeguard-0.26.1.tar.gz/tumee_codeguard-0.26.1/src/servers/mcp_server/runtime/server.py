"""
Production-ready server runtime logic for MCP server.

This module handles the actual server execution, transport management, and lifecycle
with comprehensive error handling and structured logging.
"""

import asyncio
import logging
import os
import signal
import traceback
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn.server
from starlette.middleware import Middleware

from ....utils.signal_handlers import create_shutdown_manager
from ..exceptions import (
    MCPCleanupError,
    MCPFrameworkError,
    MCPStartupError,
    MCPTimeoutError,
    MCPTransportError,
    create_startup_error,
    create_timeout_error,
    create_transport_error,
)
from ..middleware import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


async def run_server(
    mcp_instance,
    transport="network",
    host=None,
    port=None,
    startup_timeout=10.0,
    shutdown_event=None,
):
    """
    Run the MCP server with specified transport(s) using async tasks with comprehensive error handling.

    Args:
        mcp_instance: The FastMCP server instance
        transport: Transport protocol (streamable-http, sse, stdio, network)
        host: Host to bind to (ignored for stdio)
        port: Port to listen on (ignored for stdio)
        startup_timeout: Timeout for server startup in seconds

    Raises:
        MCPStartupError: If server fails to start
        MCPTransportError: If transport configuration is invalid
        MCPFrameworkError: For other server errors
    """
    # Validate inputs
    if not mcp_instance:
        raise MCPStartupError("MCP instance cannot be None")

    if transport not in ["network", "sse", "streamable-http", "stdio"]:
        raise MCPTransportError(f"Invalid transport type: {transport}", transport_type=transport)

    # Default values with validation
    host = host or "127.0.0.1"
    port = port or 8000

    if port < 1024 or port > 65535:
        raise MCPStartupError(f"Invalid port number: {port}", context={"port": port})

    logger.info(f"Starting MCP server with transport={transport}, host={host}, port={port}")

    # Disable Uvicorn's signal handlers to prevent conflicts with our handlers
    uvicorn.server.Server.install_signal_handlers = lambda self: None
    logger.debug("Disabled Uvicorn signal handlers")

    # Use shared signal handling utility for consistent behavior
    shutdown_event, signal_manager = create_shutdown_manager(
        shutdown_event=shutdown_event, service_name="MCP Server"
    )

    async def run_transport_server(transport_type, server_host, server_port, path):
        """Run a single transport server as an async task with comprehensive error handling."""
        server_id = f"{transport_type}_{server_port}"

        try:
            logger.info(f"🚀 Starting {transport_type} server on {server_host}:{server_port}{path}")
            print(f"🚀 Starting {transport_type} server on {server_host}:{server_port}{path}")

            # Create middleware list for logging with shutdown event
            middleware_list = [Middleware(RequestLoggingMiddleware, shutdown_event=shutdown_event)]

            # Configure logging to be less noisy during shutdown
            uvicorn_logger = logging.getLogger("uvicorn")
            uvicorn_error_logger = logging.getLogger("uvicorn.error")
            original_level = uvicorn_error_logger.level

            # Also suppress Uvicorn's default logger during shutdown
            uvicorn_default_logger = logging.getLogger("uvicorn")
            original_default_level = uvicorn_default_logger.level

            # Create a task to run the server
            logger.debug(f"Creating {transport_type} task on port {server_port}")
            print(f"   Creating {transport_type} task on port {server_port}")

            server_task = asyncio.create_task(
                mcp_instance.run_async(
                    transport=transport_type,
                    host=server_host,
                    port=server_port,
                    path=path,
                    middleware=middleware_list,
                )
            )

            # Give the server a moment to start up, then wait for shutdown signal
            await asyncio.sleep(1.0)  # Brief startup delay

            # Check if server failed to start
            if server_task.done():
                # Server task completed unexpectedly (likely an error)
                try:
                    await server_task  # This will raise the exception
                except Exception as e:
                    logger.error(f"Server failed to start: {e}")
                    raise create_transport_error(
                        f"{transport_type} server failed to start",
                        transport_type=transport_type,
                        operation="startup",
                        original_error=e,
                    )

            logger.info(f"{transport_type} server started successfully on port {server_port}")
            print(f"✅ {transport_type} server running on port {server_port}")

            # Wait for shutdown signal (server runs indefinitely until signal)
            await shutdown_event.wait()

            # Suppress uvicorn error logging during shutdown
            uvicorn_error_logger.setLevel(logging.CRITICAL)
            uvicorn_default_logger.setLevel(logging.CRITICAL)
            logger.info(f"{transport_type} server shutting down due to signal")

            # Cancel the server task immediately
            server_task.cancel()
            try:
                # Wait for cancellation with a shorter timeout for faster shutdown
                await asyncio.wait_for(server_task, timeout=3.0)
            except asyncio.CancelledError:
                logger.debug(f"Cancelled server task for {transport_type} server")
            except asyncio.TimeoutError:
                logger.warning(
                    f"{transport_type} server did not shutdown within timeout, forcing termination"
                )
            except Exception as e:
                # Suppress most errors during shutdown but log them for debugging
                if not any(
                    term in str(e).lower() for term in ["cancelled", "connection", "disconnect"]
                ):
                    logger.debug(f"Error during {transport_type} server shutdown: {e}")

            # Restore original logging levels
            uvicorn_error_logger.setLevel(original_level)
            uvicorn_default_logger.setLevel(original_default_level)

            logger.info(f"{transport_type} server stopped cleanly")

        except (asyncio.CancelledError, KeyboardInterrupt):
            # Normal shutdown, don't log as error
            logger.debug(f"{transport_type} server cancelled/interrupted")
        except MCPFrameworkError:
            # Re-raise our structured errors
            raise
        except Exception as e:
            # Convert unexpected errors to structured errors
            if not shutdown_event.is_set():
                # Only log/raise errors if not shutting down
                error_msg = str(e).lower()

                # Filter out expected shutdown-related errors
                if not any(
                    term in error_msg
                    for term in ["cancelled", "keyboard", "interrupt", "connection", "disconnect"]
                ):
                    logger.error(f"❌ Error in {transport_type} server: {e}")
                    logger.debug(f"❌ Traceback: {traceback.format_exc()}")
                    print(f"❌ Error in {transport_type} server: {e}")

                    # Create structured error
                    raise create_transport_error(
                        f"Transport server {transport_type} failed",
                        transport_type=transport_type,
                        operation="run_server",
                        original_error=e,
                    )
            else:
                logger.debug(f"{transport_type} server error during shutdown (suppressed): {e}")

    # Create async tasks based on transport mode with error handling
    tasks = []

    # Only use signal manager context when we created our own signal handling
    # (i.e., when shutdown_event was None and we got a SignalManager, not nullcontext)
    with signal_manager:
        try:
            logger.info(f"Configuring transport mode: {transport}")

            if transport in ["network", "sse"]:
                logger.debug(f"📡 Creating SSE server task for transport '{transport}'")
                print(f"📡 Creating SSE server task for transport '{transport}'")
                sse_task = asyncio.create_task(run_transport_server("sse", host, port, "/sse"))
                tasks.append(sse_task)

            if transport in ["network", "streamable-http"]:
                mcp_port = port + 1 if transport == "network" else port
                logger.debug(
                    f"🔌 Creating MCP server task for transport '{transport}' on port {mcp_port}"
                )
                print(f"🔌 Creating MCP server task for transport '{transport}' on port {mcp_port}")
                mcp_task = asyncio.create_task(
                    run_transport_server("streamable-http", host, mcp_port, "/mcp")
                )
                tasks.append(mcp_task)

            if not tasks:
                error_msg = f"No servers configured for transport '{transport}'"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                raise MCPTransportError(error_msg, transport_type=transport)

            logger.info(
                f"✅ Started {len(tasks)} server(s). Waiting for completion or shutdown signal."
            )
            print(f"✅ Started {len(tasks)} server(s). Press Ctrl+C to stop.")

            # Wait for shutdown signal or task completion with proper error handling
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check for any task failures
                for i, result in enumerate(results):
                    if isinstance(result, Exception) and not isinstance(
                        result, (asyncio.CancelledError, KeyboardInterrupt)
                    ):
                        task_name = f"task_{i}"
                        logger.error(f"Task {task_name} failed: {result}")
                        if isinstance(result, MCPFrameworkError):
                            raise result
                        else:
                            raise MCPTransportError(
                                f"Task {task_name} failed unexpectedly",
                                transport_type=transport,
                                cause=result,
                            )

            except KeyboardInterrupt:
                # Don't print anything here - signal handler already did
                logger.debug("KeyboardInterrupt received in main task gathering")
                shutdown_event.set()

        except KeyboardInterrupt:
            # Handle KeyboardInterrupt at top level too
            logger.debug("KeyboardInterrupt received at top level")
            shutdown_event.set()
        except MCPFrameworkError:
            # Re-raise structured errors
            shutdown_event.set()
            raise
        except Exception as e:
            # Convert unexpected errors to structured errors
            if not shutdown_event.is_set():
                logger.error(f"❌ Unexpected error in server orchestration: {e}")
                logger.debug(f"❌ Traceback: {traceback.format_exc()}")
                print(f"❌ Unexpected error: {e}")

                raise MCPStartupError(f"Server orchestration failed: {e}", cause=e)
            else:
                logger.debug(f"Error during shutdown (suppressed): {e}")
            shutdown_event.set()

        finally:
            # Wait for clean shutdown of all tasks
            if tasks:
                logger.info("Initiating graceful shutdown of all transport servers")

                # Cancel all tasks gracefully
                cancelled_tasks = []
                for i, task in enumerate(tasks):
                    if not task.done():
                        task.cancel()
                        cancelled_tasks.append(f"task_{i}")

                if cancelled_tasks:
                    logger.debug(f"Cancelled tasks: {cancelled_tasks}")

                # Wait for cancellation to complete with timeout
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True), timeout=8.0
                    )
                    logger.info("All tasks shut down cleanly")
                except asyncio.TimeoutError:
                    logger.warning(
                        "Some tasks did not shut down within timeout, forcing termination"
                    )
                    # Force termination of remaining tasks
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                            try:
                                await task
                            except asyncio.CancelledError:
                                pass
                            except Exception:
                                pass  # Suppress all errors during forced cleanup
                except Exception as e:
                    logger.debug(f"Exception during task cleanup (suppressed): {e}")

    if not shutdown_event.is_set():
        logger.info("👋 Server shutdown complete")
        print("👋 Shutdown complete")
    else:
        logger.info("👋 Server shutdown complete (via signal)")
        print("👋 Shutdown complete")


def run_server_cli(mcp_instance, transport="network", host=None, port=None, startup_timeout=10.0):
    """
    Production-ready CLI entry point that creates its own event loop with comprehensive error handling.

    Args:
        mcp_instance: The FastMCP server instance
        transport: Transport protocol (streamable-http, sse, stdio, network)
        host: Host to bind to (ignored for stdio)
        port: Port to listen on (ignored for stdio)
        startup_timeout: Timeout for server startup in seconds

    Raises:
        MCPStartupError: If server fails to start
        MCPTransportError: If transport configuration is invalid
        MCPFrameworkError: For other server errors
    """
    logger.info(f"Starting MCP server CLI with transport={transport}")

    if transport == "stdio":
        try:
            logger.info("Starting MCP server in stdio mode")
            mcp_instance.run()
        except KeyboardInterrupt:
            logger.info("MCP server stdio mode interrupted gracefully")
        except Exception as e:
            logger.error(f"Error in stdio mode: {e}")
            raise MCPStartupError(
                f"STDIO transport failed: {e}", context={"transport": "stdio"}, cause=e
            )
        return

    # Run the async server with error handling
    try:
        asyncio.run(run_server(mcp_instance, transport, host, port, startup_timeout))
        logger.info("MCP server CLI completed successfully")
    except KeyboardInterrupt:
        logger.info("MCP server CLI interrupted gracefully")
    except MCPFrameworkError:
        # Re-raise structured errors
        logger.error("MCP server CLI failed with framework error")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in MCP server CLI: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise MCPStartupError(f"CLI execution failed: {e}", cause=e)
