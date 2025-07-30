"""
Unified configuration commands for CodeGuard CLI.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console

from ...core.config import ConfigEditor, ConfigScope
from ...core.exit_codes import SUCCESS, UNEXPECTED_ERROR
from ...core.runtime import get_default_console

logger = logging.getLogger(__name__)
console = get_default_console()

# Create the config sub-app
config_app = typer.Typer(name="config", help="Manage configuration for various CodeGuard services")


@config_app.command("show")
def config_show(
    service: str = typer.Argument(..., help="Service name (p2p, refactor)"),
):
    """Show current configuration for a service."""
    try:
        service_map = {
            "p2p": lambda: __import__(
                "src.servers.p2p_server.config", fromlist=["get_p2p_service"]
            ).get_p2p_service(),
            "refactor": lambda: __import__(
                "src.context.config", fromlist=["get_refactor_service"]
            ).get_refactor_service(),
        }

        if service not in service_map:
            console.print(f"[red]❌ Unknown service: {service}[/red]")
            console.print(f"Available services: {', '.join(service_map.keys())}")
            logger.error(f"Unknown service: {service}")
            return UNEXPECTED_ERROR

        config_service = service_map[service]()
        config = config_service.load_config()

        console.print(f"📋 Current {service.upper()} Configuration:")
        console.print(yaml.dump(config.model_dump(), default_flow_style=False, sort_keys=False))

        return SUCCESS

    except Exception as e:
        console.print(f"[red]❌ Error showing {service} configuration:[/red] {e}")
        logger.exception(f"Error showing {service} configuration", exc_info=e)
        return UNEXPECTED_ERROR


@config_app.command("edit")
def config_edit(
    service: str = typer.Argument(..., help="Service name (p2p, refactor)"),
    scope: str = typer.Option("user", "--scope", help="Configuration scope (user, project, local)"),
):
    """Edit configuration for a service."""
    try:
        service_map = {
            "p2p": lambda: __import__(
                "src.servers.p2p_server.config", fromlist=["get_p2p_service"]
            ).get_p2p_service(),
            "refactor": lambda: __import__(
                "src.context.config", fromlist=["get_refactor_service"]
            ).get_refactor_service(),
        }

        if service not in service_map:
            console.print(f"[red]❌ Unknown service: {service}[/red]")
            console.print(f"Available services: {', '.join(service_map.keys())}")
            logger.error(f"Unknown service: {service}")
            return UNEXPECTED_ERROR

        try:
            config_scope = ConfigScope(scope)
        except ValueError as ve:
            console.print(f"[red]❌ Invalid scope: {scope}[/red]")
            console.print(f"Available scopes: {', '.join([s.value for s in ConfigScope])}")
            logger.exception(f"Invalid scope: {scope}", exc_info=ve)
            return UNEXPECTED_ERROR

        config_service = service_map[service]()
        editor = ConfigEditor(config_service)

        console.print(f"✏️ Editing {service} configuration ({scope} scope)...")

        if editor.edit_config(config_scope):
            console.print("✅ Configuration updated successfully")
        else:
            console.print("❌ Configuration edit failed")
            logger.error(f"Configuration edit failed for {service} ({scope} scope)")
            return UNEXPECTED_ERROR

        return SUCCESS

    except Exception as e:
        console.print(f"[red]❌ Error editing {service} configuration:[/red] {e}")
        logger.exception(f"Error editing {service} configuration", exc_info=e)
        return UNEXPECTED_ERROR


@config_app.command("reset")
def config_reset(
    service: str = typer.Argument(..., help="Service name (p2p, refactor)"),
    scope: str = typer.Option("user", "--scope", help="Configuration scope (user, project, local)"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
):
    """Reset configuration to defaults for a service."""
    try:
        service_map = {
            "p2p": lambda: __import__(
                "src.servers.p2p_server.config", fromlist=["get_p2p_service"]
            ).get_p2p_service(),
            "refactor": lambda: __import__(
                "src.context.config", fromlist=["get_refactor_service"]
            ).get_refactor_service(),
        }

        if service not in service_map:
            console.print(f"[red]❌ Unknown service: {service}[/red]")
            console.print(f"Available services: {', '.join(service_map.keys())}")
            logger.error(f"Unknown service: {service}")
            return UNEXPECTED_ERROR

        try:
            config_scope = ConfigScope(scope)
        except ValueError:
            console.print(f"[red]❌ Invalid scope: {scope}[/red]")
            console.print(f"Available scopes: {', '.join([s.value for s in ConfigScope])}")
            logger.error(f"Invalid scope: {scope}")
            return UNEXPECTED_ERROR

        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to reset {service} configuration ({scope} scope) to defaults?"
            )
            if not confirm:
                console.print("❌ Operation cancelled")
                return SUCCESS

        config_service = service_map[service]()

        if config_service.reset_to_defaults(config_scope):
            console.print(
                f"✅ {service.capitalize()} configuration reset to defaults ({scope} scope)"
            )
        else:
            console.print(f"❌ Failed to reset {service} configuration")
            logger.error(f"Failed to reset {service} configuration ({scope} scope)")
            return UNEXPECTED_ERROR

        return SUCCESS

    except Exception as e:
        console.print(f"[red]❌ Error resetting {service} configuration:[/red] {e}")
        logger.exception(f"Error resetting {service} configuration", exc_info=e)
        return UNEXPECTED_ERROR


@config_app.command("debug")
def config_debug(
    service: str = typer.Argument(..., help="Service name (p2p, refactor)"),
):
    """Show configuration hierarchy and debug information for a service."""
    try:
        service_map = {
            "p2p": lambda: __import__(
                "src.servers.p2p_server.config", fromlist=["get_p2p_service"]
            ).get_p2p_service(),
            "refactor": lambda: __import__(
                "src.context.config", fromlist=["get_refactor_service"]
            ).get_refactor_service(),
        }

        if service not in service_map:
            console.print(f"[red]❌ Unknown service: {service}[/red]")
            console.print(f"Available services: {', '.join(service_map.keys())}")
            logger.error(f"Unknown service: {service}")
            return UNEXPECTED_ERROR

        config_service = service_map[service]()

        # Show hierarchy
        console.print(config_service.show_hierarchy())
        console.print()

        # Show save paths for each scope
        console.print("💾 Save locations:")
        for scope in ConfigScope:
            save_path = config_service.get_save_path(scope)
            exists = "✓" if save_path.exists() else "✗"
            console.print(f"  {scope.value:8} {exists} {save_path}")

        return SUCCESS

    except Exception as e:
        console.print(f"[red]❌ Error debugging {service} configuration:[/red] {e}")
        logger.exception(f"Error debugging {service} configuration", exc_info=e)
        return UNEXPECTED_ERROR


@config_app.command("list")
def config_list():
    """List all available configuration services."""
    console.print("📋 Available configuration services:")
    console.print()

    services = {
        "p2p": "P2P network configuration for path management and coordination",
        "refactor": "Refactor urgency analysis configuration for scoring weights and thresholds",
    }

    for service_name, description in services.items():
        console.print(f"  [cyan]{service_name:10}[/cyan] {description}")

    console.print()
    console.print("💡 Use 'codeguard config show <service>' to view current configuration")
    console.print("💡 Use 'codeguard config edit <service>' to edit configuration")

    return SUCCESS
