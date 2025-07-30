"""
CLI utility functions for P2P network operations.

This module contains utility functions for querying and monitoring P2P networks,
separated from the core HierarchicalNetworkManager class for better organization.
"""

import asyncio
import json
import os
import select
import sys
import termios
import time
import tty
from typing import List, Optional

import aioconsole
import zmq
import zmq.asyncio

from ...core.console_shared import CONSOLE, cprint
from ...core.project.hierarchy_display import format_hierarchy_display
from ...utils.logging_config import get_logger, setup_cli_logging
from .config import P2PConfig, get_p2p_service
from .models import DiscoveryAnnouncement, NodeInfo, NodeMode
from .network_manager import HierarchicalNetworkManager

logger = get_logger(__name__)


async def getch():
    """Get a single character from stdin without pressing Enter."""
    try:
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())

            # Check if input is available
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                char = sys.stdin.read(1)
                return char
            return None
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        # Fallback to regular input if terminal manipulation fails
        return None


async def keyboard_handler(shutdown_event: asyncio.Event, discovery_manager):
    """Handle keyboard input for monitor commands."""
    try:
        cprint("📝 Press 'q' to quit, 'l' to list nodes")
        while not shutdown_event.is_set():
            try:
                # Read a single character without Enter
                char = await getch()

                if not char:
                    await asyncio.sleep(0.1)
                    continue

                if char.lower() == "q":
                    cprint("🛑 Quitting monitor...")
                    shutdown_event.set()
                    break
                elif char.lower() == "l":
                    try:
                        # Use cached hierarchy with smart expiration
                        hierarchy_data = await discovery_manager.get_cached_hierarchy()

                        # Format and display the hierarchy
                        formatted_output = format_hierarchy_display(hierarchy_data)
                        cprint(formatted_output)

                    except Exception as e:
                        logger.debug(f"Error getting cached hierarchy: {e}")
                        cprint("Error retrieving hierarchy data")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Keyboard handler error: {e}")

    except Exception as e:
        logger.debug(f"Keyboard handler setup error: {e}")


async def handle_query(
    paths: List[str], show_all: bool = False, config: Optional[P2PConfig] = None, timeout: int = 5
):
    """Query the network for path ownership."""
    # Setup CLI logging for this function
    setup_cli_logging(logger)

    logger.info(f"Scanning P2P network for {timeout} seconds...")

    # Use the singleton HierarchicalNetworkManager
    if config:
        config_obj = config
    else:
        p2p_service = get_p2p_service()
        config_obj = p2p_service.load_config()
    manager = await HierarchicalNetworkManager.get_instance(
        config=config_obj,
        managed_paths=[],  # Query doesn't manage paths
        discovery_priority=0,  # Low priority for query operations
        node_mode=NodeMode.MONITOR,  # Query operations are monitor-type
    )

    # Start services (idempotent)
    await manager.start_services()

    # Wait for discovery to populate
    logger.info("Waiting for discovery data...")
    await asyncio.sleep(timeout)

    # Get discovered nodes from the singleton's discovery manager
    known_nodes = manager.discovery_manager._known_nodes
    registry = {}

    # Convert known_nodes to registry format
    for node_id, node_data in known_nodes.items():
        managed_paths = node_data.get("managed_paths", [])
        boundaries = node_data.get("boundaries", {})
        for path in managed_paths:
            registry[path] = NodeInfo(
                node_id=node_id,
                address=node_data.get("address", "Unknown"),
                managed_paths=managed_paths,
                boundaries=boundaries,
                parent=None,  # Not tracked in current format
                timestamp=node_data.get("last_seen", time.time()),
            )

    if show_all:
        # Show all registered paths
        if registry:
            logger.info("Found P2P instances:")
            all_paths = {}

            # Add paths from registry
            for path, info in registry.items():
                all_paths[path] = info

            # Sort by path
            for path in sorted(all_paths.keys()):
                info = all_paths[path]
                logger.info(f"  {path}: {info.node_id} at {info.address}")
        else:
            logger.info("No P2P instances found in the network")
    else:
        # Query specific paths
        found_any = False
        for path in paths:
            logger.info(f"Querying: {path}")

            # Find best match in registry
            owner = None
            best_match_len = 0

            for reg_path, info in registry.items():
                if path.startswith(reg_path + "/") or path == reg_path:
                    if len(reg_path) > best_match_len:
                        owner = info
                        best_match_len = len(reg_path)

            if owner:
                logger.info(f"  Root owner: {owner.node_id} at {owner.address}")
                found_any = True
            else:
                logger.info("  No owner found")

        if not found_any and not registry:
            logger.info("No P2P instances found in the network")


async def handle_monitor(config: Optional[P2PConfig] = None, timeout: int = 0):
    """Monitor P2P network for join/leave events using priority discovery system."""
    setup_cli_logging(logger)

    cprint("🚀 Starting P2P network monitor with discovery fallback...")
    logger.debug("Starting P2P network monitor with discovery fallback...")

    # Use provided config or load default
    if config:
        config_obj = config
    else:
        p2p_service = get_p2p_service()
        config_obj = p2p_service.load_config()

    # Use the singleton HierarchicalNetworkManager
    shutdown_event = asyncio.Event()
    monitor_manager = await HierarchicalNetworkManager.get_instance(
        config=config_obj,
        managed_paths=[],  # Monitor doesn't manage paths
        shutdown_event=shutdown_event,
        discovery_priority=25,  # Monitor priority
        node_mode=NodeMode.MONITOR,  # This is a monitor node
    )

    start_time = time.time()

    keyboard_task = None
    try:
        # Start the monitor (which may become discovery broker if none exists)
        await monitor_manager.start_services()

        if not monitor_manager.discovery_manager.is_discovery_broker:
            cprint("📡 📺 Monitor connected to existing discovery service")

        # Start keyboard handler task for interactive commands
        keyboard_task = asyncio.create_task(
            keyboard_handler(shutdown_event, monitor_manager.discovery_manager)
        )

        # Monitor loop - just wait and let DiscoveryManager handle all message processing
        # No competing recv operations here to avoid race conditions with DiscoveryManager
        while not shutdown_event.is_set():
            # Check timeout only if timeout > 0 (0 means run forever)
            if timeout > 0 and (time.time() - start_time) > timeout:
                logger.info(f"Monitor timeout reached ({timeout}s)")
                break

            # Just wait - DiscoveryManager handles all discovery messages
            # The keyboard handler provides the interactive functionality
            await asyncio.sleep(1.0)

    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
        raise
    finally:
        shutdown_event.set()
        # Cancel keyboard handler task
        if keyboard_task:
            keyboard_task.cancel()
            try:
                await keyboard_task
            except asyncio.CancelledError:
                pass
        await monitor_manager.stop()
