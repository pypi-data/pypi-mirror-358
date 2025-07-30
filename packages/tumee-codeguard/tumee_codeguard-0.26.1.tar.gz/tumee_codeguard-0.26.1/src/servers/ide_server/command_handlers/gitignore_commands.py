"""
Gitignore command handlers for IDE Server.

This module contains handlers for gitignore-related operations including
pattern suggestions, template generation, and workspace-based analysis.
"""

import time
from pathlib import Path
from typing import Any, Dict

from ....ide.gitignore_patterns import gitignore_patterns_db


class GitignoreCommandHandler:
    """
    Handles gitignore-related commands for the IDE server.

    This class provides gitignore pattern suggestions, template generation,
    and workspace-specific gitignore analysis capabilities.
    """

    def __init__(self, rpc_server, workspace_analyzer, template_generator, workspace_file_analyzer):
        """
        Initialize the gitignore command handler.

        Args:
            rpc_server: The RPC server instance for sending responses
            workspace_analyzer: WorkspaceAnalyzer for workspace analysis
            template_generator: GitignoreTemplateGenerator for template generation
            workspace_file_analyzer: WorkspaceFileAnalyzer for file analysis
        """
        self.rpc_server = rpc_server
        self.workspace_analyzer = workspace_analyzer
        self.template_generator = template_generator
        self.workspace_file_analyzer = workspace_file_analyzer

    def handle_getGitignoreSuggestions_command(self, request: Dict[str, Any]) -> None:
        """Handle getGitignoreSuggestions command"""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            start_time = time.time()

            # Extract parameters from payload
            prefix = payload.get("prefix", "")
            context = payload.get("context", "file")

            # Validate context parameter
            valid_contexts = ["file", "folder", "template"]
            if context not in valid_contexts:
                self.rpc_server._send_error_response(
                    request_id,
                    f"Invalid context '{context}'. Must be one of: {', '.join(valid_contexts)}",
                    "INVALID_CONTEXT",
                )
                return

            # Search for matching patterns
            suggestions = gitignore_patterns_db.search_patterns(prefix, context)

            # Limit results to prevent overwhelming the client
            max_suggestions = 50
            if len(suggestions) > max_suggestions:
                suggestions = suggestions[:max_suggestions]

            result = {"suggestions": suggestions}

            timing = time.time() - start_time
            self.rpc_server._send_success_response(request_id, result, timing)

        except Exception as e:
            self.rpc_server._send_error_response(
                request_id, f"Failed to get gitignore suggestions: {str(e)}", "GITIGNORE_ERROR"
            )

    async def handle_getGitignoreTemplate_command(self, request: Dict[str, Any]) -> None:
        """Handle getGitignoreTemplate command"""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            start_time = time.time()

            # Extract parameters from payload
            workspace_path_str = payload.get("workspacePath", "")
            context = payload.get("context", "template")

            # Validate workspace path
            if not workspace_path_str:
                self.rpc_server._send_error_response(
                    request_id, "workspacePath parameter is required", "MISSING_WORKSPACE_PATH"
                )
                return

            # Validate context parameter
            valid_contexts = ["template", "default", "detected"]
            if context not in valid_contexts:
                self.rpc_server._send_error_response(
                    request_id,
                    f"Invalid context '{context}'. Must be one of: {', '.join(valid_contexts)}",
                    "INVALID_CONTEXT",
                )
                return

            # Convert to Path and validate
            try:
                workspace_path = Path(workspace_path_str).resolve()
                if not workspace_path.exists():
                    self.rpc_server._send_error_response(
                        request_id,
                        f"Workspace path does not exist: {workspace_path_str}",
                        "WORKSPACE_NOT_FOUND",
                    )
                    return

                if not workspace_path.is_dir():
                    self.rpc_server._send_error_response(
                        request_id,
                        f"Workspace path is not a directory: {workspace_path_str}",
                        "WORKSPACE_NOT_DIRECTORY",
                    )
                    return

            except Exception as e:
                self.rpc_server._send_error_response(
                    request_id, f"Invalid workspace path: {str(e)}", "INVALID_WORKSPACE_PATH"
                )
                return

            # Generate template
            template_content = await self.template_generator.generate_template(
                workspace_path, context
            )

            result = {"template": template_content}

            timing = time.time() - start_time
            self.rpc_server._send_success_response(request_id, result, timing)

        except Exception as e:
            self.rpc_server._send_error_response(
                request_id,
                f"Failed to generate gitignore template: {str(e)}",
                "TEMPLATE_GENERATION_ERROR",
            )

    async def handle_getWorkspaceGitignoreSuggestions_command(
        self, request: Dict[str, Any]
    ) -> None:
        """Handle getWorkspaceGitignoreSuggestions command"""
        request_id = request.get("id", "")
        payload = request.get("payload", {})

        try:
            start_time = time.time()

            # Extract parameters from payload
            prefix = payload.get("prefix", "")
            workspace_path_str = payload.get("workspacePath", "")
            context = payload.get("context", "file")
            max_suggestions = payload.get("maxSuggestions", 20)

            # Validate workspace path
            if not workspace_path_str:
                self.rpc_server._send_error_response(
                    request_id, "workspacePath parameter is required", "MISSING_WORKSPACE_PATH"
                )
                return

            # Validate context parameter
            valid_contexts = ["file", "folder", "template"]
            if context not in valid_contexts:
                self.rpc_server._send_error_response(
                    request_id,
                    f"Invalid context '{context}'. Must be one of: {', '.join(valid_contexts)}",
                    "INVALID_CONTEXT",
                )
                return

            # Validate max_suggestions
            if not isinstance(max_suggestions, int) or max_suggestions < 1 or max_suggestions > 100:
                self.rpc_server._send_error_response(
                    request_id,
                    "maxSuggestions must be an integer between 1 and 100",
                    "INVALID_MAX_SUGGESTIONS",
                )
                return

            # Convert to Path and validate
            try:
                workspace_path = Path(workspace_path_str).resolve()
                if not workspace_path.exists():
                    self.rpc_server._send_error_response(
                        request_id,
                        f"Workspace path does not exist: {workspace_path_str}",
                        "WORKSPACE_NOT_FOUND",
                    )
                    return

                if not workspace_path.is_dir():
                    self.rpc_server._send_error_response(
                        request_id,
                        f"Workspace path is not a directory: {workspace_path_str}",
                        "WORKSPACE_NOT_DIRECTORY",
                    )
                    return

            except Exception as e:
                self.rpc_server._send_error_response(
                    request_id, f"Invalid workspace path: {str(e)}", "INVALID_WORKSPACE_PATH"
                )
                return

            # Get workspace-based suggestions
            suggestions = await self.workspace_file_analyzer.get_workspace_suggestions(
                prefix, workspace_path, context, max_suggestions
            )

            result = {"suggestions": suggestions}

            timing = time.time() - start_time
            self.rpc_server._send_success_response(request_id, result, timing)

        except Exception as e:
            self.rpc_server._send_error_response(
                request_id, f"Failed to analyze workspace: {str(e)}", "WORKSPACE_ANALYSIS_ERROR"
            )
