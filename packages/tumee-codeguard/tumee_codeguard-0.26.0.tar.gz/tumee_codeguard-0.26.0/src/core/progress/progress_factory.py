"""
Progress Factory - Unified Progress Setup for Local and Remote Modes

Creates properly initialized ConsoleFormatter and ComponentProgressTracker instances
with consistent configuration for both local and remote command execution.
"""

import asyncio
import logging
from typing import List, Optional, Tuple

from ..formatters.console import ConsoleFormatter, StreamingProgressSender
from ..runtime import get_current_command_id, is_worker_process

logger = logging.getLogger(__name__)


def create_progress_formatter(
    worker_mode: str,
    component_specs: Optional[List[Tuple[str, dict]]] = None,
    streaming_sender: Optional[StreamingProgressSender] = None,
    command_id: Optional[str] = None,
    show_progress: bool = True,
    total_expected_work: Optional[int] = None,
) -> ConsoleFormatter:
    """
    Create a properly initialized ConsoleFormatter for progress display.

    This function encapsulates the progress setup logic used by both local and remote
    execution modes, ensuring consistent behavior and avoiding code duplication.

    Args:
        component_specs: List of (component_name, params) tuples for expected work calculation
        streaming_sender: Optional streaming sender for remote progress updates
        command_id: Optional command ID for streaming (auto-detected if None)
        show_progress: Whether to enable progress display
        total_expected_work: Optional total expected work units (overrides component count)

    Returns:
        Configured ConsoleFormatter instance (always valid, never None)
    """

    # Calculate expected total work units
    if total_expected_work is not None:
        expected_total = total_expected_work
    else:
        # Default to 1 per component + 1 for routing
        expected_total = len(component_specs) + 1 if component_specs else 1

    # Auto-detect command ID if not provided
    if command_id is None:
        command_id = get_current_command_id()

    # Auto-detect worker process and create appropriate sender for progress forwarding
    if streaming_sender is None and is_worker_process():
        if worker_mode == "p2p":
            # P2P mode: Must use cached streaming sender from message handler
            if not command_id:
                raise RuntimeError("P2P mode requires command_id")

            from ...servers.p2p_server.p2p_manager.streaming_cache import StreamingServerCache

            cache = StreamingServerCache.get_instance()
            streaming_sender = cache.get(command_id)
            if not streaming_sender:
                logger.error(f"No streaming sender found in cache for command_id: {command_id}")
                raise RuntimeError(
                    f"No streaming sender found in cache for command_id: {command_id}"
                )

        elif worker_mode == "ipc":
            # IPC mode: Use stdout sender
            from ..streaming.stdout import StdoutMessageSender

            streaming_sender = StdoutMessageSender()
            # Start the sender to enable message processing
            try:
                loop = asyncio.get_running_loop()
                # Schedule the start coroutine on the existing event loop
                asyncio.create_task(streaming_sender.start())
            except RuntimeError:
                logger.warning(
                    "No running event loop found, will start streaming sender when loop is available"
                )

                # No event loop running, create a task that will start when loop is available
                async def start_when_ready():
                    await streaming_sender.start()

                # This will be picked up when an event loop starts
                asyncio.ensure_future(start_when_ready())
        else:
            raise RuntimeError(f"Invalid worker mode: {worker_mode}")

    # Create ConsoleFormatter with proper initialization
    formatter = ConsoleFormatter(
        streaming_sender=streaming_sender,
        command_id=command_id,
        show_progress=show_progress,
    )

    # Pre-initialize expected total for immediate progress display
    if expected_total > 0:
        formatter._expected_total = expected_total

    return formatter


def setup_unified_progress(
    worker_mode: str,
    component_specs: Optional[List[Tuple[str, dict]]] = None,
    streaming_sender: Optional[StreamingProgressSender] = None,
    command_id: Optional[str] = None,
    show_progress: bool = True,
    total_expected_work: Optional[int] = None,
) -> ConsoleFormatter:
    """
    Complete progress setup in one call - creates formatter.

    Args:
        component_specs: List of (component_name, params) tuples for expected work calculation
        streaming_sender: Optional streaming sender for remote progress updates
        command_id: Optional command ID for streaming (auto-detected if None)
        show_progress: Whether to enable progress display
        total_expected_work: Optional total expected work units (overrides component count)

    Returns:
        ConsoleFormatter instance (always valid, use formatter.create_progress_callback() for callback)
    """
    formatter = create_progress_formatter(
        worker_mode=worker_mode,
        component_specs=component_specs,
        streaming_sender=streaming_sender,
        command_id=command_id,
        show_progress=show_progress,
        total_expected_work=total_expected_work,
    )

    return formatter
