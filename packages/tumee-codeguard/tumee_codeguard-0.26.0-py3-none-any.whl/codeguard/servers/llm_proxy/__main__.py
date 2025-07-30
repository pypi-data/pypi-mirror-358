"""
Entry point for aiohttp LLM proxy server.
"""

import asyncio
import logging
import ssl
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from aiohttp import web

from ...utils.signal_handlers import create_shutdown_manager
from .server import LLMProxyServer, create_ssl_context

logger = logging.getLogger(__name__)


async def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file (optional)

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default config path
        config_path = str(
            Path(__file__).parent.parent.parent / "resources" / "llm_proxy_default.yaml"
        )

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        logging.info(f"Loaded configuration from {config_path}")
        return config

    except Exception as e:
        logging.error(f"Failed to load config from {config_path}: {e}")
        # Return minimal default config
        return {
            "upstream": {
                "timeout": 30,
                "anthropic": {"base_url": "https://api.anthropic.com"},
                "openai": {"base_url": "https://api.openai.com"},
            },
            "content": {"injection": {"enabled": False}, "filtering": {"enabled": False}},
            "tools": {"logging": {"enabled": True}},
            "streaming": {"enable_processing": True},
        }


async def create_server(
    config: Dict[str, Any], host: str, port: int, shutdown_event: Optional[asyncio.Event] = None
) -> Tuple[LLMProxyServer, web.AppRunner]:
    """
    Create and configure the LLM proxy server.

    Args:
        config: Server configuration
        host: Server host
        port: Server port

    Returns:
        Configured LLMProxyServer instance
    """
    # Create server instance with shutdown event
    server = LLMProxyServer(config, shutdown_event)

    # Create SSL context
    ssl_context = None
    server_config = config.get("server", {})

    cert_file = server_config.get("ssl_cert_file")
    key_file = server_config.get("ssl_key_file")

    if cert_file and key_file:
        try:
            ssl_context = create_ssl_context(cert_file, key_file)
            logging.info(f"SSL enabled with cert: {cert_file}")
        except Exception as e:
            logging.error(f"Failed to create SSL context: {e}")
            logging.info("Continuing without SSL")
    else:
        logging.info("SSL not configured, running HTTP only")

    # Start server
    runner = await server.start_server(host=host, port=port, ssl_context=ssl_context)

    return server, runner


async def run_proxy_with_shutdown(
    config_path: Optional[str] = None,
    host: str = "localhost",
    port: int = 8080,
    shutdown_event: Optional[asyncio.Event] = None,
):
    """
    Run LLM proxy with shared shutdown coordination.

    Args:
        config_path: Path to configuration file
        host: Server host
        port: Server port
        shutdown_event: External shutdown event for coordination
    """
    # Create shutdown management - uses external event if provided
    shutdown_event, signal_manager = create_shutdown_manager(
        shutdown_event=shutdown_event, service_name="LLM Proxy"
    )

    server: Optional[LLMProxyServer] = None
    runner: Optional[web.AppRunner] = None

    # Only use signal manager context when we created our own signal handling
    # (i.e., when shutdown_event was None and we got a SignalManager, not nullcontext)
    with signal_manager:
        try:
            # Load configuration
            config = await load_config(config_path)

            # Create and start server with shutdown event
            logger.info(f"Starting CodeGuard LLM Proxy on {host}:{port}")
            server, runner = await create_server(config, host, port, shutdown_event)

            # Create shutdown monitor task
            async def shutdown_monitor():
                logger.info("LLM Proxy shutdown monitor started, waiting for signal...")
                await shutdown_event.wait()
                logger.info("LLM Proxy received shutdown signal, stopping server...")
                await runner.cleanup()
                logger.info("LLM Proxy runner cleanup complete")

            # Run shutdown monitor in background
            shutdown_task = asyncio.create_task(shutdown_monitor())
            logger.info("LLM Proxy shutdown monitor task created")

            try:
                # Wait for shutdown task to complete
                logger.info("LLM Proxy waiting for shutdown task...")
                await shutdown_task
                logger.info("LLM Proxy shutdown task completed")
            except asyncio.CancelledError:
                logger.info("LLM Proxy shutdown task cancelled")
                await runner.cleanup()

        except Exception as e:
            logger.error(f"LLM Proxy error: {e}", exc_info=True)
            raise

        finally:
            # Final cleanup
            try:
                if server:
                    await server.cleanup()
                # runner cleanup is handled in shutdown_monitor
                logger.info("LLM Proxy shutdown complete")
            except Exception as e:
                logger.error(f"LLM Proxy cleanup error: {e}", exc_info=True)


async def main():
    """
    Main entry point for standalone aiohttp LLM proxy.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    # Parse command line arguments (basic)
    import argparse

    parser = argparse.ArgumentParser(description="CodeGuard LLM Proxy Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    try:
        # Run with standalone signal handling (no external shutdown event)
        await run_proxy_with_shutdown(
            config_path=args.config,
            host=args.host,
            port=args.port,
            shutdown_event=None,  # Creates own shutdown event and signal handling
        )

    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
