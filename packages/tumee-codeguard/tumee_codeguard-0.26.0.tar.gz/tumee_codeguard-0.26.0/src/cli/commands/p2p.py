"""
P2P commands for CodeGuard CLI.

This module implements the 'p2p' command group for P2P path management
and coordination between CodeGuard instances.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
import yaml
from rich.console import Console

from ...core.config import ConfigEditor, ConfigScope
from ...core.console_shared import CONSOLE, output_mode
from ...core.exit_codes import SUCCESS, UNEXPECTED_ERROR
from ...core.formatters import DataType, FormatterRegistry
from ...core.runtime import get_default_console
from ...servers.p2p_server import HierarchicalNetworkManager
from ...servers.p2p_server.cli_utils import handle_monitor, handle_query
from ...servers.p2p_server.config import P2PConfig, get_p2p_service
from ...servers.p2p_server.exceptions import P2PError, PathConflictError
from ...utils.logging_config import get_logger, setup_cli_logging
from ...utils.signal_handlers import create_shutdown_manager

# Configure logger to output to console
logger = get_logger(__name__)
setup_cli_logging(logger)

console = get_default_console()

# Create the p2p sub-app
p2p_app = typer.Typer(
    name="p2p", help="P2P path management and coordination between CodeGuard instances"
)


@p2p_app.command("query")
def p2p_query(
    paths: Optional[List[Path]] = typer.Argument(None, help="Paths to query ownership for"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all registered paths"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="P2P configuration file"),
    timeout: int = typer.Option(5, "--timeout", help="Query timeout in seconds"),
    output_format: str = typer.Option(
        "console", "--output-format", help="Output format (console, table, json, yaml)"
    ),
):
    """Query who owns specific paths in the P2P network."""
    try:
        # Load configuration
        service = get_p2p_service()
        config = service.load_config()

        if not show_all and not paths:
            console.print("[red]❌ Error:[/red] Must specify paths to query or use --all")
            logger.error("P2P query failed: No paths specified and --all not used")
            return UNEXPECTED_ERROR

        path_strs = [str(p.absolute()) for p in paths] if paths else []

        console.print("🔍 Querying P2P network...")

        # Run the async query
        async def main():
            try:
                # For now, we'll call the original handle_query but should be updated to return structured data
                await handle_query(path_strs, show_all, config, timeout)

                # TODO: Update handle_query to return structured data instead of printing directly
                # Then use: _display_p2p_results(query_results, DataType.P2P_NODE_LIST, output_format)

                return SUCCESS
            except P2PError as e:
                console.print(f"[red]❌ P2P error:[/red] {e}")
                logger.exception("P2P query failed", exc_info=e)
                return UNEXPECTED_ERROR

        return asyncio.run(main())

    except Exception as e:
        console.print(f"[red]❌ Error querying P2P network:[/red] {e}")
        logger.exception("P2P query failed", exc_info=e)
        return UNEXPECTED_ERROR


@p2p_app.command("list")
def p2p_list(
    config_file: Optional[Path] = typer.Option(None, "--config", help="P2P configuration file"),
    timeout: int = typer.Option(5, "--timeout", help="Discovery timeout in seconds"),
    output_format: str = typer.Option(
        "console", "--output-format", help="Output format (console, table, json, yaml)"
    ),
):
    """List all active P2P instances and their managed paths."""
    try:
        console.print("📋 Listing all P2P instances...")

        # This is equivalent to query --all
        return p2p_query(
            paths=None,
            show_all=True,
            config_file=config_file,
            timeout=timeout,
            output_format=output_format,
        )

    except Exception as e:
        console.print(f"[red]❌ Error listing P2P instances:[/red] {e}")
        logger.exception("P2P list failed", exc_info=e)
        return UNEXPECTED_ERROR


@p2p_app.command("stop")
def p2p_stop(
    paths: Optional[List[Path]] = typer.Argument(
        None, help="Paths to stop managing (all if none specified)"
    ),
    config_file: Optional[Path] = typer.Option(None, "--config", help="P2P configuration file"),
    force: bool = typer.Option(False, "--force", help="Force stop without confirmation"),
):
    """Stop the local P2P manager instance."""
    try:
        if not force:
            confirm = typer.confirm("Are you sure you want to stop the P2P manager?")
            if not confirm:
                console.print("❌ Operation cancelled")
                return SUCCESS

        console.print("🛑 Stopping P2P manager...")

        # For now, this is a placeholder - we'd need to implement process management
        # to find and stop running instances
        console.print("⚠️  Stop command not yet fully implemented")
        console.print("💡 Use Ctrl+C to stop running instances manually")

        return SUCCESS

    except Exception as e:
        console.print(f"[red]❌ Error stopping P2P manager:[/red] {e}")
        logger.exception("P2P stop failed", exc_info=e)
        return UNEXPECTED_ERROR


@p2p_app.command("status")
def p2p_status(
    config_file: Optional[Path] = typer.Option(None, "--config", help="P2P configuration file"),
    output_format: str = typer.Option(
        "console", "--output-format", help="Output format (console, table, json, yaml)"
    ),
):
    """Show status of P2P network and local node."""
    try:
        console.print("📊 Checking P2P network status...")

        # Load configuration
        service = get_p2p_service()
        config = service.load_config()

        # Create status data structure
        status_data = {
            "config": {
                "discovery_port": config.discovery_port,
                "port_range_start": config.port_range_start,
                "port_range_end": config.port_range_end,
                "broadcast_interval": config.broadcast_interval,
                "node_timeout": config.node_timeout,
                "force_registration": config.force_registration,
                "managed_paths": config.managed_paths,
            }
        }

        # Use formatter system
        _display_p2p_results([status_data], DataType.P2P_STATUS, output_format)

        # Query network for active instances
        console.print("\n🔍 Active network instances:")
        return p2p_list(config_file=config_file, output_format=output_format)

    except Exception as e:
        console.print(f"[red]❌ Error checking P2P status:[/red] {e}")
        logger.exception("P2P status check failed", exc_info=e)
        return UNEXPECTED_ERROR


@p2p_app.command("monitor")
def p2p_monitor(
    timeout: int = typer.Option(0, "--timeout", help="Monitor timeout in seconds (0 = forever)"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="P2P configuration file"),
):
    """Monitor P2P network join/leave events in real-time."""
    try:
        # Load configuration
        service = get_p2p_service()
        config = service.load_config()

        console.print("🔍 Monitoring P2P network for join/leave events...")
        console.print("⏹️ Press 'q' to quit, 'l' to list nodes, or Ctrl+C to stop monitoring")

        # Run the async monitor
        async def main():
            try:
                await handle_monitor(config, timeout)
                return SUCCESS
            except KeyboardInterrupt:
                console.print("\n🛑 Monitoring stopped by user")
                return SUCCESS
            except P2PError as e:
                console.print(f"[red]❌ P2P error:[/red] {e}")
                logger.exception("P2P monitor failed", exc_info=e)
                return UNEXPECTED_ERROR

        return asyncio.run(main())

    except Exception as e:
        console.print(f"[red]❌ Error monitoring P2P network:[/red] {e}")
        logger.exception("P2P monitor failed", exc_info=e)
        return UNEXPECTED_ERROR


@p2p_app.command("config")
def p2p_config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", help="Edit configuration file"),
    create: bool = typer.Option(False, "--create", help="Create default configuration file"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Configuration file path"),
):
    """Manage P2P configuration."""
    try:
        if create:
            # Create default configuration
            service = get_p2p_service()

            if config_file:
                config_path = config_file
                if config_path.exists():
                    overwrite = typer.confirm(
                        f"Configuration file {config_path} already exists. Overwrite?"
                    )
                    if not overwrite:
                        console.print("❌ Operation cancelled")
                        return SUCCESS

                # Create default config and save to specific file
                config = P2PConfig()
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, "w") as f:
                    yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)
            else:
                # Use service to create user config
                service.reset_to_defaults(ConfigScope.USER)
                config_path = service.get_save_path(ConfigScope.USER)

            console.print(f"✅ Created default configuration at {config_path}")

        elif show:
            # Show current configuration
            service = get_p2p_service()
            config = service.load_config()
            console.print("📋 Current P2P Configuration:")
            console.print(f"  Discovery port: {config.discovery_port}")
            console.print(f"  Port range: {config.port_range_start}-{config.port_range_end}")
            console.print(f"  Broadcast interval: {config.broadcast_interval}s")
            console.print(f"  Health check interval: {config.health_check_interval}s")
            console.print(f"  Node timeout: {config.node_timeout}s")
            console.print(f"  Bind host: {config.bind_host}")
            console.print(f"  Force registration: {config.force_registration}")
            console.print(f"  Delegate file: {config.delegate_file_name}")
            console.print(f"  Managed paths: {config.managed_paths or 'None'}")

        elif edit:
            # Edit configuration
            service = get_p2p_service()
            editor = ConfigEditor(service)

            if config_file:
                # For specific config file, edit it directly
                if not config_file.exists():
                    create_new = typer.confirm(
                        f"Configuration file {config_file} does not exist. Create it?"
                    )
                    if create_new:
                        config = P2PConfig()
                        config_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(config_file, "w") as f:
                            yaml.dump(
                                config.model_dump(), f, default_flow_style=False, sort_keys=False
                            )
                    else:
                        console.print("❌ Operation cancelled")
                        return SUCCESS

                # Try to open with system editor
                editor_cmd = os.environ.get("EDITOR", "nano")
                os.system(f"{editor_cmd} {config_file}")
                console.print(f"✅ Configuration file edited: {config_file}")
            else:
                # Use service editor for user config
                if editor.edit_config(ConfigScope.USER):
                    console.print("✅ Configuration updated successfully")
                else:
                    console.print("❌ Configuration edit failed")

        else:
            console.print("❌ Please specify --show, --edit, or --create")
            logger.error("P2P config command failed: No action specified")
            return UNEXPECTED_ERROR

        return SUCCESS

    except Exception as e:
        console.print(f"[red]❌ Error managing configuration:[/red] {e}")
        logger.exception("P2P config management failed")
        return UNEXPECTED_ERROR


def _display_p2p_results(data: List[dict], data_type: DataType, output_format: str):
    """Display P2P results using the unified formatter system."""

    # Get the appropriate formatter
    formatter = FormatterRegistry.get_formatter(output_format)
    if not formatter:
        console.print(f"[red]Error: Unknown output format '{output_format}'[/red]")
        console.print(f"Available formats: {FormatterRegistry.get_available_formats()}")
        return

    # Check if formatter supports the data type
    if not formatter.supports_data_type(data_type):
        console.print(
            f"[red]Error: {output_format} formatter doesn't support {data_type.value}[/red]"
        )
        return

    # Format the results
    try:
        import asyncio

        formatted_output = asyncio.run(formatter.format_collection(data, data_type))

        # Print to console
        print(formatted_output, end="")

    except Exception as e:
        console.print(f"[red]Error formatting results: {e}[/red]")
        logger.exception("Formatting error")
