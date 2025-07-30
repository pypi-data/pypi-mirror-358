"""
P2P Command Classifier

Determines which CLI commands require P2P routing and which can be executed locally.
Classifies commands as source-touching (need P2P), streaming (need progress forwarding),
or utility (local only).
"""

from enum import Enum
from typing import Dict, List, Optional, Set

try:
    from ....utils.logging_config import get_logger
except ImportError:
    # Handle case when running as standalone script
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from utils.logging_config import get_logger

logger = get_logger(__name__)


class CommandType(str, Enum):
    """Types of commands for P2P routing decisions."""

    SOURCE_TOUCHING = "source_touching"  # Commands that access source files/directories
    STREAMING = "streaming"  # Commands that produce progress/streaming output
    UTILITY = "utility"  # Utility commands that are always local
    SERVER = "server"  # Server/daemon commands


class P2PRequirement(str, Enum):
    """P2P routing requirements for commands."""

    REQUIRED = "required"  # Must check P2P ownership, route if needed
    OPTIONAL = "optional"  # Can benefit from P2P but not required
    NEVER = "never"  # Never use P2P routing
    SERVER_ONLY = "server_only"  # Only triggers P2P startup, doesn't route


class CommandInfo:
    """Information about a command's P2P routing requirements."""

    def __init__(
        self,
        command_type: CommandType,
        p2p_requirement: P2PRequirement,
        supports_streaming: bool = False,
        paths_from_args: Optional[List[str]] = None,
        description: str = "",
    ):
        self.command_type = command_type
        self.p2p_requirement = p2p_requirement
        self.supports_streaming = supports_streaming
        self.paths_from_args = paths_from_args or []
        self.description = description

    def needs_p2p_check(self) -> bool:
        """Check if this command needs P2P ownership verification."""
        return self.p2p_requirement in [P2PRequirement.REQUIRED, P2PRequirement.OPTIONAL]

    def needs_streaming_support(self) -> bool:
        """Check if this command needs streaming support for remote execution."""
        return self.supports_streaming

    def triggers_p2p_startup(self) -> bool:
        """Check if this command should trigger P2P startup."""
        return self.p2p_requirement in [
            P2PRequirement.REQUIRED,
            P2PRequirement.OPTIONAL,
            P2PRequirement.SERVER_ONLY,
        ]


class CommandClassifier:
    """Classifies CLI commands for P2P routing decisions."""

    def __init__(self):
        self.command_registry: Dict[str, CommandInfo] = {}
        self._initialize_command_registry()

    def _initialize_command_registry(self):
        """Initialize the registry of known commands and their P2P requirements."""

        # Source-touching commands that require P2P routing
        self.command_registry.update(
            {
                "verify": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["original", "modified"],
                    description="File verification against guards",
                ),
                "tags": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["path"],
                    description="Guard tag scanning",
                ),
                "show": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["file"],
                    description="File visualization with guards",
                ),
                "acl": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["path"],
                    description="ACL permission checking",
                ),
            }
        )

        # Context commands - these support streaming and need P2P
        self.command_registry.update(
            {
                "context up": CommandInfo(
                    CommandType.STREAMING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=True,
                    paths_from_args=["directory"],
                    description="Context discovery walking up",
                ),
                "context down": CommandInfo(
                    CommandType.STREAMING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=True,
                    paths_from_args=["directory"],
                    description="Context discovery walking down",
                ),
                "context wide": CommandInfo(
                    CommandType.STREAMING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=True,
                    paths_from_args=["directory"],
                    description="Context discovery breadth-first",
                ),
                "context path": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["path"],
                    description="Single path context scanning",
                ),
                "context analyze": CommandInfo(
                    CommandType.STREAMING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=True,
                    paths_from_args=["directory"],
                    description="Intelligent context analysis",
                ),
                "context query": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["directory"],
                    description="Query cached context",
                ),
                "context update": CommandInfo(
                    CommandType.STREAMING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=True,
                    paths_from_args=["directory"],
                    description="Incremental context update",
                ),
                "context stats": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["directory"],
                    description="Context cache statistics",
                ),
                "context invalidate": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["directory"],
                    description="Invalidate context cache",
                ),
            }
        )

        # Guards commands
        self.command_registry.update(
            {
                "guards create": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["directory"],
                    description="Create .ai-attributes file",
                ),
                "guards list": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["directory"],
                    description="List guard rules",
                ),
                "guards validate": CommandInfo(
                    CommandType.STREAMING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=True,
                    paths_from_args=["directory"],
                    description="Validate .ai-attributes files",
                ),
                "guards directories": CommandInfo(
                    CommandType.SOURCE_TOUCHING,
                    P2PRequirement.REQUIRED,
                    supports_streaming=False,
                    paths_from_args=["directory"],
                    description="List guarded directories",
                ),
            }
        )

        # Server commands - trigger P2P startup
        self.command_registry.update(
            {
                "serve mcp": CommandInfo(
                    CommandType.SERVER,
                    P2PRequirement.SERVER_ONLY,
                    supports_streaming=False,
                    description="Start MCP server",
                ),
                "serve proxy": CommandInfo(
                    CommandType.SERVER,
                    P2PRequirement.SERVER_ONLY,
                    supports_streaming=False,
                    description="Start LLM proxy server",
                ),
                "serve llm": CommandInfo(
                    CommandType.SERVER,
                    P2PRequirement.SERVER_ONLY,
                    supports_streaming=False,
                    description="Start LLM services",
                ),
                "serve all": CommandInfo(
                    CommandType.SERVER,
                    P2PRequirement.SERVER_ONLY,
                    supports_streaming=False,
                    description="Start all services",
                ),
                "serve p2p": CommandInfo(
                    CommandType.SERVER,
                    P2PRequirement.SERVER_ONLY,
                    supports_streaming=False,
                    paths_from_args=["paths"],
                    description="Start P2P server",
                ),
                "serve ide": CommandInfo(
                    CommandType.SERVER,
                    P2PRequirement.SERVER_ONLY,
                    supports_streaming=False,
                    description="Start IDE attachment",
                ),
            }
        )

        # Utility commands - never use P2P
        self.command_registry.update(
            {
                "help": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Show help information"
                ),
                "docs": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Show documentation"
                ),
                "tui": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Launch TUI interface"
                ),
                # Setup commands
                "setup roots": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Setup security roots"
                ),
                "setup config": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Setup configuration"
                ),
                # SSL commands
                "ssl generate": CommandInfo(
                    CommandType.UTILITY,
                    P2PRequirement.NEVER,
                    description="Generate SSL certificates",
                ),
                "ssl verify": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Verify SSL certificates"
                ),
                # Prompt commands
                "prompt add": CommandInfo(
                    CommandType.UTILITY,
                    P2PRequirement.NEVER,
                    description="Add prompt injection rule",
                ),
                "prompt list": CommandInfo(
                    CommandType.UTILITY,
                    P2PRequirement.NEVER,
                    description="List prompt injection rules",
                ),
                # Smart notes commands
                "smart capture": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Capture smart notes"
                ),
                "smart query": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Query smart notes"
                ),
                # System commands
                "sys info": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="System information"
                ),
                "sys health": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="System health check"
                ),
                # P2P commands (except serve p2p)
                "p2p start": CommandInfo(
                    CommandType.SERVER,
                    P2PRequirement.SERVER_ONLY,
                    supports_streaming=False,
                    paths_from_args=["paths"],
                    description="Start P2P management",
                ),
                "p2p stop": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Stop P2P management"
                ),
                "p2p status": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="P2P management status"
                ),
                "p2p query": CommandInfo(
                    CommandType.UTILITY, P2PRequirement.NEVER, description="Query P2P network"
                ),
            }
        )

        logger.info(f"Initialized command classifier with {len(self.command_registry)} commands")

    def classify_command(self, command_name: str, subcommand: Optional[str] = None) -> CommandInfo:
        """Classify a command and return its P2P routing information."""
        # Build full command name
        if subcommand:
            full_command = f"{command_name} {subcommand}"
        else:
            full_command = command_name

        # Look up in registry
        if full_command in self.command_registry:
            return self.command_registry[full_command]

        # Fallback: try just the main command
        if command_name in self.command_registry:
            return self.command_registry[command_name]

        # Default: assume source-touching if not known
        logger.warning(f"Unknown command '{full_command}', assuming source-touching")
        return CommandInfo(
            CommandType.SOURCE_TOUCHING,
            P2PRequirement.OPTIONAL,
            supports_streaming=False,
            description=f"Unknown command: {full_command}",
        )

    def extract_paths_from_args(self, command_info: CommandInfo, args: Dict) -> List[str]:
        """Extract file/directory paths from command arguments."""
        paths = []

        for path_arg in command_info.paths_from_args:
            if path_arg in args and args[path_arg] is not None:
                arg_value = args[path_arg]

                # Handle single path
                if isinstance(arg_value, str):
                    paths.append(arg_value)
                # Handle list of paths
                elif isinstance(arg_value, list):
                    paths.extend(str(p) for p in arg_value)
                # Handle Path objects
                elif hasattr(arg_value, "__fspath__"):
                    paths.append(str(arg_value))

        return paths

    def should_route_to_p2p(
        self, command_name: str, subcommand: Optional[str] = None, args: Optional[Dict] = None
    ) -> bool:
        """Determine if a command should be routed through P2P."""
        command_info = self.classify_command(command_name, subcommand)
        return command_info.needs_p2p_check()

    def should_start_p2p(self, command_name: str, subcommand: Optional[str] = None) -> bool:
        """Determine if a command should trigger P2P startup."""
        command_info = self.classify_command(command_name, subcommand)
        return command_info.triggers_p2p_startup()

    def needs_streaming(self, command_name: str, subcommand: Optional[str] = None) -> bool:
        """Determine if a command needs streaming support."""
        command_info = self.classify_command(command_name, subcommand)
        return command_info.needs_streaming_support()

    def get_command_paths(
        self, command_name: str, subcommand: Optional[str] = None, args: Optional[Dict] = None
    ) -> List[str]:
        """Get the paths that a command operates on."""
        if args is None:
            return []

        command_info = self.classify_command(command_name, subcommand)
        return self.extract_paths_from_args(command_info, args)

    def get_source_touching_commands(self) -> List[str]:
        """Get all commands that touch source files."""
        return [
            cmd
            for cmd, info in self.command_registry.items()
            if info.command_type in [CommandType.SOURCE_TOUCHING, CommandType.STREAMING]
        ]

    def get_streaming_commands(self) -> List[str]:
        """Get all commands that support streaming."""
        return [cmd for cmd, info in self.command_registry.items() if info.supports_streaming]

    def get_server_commands(self) -> List[str]:
        """Get all server/daemon commands."""
        return [
            cmd
            for cmd, info in self.command_registry.items()
            if info.command_type == CommandType.SERVER
        ]
