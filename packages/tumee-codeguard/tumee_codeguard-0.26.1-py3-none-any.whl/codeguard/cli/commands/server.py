"""
Server and utility CLI commands for CodeGuard.
Handles MCP server, git hooks, and section validation.
"""

import argparse
import sys

# MCP server imports are intentionally delayed to avoid initialization unless MCP mode is used
from ...vcs.git_integration import GitError, GitIntegration


def cmd_install_hook(args: argparse.Namespace) -> int:
    """
    Execute the 'install-hook' command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    repo_path = args.git_repo if args.git_repo else None

    # Initialize git integration
    try:
        git = GitIntegration(repo_path)
    except GitError as e:
        print(f"Error: {str(e)}")
        return 1

    # Install pre-commit hook
    try:
        hook_path = git.install_pre_commit_hook()
        print(f"Pre-commit hook installed: {hook_path}")
        return 0
    except Exception as e:
        print(f"Error installing pre-commit hook: {str(e)}")
        return 1


def cmd_mcp(args: argparse.Namespace) -> int:
    """
    Execute the 'mcp' command to start the MCP server.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Import MCP server components only when actually starting MCP mode
        from ...servers.mcp_server.mcp_server import mcp, register_tools
        from ...servers.mcp_server.runtime.server import run_server_cli

        # Register MCP tools only when starting the server
        register_tools()

        transport = args.transport
        host = args.host
        port = args.port

        print(f"Starting CodeGuard MCP server...")
        print(f"Transport: {transport}")
        if transport != "stdio":
            print(f"Host: {host}")
            print(f"Port: {port}")

        run_server_cli(mcp_instance=mcp, transport=transport, host=host, port=port)
        return 0
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}")
        return 1


def cmd_ide(args: argparse.Namespace) -> int:
    """
    Execute the 'ide' command to start IDE attachment mode.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        from ...ide.worker_mode import start_worker_mode

        min_version = getattr(args, "min_version", None)
        start_worker_mode(min_version)
        return 0
    except Exception as e:
        print(f"Error: IDE mode failed: {str(e)}", file=sys.stderr)
        return 1
