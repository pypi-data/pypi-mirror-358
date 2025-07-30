"""
Worker Mode implementation for CodeGuard CLI.
Provides persistent, high-performance parser service via JSON over stdin/stdout.

This is the main orchestrator that coordinates all IDE server components.
"""

from typing import Optional

from ..servers.ide_server import DocumentManager, RPCServer
from ..servers.ide_server.command_handlers.document_commands import DocumentCommandHandler
from ..servers.ide_server.command_handlers.gitignore_commands import GitignoreCommandHandler
from ..servers.ide_server.command_handlers.lsp_commands import LSPCommandHandler
from ..servers.ide_server.command_handlers.system_commands import SystemCommandHandler
from ..servers.ide_server.command_handlers.theme_commands import ThemeCommandHandler
from .template_generator import GitignoreTemplateGenerator
from .workspace_analyzer import WorkspaceAnalyzer
from .workspace_file_analyzer import WorkspaceFileAnalyzer


class WorkerModeProcessor:
    """
    Main processor for worker mode operations.

    This orchestrator coordinates all IDE server components including
    RPC communication, document management, and command handling.
    """

    def __init__(self, min_version: Optional[str] = None):
        """
        Initialize the worker mode processor.

        Args:
            min_version: Minimum required version for compatibility checking
        """
        # Initialize core components
        self.rpc_server = RPCServer(min_version)
        self.document_manager = DocumentManager()

        # Initialize workspace analysis components
        self.workspace_analyzer = WorkspaceAnalyzer()
        self.template_generator = GitignoreTemplateGenerator(self.workspace_analyzer)
        self.workspace_file_analyzer = WorkspaceFileAnalyzer()

        # Initialize command handlers
        self.system_handler = SystemCommandHandler(self.rpc_server, min_version)
        self.document_handler = DocumentCommandHandler(self.rpc_server, self.document_manager)
        self.theme_handler = ThemeCommandHandler(self.rpc_server)
        self.gitignore_handler = GitignoreCommandHandler(
            self.rpc_server,
            self.workspace_analyzer,
            self.template_generator,
            self.workspace_file_analyzer,
        )
        self.lsp_handler = LSPCommandHandler(self.rpc_server)

        # Register command handlers with the RPC server
        self._register_handlers()

    def _register_handlers(self):
        """Register all command handlers with the RPC server"""
        # System commands
        self.rpc_server.register_handler("version", self.system_handler)
        self.rpc_server.register_handler("ping", self.system_handler)
        self.rpc_server.register_handler("shutdown", self.system_handler)

        # Document commands
        self.rpc_server.register_handler("setDocument", self.document_handler)
        self.rpc_server.register_handler("applyDelta", self.document_handler)

        # Theme commands
        self.rpc_server.register_handler("getThemes", self.theme_handler)
        self.rpc_server.register_handler("createTheme", self.theme_handler)
        self.rpc_server.register_handler("updateTheme", self.theme_handler)
        self.rpc_server.register_handler("deleteTheme", self.theme_handler)
        self.rpc_server.register_handler("exportTheme", self.theme_handler)
        self.rpc_server.register_handler("importTheme", self.theme_handler)
        self.rpc_server.register_handler("getCurrentTheme", self.theme_handler)
        self.rpc_server.register_handler("setCurrentTheme", self.theme_handler)

        # Gitignore commands
        self.rpc_server.register_handler("getGitignoreSuggestions", self.gitignore_handler)
        self.rpc_server.register_handler("getGitignoreTemplate", self.gitignore_handler)
        self.rpc_server.register_handler("getWorkspaceGitignoreSuggestions", self.gitignore_handler)

        # LSP commands (pattern-based)
        self.rpc_server.register_handler("lsp", self.lsp_handler)

    def run(self):
        """Main worker mode loop"""
        self.rpc_server.run()


def start_worker_mode(min_version: Optional[str] = None):
    """Start worker mode with optional minimum version requirement"""
    processor = WorkerModeProcessor(min_version)
    processor.run()
