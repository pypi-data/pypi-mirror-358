"""
Streaming Protocol Message Types

Defines transport-agnostic message types for streaming communication.
These messages can be sent over any transport (ZMQ, stdout, files, etc.).
"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StreamingMessageType(str, Enum):
    """Types of streaming messages."""

    PROGRESS_UPDATE = "PROGRESS_UPDATE"
    STATUS_MESSAGE = "STATUS_MESSAGE"
    STREAM_JSON = "STREAM_JSON"
    COMMAND_COMPLETE = "COMMAND_COMPLETE"
    COMMAND_ERROR = "COMMAND_ERROR"
    STREAM_START = "STREAM_START"
    STREAM_END = "STREAM_END"
    COMPONENT_START = "COMPONENT_START"
    COMPONENT_PROGRESS = "COMPONENT_PROGRESS"
    COMPONENT_COMPLETE = "COMPONENT_COMPLETE"
    COMPONENT_ERROR = "COMPONENT_ERROR"


class StreamingMessage(BaseModel):
    """Base class for all streaming messages."""

    type: StreamingMessageType
    command_id: str
    timestamp: float = Field(default_factory=time.time)


class ProgressUpdate(StreamingMessage):
    """Progress update message for long-running operations."""

    type: StreamingMessageType = StreamingMessageType.PROGRESS_UPDATE
    progress: int  # Current progress (0-100 or current count)
    total: int = 0  # Total items if known
    message: str = ""  # Description of current operation
    stage: Optional[str] = None  # Current stage name

    # Component tracker fields for cumulative progress display
    component_id: Optional[str] = None  # Component generating this progress
    component_event: Optional[str] = None  # "start", "update", "stop"
    cumulative_current: Optional[float] = None  # Current cumulative progress
    cumulative_total: Optional[float] = None  # Total cumulative progress


class StatusMessage(StreamingMessage):
    """Status or log message."""

    type: StreamingMessageType = StreamingMessageType.STATUS_MESSAGE
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    message: str
    source: Optional[str] = None  # Component that generated the message


class StreamJson(StreamingMessage):
    """Complete JSON structure for streaming."""

    type: StreamingMessageType = StreamingMessageType.STREAM_JSON
    data: str  # Complete JSON string
    encoding: str = "utf-8"


class CommandComplete(StreamingMessage):
    """Final command completion message with results."""

    type: StreamingMessageType = StreamingMessageType.COMMAND_COMPLETE
    status: str  # "success", "error", "timeout"
    exit_code: int = 0
    result: Optional[Dict[str, Any]] = None  # JSON result data
    error: Optional[str] = None
    execution_time: Optional[float] = None


class CommandError(StreamingMessage):
    """Command error message."""

    type: StreamingMessageType = StreamingMessageType.COMMAND_ERROR
    error: str
    error_type: str = "execution_error"
    traceback: Optional[str] = None


class StreamStart(StreamingMessage):
    """Stream start notification."""

    type: StreamingMessageType = StreamingMessageType.STREAM_START
    command: str  # The command being executed
    args: List[str] = Field(default_factory=list)
    environment: Optional[Dict[str, str]] = None


class StreamEnd(StreamingMessage):
    """Stream end notification."""

    type: StreamingMessageType = StreamingMessageType.STREAM_END
    final_status: str


class ComponentStart(StreamingMessage):
    """Component analysis start notification."""

    type: StreamingMessageType = StreamingMessageType.COMPONENT_START
    component_name: str
    estimated_duration: Optional[float] = None  # Estimated seconds to complete
    sequence_number: int = 0  # For ordering
    dependencies: List[str] = Field(default_factory=list)  # Components this depends on


class ComponentProgress(StreamingMessage):
    """Component analysis progress update."""

    type: StreamingMessageType = StreamingMessageType.COMPONENT_PROGRESS
    component_name: str
    progress: int  # 0-100 percentage
    current_step: str = ""  # Description of current operation
    sequence_number: int = 0


class ComponentComplete(StreamingMessage):
    """Component analysis completion with results."""

    type: StreamingMessageType = StreamingMessageType.COMPONENT_COMPLETE
    component_name: str
    data: Dict[str, Any]  # Component results
    execution_time: float
    sequence_number: int = 0
    next_components: List[str] = Field(
        default_factory=list
    )  # Components unlocked by this completion


class ComponentError(StreamingMessage):
    """Component analysis error."""

    type: StreamingMessageType = StreamingMessageType.COMPONENT_ERROR
    component_name: str
    error: str
    error_type: str = "component_error"
    sequence_number: int = 0
    can_continue: bool = True  # Whether other components can still run
