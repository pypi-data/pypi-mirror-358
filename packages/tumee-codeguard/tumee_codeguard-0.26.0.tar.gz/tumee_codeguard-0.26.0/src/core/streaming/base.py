"""
Base Message Sender

Provides abstract base class for sending streaming messages with unified queue/writer pattern.
Implementations handle different transport mechanisms (ZMQ, stdout, files, etc.).
"""

import asyncio
from typing import Any, Dict, Optional

from ...utils.logging_config import get_logger
from .protocol import (
    CommandComplete,
    ComponentComplete,
    ComponentProgress,
    ComponentStart,
    ProgressUpdate,
    StatusMessage,
    StreamingMessage,
    StreamJson,
)

logger = get_logger(__name__)


class MessageSender:
    """Abstract base for sending streaming messages with unified queue/writer pattern."""

    def __init__(self):
        self.running = False
        self.message_queue = asyncio.Queue()
        self.writer_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the message sender."""
        if self.running:
            return
        self.running = True
        await self._setup_destination()
        self.writer_task = asyncio.create_task(self._message_writer())
        await asyncio.sleep(0)  # Yield to ensure task starts properly

    async def stop(self):
        """Stop the message sender."""
        if not self.running:
            return
        self.running = False

        # Send shutdown signal to queue worker AFTER all current messages
        try:
            self.message_queue.put_nowait(None)
        except asyncio.QueueFull:
            pass  # Queue is full, worker will exit when task is cancelled anyway

        if self.writer_task:
            try:
                # Give more time for messages to be processed
                await asyncio.wait_for(self.writer_task, timeout=5.0)
            except asyncio.TimeoutError:
                self.writer_task.cancel()
                try:
                    await self.writer_task
                except asyncio.CancelledError:
                    pass
            self.writer_task = None
        await self._cleanup_destination()

    async def _setup_destination(self):
        """Setup the destination (implemented by subclasses)."""
        pass

    async def _cleanup_destination(self):
        """Cleanup the destination (implemented by subclasses)."""
        pass

    async def _send_message(self, message: StreamingMessage):
        """Send message to destination (implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement _send_message")

    async def _message_writer(self):
        """Single writer task that consumes message queue."""
        try:
            while self.running:
                try:
                    message = await self.message_queue.get()

                    # Check if we got a shutdown signal
                    if message is None:
                        break

                    await self._send_message(message)
                    self.message_queue.task_done()

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Continue processing other messages
                    continue
        finally:
            logger.debug(f"Queue worker exiting, running={self.running}")

    async def send_message(self, message: StreamingMessage):
        """Queue a message for sending."""
        try:
            self.message_queue.put_nowait(message)
            await asyncio.sleep(0.017)  # Fixed delay after each put
        except asyncio.QueueFull:
            logger.warning("Message queue full, dropping message")
        except Exception as e:
            logger.error(f"Exception in send_message: {e}")

    async def send_progress(
        self,
        command_id: str,
        progress: int,
        total: Optional[int] = None,
        message: str = "",
        stage: Optional[str] = None,
        component_id: Optional[str] = None,
        component_event: Optional[str] = None,
        cumulative_current: Optional[float] = None,
        cumulative_total: Optional[float] = None,
    ):
        """Send progress update message. For component events, use dedicated component methods."""
        # If this is a component event, delegate to appropriate component method
        if component_event and component_id:
            if component_event == "start":
                await self.send_component_start(
                    command_id=command_id,
                    component_id=component_id,
                    total=total or 100,
                    phase=stage or component_id,
                    overall_total=cumulative_total,
                )
                return
            elif component_event == "update":
                await self.send_component_progress(
                    command_id=command_id,
                    component_id=component_id,
                    current=progress,
                )
                return
            elif component_event == "stop":
                await self.send_component_complete(
                    command_id=command_id,
                    component_id=component_id,
                )
                return

        # Regular progress update
        progress_msg = ProgressUpdate(
            command_id=command_id,
            progress=progress,
            total=total or 0,  # Convert None to 0 for ProgressUpdate
            message=message,
            stage=stage,
            component_id=component_id,
            component_event=component_event,
            cumulative_current=cumulative_current,
            cumulative_total=cumulative_total,
        )
        await self.send_message(progress_msg)

    async def send_status(
        self, command_id: str, level: str, message: str, source: Optional[str] = None
    ):
        """Send status message."""
        status_msg = StatusMessage(
            command_id=command_id, level=level, message=message, source=source
        )
        await self.send_message(status_msg)

    async def send_output(self, command_id: str, stream: str, data: str, encoding: str = "utf-8"):
        """Send output data message."""
        json_msg = StreamJson(command_id=command_id, data=data, encoding=encoding)
        await self.send_message(json_msg)

    async def send_completion(
        self,
        command_id: str,
        status: str,
        exit_code: int = 0,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
    ):
        """Send command completion message."""
        complete_msg = CommandComplete(
            command_id=command_id,
            status=status,
            exit_code=exit_code,
            result=result,
            error=error,
            execution_time=execution_time,
        )
        await self.send_message(complete_msg)

    async def send_component_start(
        self,
        command_id: str,
        component_id: str,
        total: int = 100,
        phase: Optional[str] = None,
        overall_total: Optional[float] = None,
    ):
        """Send component start message."""
        component_msg = ComponentStart(
            command_id=command_id,
            component_name=component_id,  # Use component_name as expected by protocol
        )
        await self.send_message(component_msg)

    async def send_component_progress(
        self,
        command_id: str,
        component_id: str,
        current: int,
    ):
        """Send component progress message."""
        component_msg = ComponentProgress(
            command_id=command_id,
            component_name=component_id,  # Use component_name as expected by protocol
            progress=current,
        )
        await self.send_message(component_msg)

    async def send_component_complete(
        self,
        command_id: str,
        component_id: str,
    ):
        """Send component complete message."""
        component_msg = ComponentComplete(
            command_id=command_id,
            component_name=component_id,  # Use component_name as expected by protocol
            data={},  # Empty data for now
            execution_time=0.0,  # Placeholder
        )
        await self.send_message(component_msg)
