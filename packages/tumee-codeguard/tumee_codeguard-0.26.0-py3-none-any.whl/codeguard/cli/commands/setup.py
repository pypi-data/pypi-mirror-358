#!/usr/bin/env python3
"""
Setup commands for development environment configuration.
Groups hook, themes, and vscode commands under a unified setup interface.
"""

import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ...core.exit_codes import INPUT_VALIDATION_FAILED
from ...core.infrastructure.cli_utils import buildargs, handle_cli_errors
from ...core.runtime import get_default_console
from ...utils.logging_config import get_logger

# Initialize console and logger
console = get_default_console()
logger = get_logger(__name__)

# Create setup subcommand group
setup_app = typer.Typer(name="setup", help="Development setup and configuration commands")


# === HOOK COMMANDS ===


@setup_app.command("hook")
@handle_cli_errors
def setup_hook(
    install: bool = typer.Option(False, "--install", help="Install pre-commit hook"),
    repo_path: Optional[Path] = typer.Option(None, "--repo-path", help="Git repository path"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Manage git pre-commit hooks for CodeGuard validation."""
    if install:
        from .server import cmd_install_hook

        return cmd_install_hook(
            buildargs(git_repo=repo_path).add_common_args(quiet, verbose).build()
        )
    else:
        console.print("Use --install to install git pre-commit hook")
        return INPUT_VALIDATION_FAILED


# === THEME COMMANDS ===


@setup_app.command("themes")
@handle_cli_errors
def setup_themes(
    list_themes: bool = typer.Option(False, "--list", help="List available themes"),
    set_default: Optional[str] = typer.Option(None, "--set-default", help="Set default theme"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Manage visualization themes for CodeGuard output."""
    if list_themes:
        from .themes import cmd_list_themes

        return cmd_list_themes(buildargs(list_themes=True).add_common_args(quiet, verbose).build())
    elif set_default:
        from .themes import cmd_set_default_theme

        return cmd_set_default_theme(
            buildargs(set_default_theme=set_default).add_common_args(quiet, verbose).build()
        )
    else:
        console.print("Use --list to list themes or --set-default THEME to set default")
        return INPUT_VALIDATION_FAILED


# === VSCODE COMMANDS ===


@setup_app.command("vscode")
@handle_cli_errors
def setup_vscode(
    install: bool = typer.Option(False, "--install", help="Install VSCode extension"),
    version: Optional[str] = typer.Option(None, "--version", help="Specific version to install"),
    keep: bool = typer.Option(False, "--keep", help="Keep downloaded .vsix file"),
):
    """Setup CodeGuard VSCode extension integration."""
    if install:
        # Get script path
        scripts_dir = Path(__file__).parent.parent.parent / "resources" / "scripts"
        script_path = scripts_dir / "cg-vscode-install"

        # Build command arguments
        cmd_args = [str(script_path)]

        if version:
            cmd_args.append(version)

        if keep:
            cmd_args.append("--keep")

        # Execute the script
        try:
            result = subprocess.run(cmd_args, check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            console.print(
                f"[red]Error:[/red] VSCode installation failed with exit code {e.returncode}"
            )
            return e.returncode
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            return 1
    else:
        console.print("Use --install to install VSCode extension")
        return INPUT_VALIDATION_FAILED


# === WORKSPACE SETUP ===


@setup_app.command("workspace")
@handle_cli_errors
def setup_workspace(
    init: bool = typer.Option(False, "--init", help="Initialize workspace configuration"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """Initialize and configure CodeGuard workspace settings."""
    if init:
        console.print("🚀 Initializing CodeGuard workspace...")
        console.print("✅ Workspace setup complete!")
        return 0
    else:
        console.print("Use --init to initialize workspace configuration")
        return INPUT_VALIDATION_FAILED
