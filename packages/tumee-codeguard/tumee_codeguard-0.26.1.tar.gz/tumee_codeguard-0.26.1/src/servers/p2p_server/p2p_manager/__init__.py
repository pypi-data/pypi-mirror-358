"""
P2P Package for CodeGuard

Provides peer-to-peer networking capabilities for distributed AI ownership
and command execution with streaming support.
"""

from .command_classifier import CommandClassifier, CommandInfo, CommandType, P2PRequirement
from .command_router import CommandRouter, RoutingDecision
from .lazy_manager import (
    LazyP2PManager,
    ensure_p2p_for_command,
    get_p2p_command_router,
    get_p2p_network_manager,
    get_p2p_remote_executor,
    is_p2p_available,
    shutdown_p2p,
)
from .mcp_router import MCPRouter, MCPRoutingDecision
from .remote_executor import RemoteExecutionResult, RemoteExecutor
from .streaming_protocol import (
    CommandComplete,
    ProgressUpdate,
    StatusMessage,
    StreamingMessage,
    StreamingMessageType,
    StreamingProtocol,
    StreamJson,
)

__all__ = [
    # Streaming Protocol
    "StreamingMessage",
    "StreamingMessageType",
    "ProgressUpdate",
    "StatusMessage",
    "StreamJson",
    "CommandComplete",
    "StreamingProtocol",
    # Command Classification
    "CommandClassifier",
    "CommandInfo",
    "CommandType",
    "P2PRequirement",
    # Command Routing
    "CommandRouter",
    "RoutingDecision",
    # Remote Execution
    "RemoteExecutor",
    "RemoteExecutionResult",
    # MCP Integration
    "MCPRouter",
    "MCPRoutingDecision",
    # Lazy Management
    "LazyP2PManager",
    "ensure_p2p_for_command",
    "get_p2p_command_router",
    "get_p2p_network_manager",
    "get_p2p_remote_executor",
    "is_p2p_available",
    "shutdown_p2p",
]
