"""
Core Streaming Module

Provides transport-agnostic streaming message infrastructure for CodeGuard.
Supports multiple output destinations (ZMQ, stdout, files, etc.) with unified API.
"""

from .base import MessageSender
from .protocol import (
    CommandComplete,
    CommandError,
    ComponentComplete,
    ComponentError,
    ComponentProgress,
    ComponentStart,
    ProgressUpdate,
    StatusMessage,
    StreamEnd,
    StreamingMessage,
    StreamingMessageType,
    StreamJson,
    StreamStart,
)
from .stdout import StdoutMessageSender

__all__ = [
    "MessageSender",
    "StdoutMessageSender",
    "ProgressUpdate",
    "StatusMessage",
    "StreamJson",
    "CommandComplete",
    "CommandError",
    "StreamStart",
    "StreamEnd",
    "ComponentStart",
    "ComponentProgress",
    "ComponentComplete",
    "ComponentError",
    "StreamingMessage",
    "StreamingMessageType",
]
