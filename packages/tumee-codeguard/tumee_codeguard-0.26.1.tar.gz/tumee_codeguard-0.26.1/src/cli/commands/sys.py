"""
CLI commands for system status and management.

Provides system-level commands for monitoring proxy status,
active connections, and system health.
"""

import asyncio
import json
import logging
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from ...core.formatters import FormatterRegistry
from ...core.formatters.base import DataType
from ...core.runtime import get_default_console
from ...utils.logging_config import get_logger

logger = get_logger(__name__)
console = get_default_console()

# Create sys CLI group
sys_app = typer.Typer(name="sys", help="System status and management commands")


@sys_app.command("status")
async def status_command(
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    include_health_check: bool = typer.Option(
        True, "--health-check/--no-health-check", help="Include upstream health checks"
    ),
    include_system_info: bool = typer.Option(
        True, "--system-info/--no-system-info", help="Include system resource information"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    Show comprehensive system and proxy status.

    Displays information about:
    - Proxy server health and configuration
    - Active connections and sessions
    - Registered plugins and hooks
    - System resource information
    - Upstream service connectivity

    Examples:
      codeguard sys status
      codeguard sys status --format json
      codeguard sys status --no-health-check --format yaml
    """

    async def _get_status():
        try:
            # Collect system status information
            status_data = await _collect_system_status(
                include_health_check=include_health_check,
                include_system_info=include_system_info,
                verbose=verbose,
            )

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if not formatter:
                # Fallback to JSON formatter for unknown formats
                formatter = FormatterRegistry.get_formatter("json")

            if output_format.lower() == "text" and not output:
                # Special handling for text format to console
                _display_status_table(status_data, verbose=verbose, quiet=quiet)
            else:
                # Use formatter for other formats or file output
                if not formatter:
                    raise RuntimeError("No formatter available")
                formatted_output = await formatter.format_collection(
                    [status_data], DataType.P2P_STATUS
                )

                if output:
                    output.write_text(formatted_output)
                    if not quiet:
                        console.print(f"Status report written to {output}")
                else:
                    console.print(formatted_output)

        except Exception as e:
            logger.error(f"Error getting system status: {e}", exc_info=True)
            console.print(f"[red]Error getting system status: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(_get_status())


async def _collect_system_status(
    include_health_check: bool = True, include_system_info: bool = True, verbose: bool = False
) -> Dict:
    """
    Collect comprehensive system status information.

    Returns:
        Dictionary containing status information
    """
    import os
    import platform
    from datetime import timezone

    status_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proxy": {"status": "unknown", "version": "1.0.0", "configuration": {}},
        "plugins": {"registered_count": 0, "active_hooks": [], "statistics": {}},
        "sessions": {"active_count": 0, "total_processed": 0},
    }

    # Check if proxy server is running
    proxy_status = await _check_proxy_status()
    status_data["proxy"].update(proxy_status)

    # Get plugin information
    plugin_info = await _get_plugin_information()
    status_data["plugins"].update(plugin_info)

    # Get session information (if available)
    session_info = await _get_session_information()
    status_data["sessions"].update(session_info)

    # Include upstream health checks if requested
    if include_health_check:
        upstream_health = await _check_upstream_health()
        status_data["upstream"] = upstream_health

    # Include system information if requested
    if include_system_info:
        try:
            system_info = _get_system_information()
            status_data["system"] = system_info
        except ImportError as e:
            status_data["system"] = {
                "error": f"System monitoring requires psutil: {e}",
                "message": "Install with: pip install psutil",
            }

    return status_data


async def _check_proxy_status() -> Dict:
    """Check if the LLM proxy server is running and accessible."""
    try:
        # Try to connect to default proxy ports
        proxy_ports = [8080, 8443, 3001]  # Common proxy ports
        proxy_host = "localhost"

        for port in proxy_ports:
            try:
                # Try to connect to the proxy health endpoint
                import aiohttp

                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                    async with session.get(f"http://{proxy_host}:{port}/health") as response:
                        if response.status == 200:
                            health_data = await response.json()
                            return {
                                "status": "running",
                                "host": proxy_host,
                                "port": port,
                                "health": health_data,
                                "accessible": True,
                            }
            except Exception:
                continue

        # If no proxy found running, check if process exists
        return {
            "status": "not_running",
            "accessible": False,
            "message": "No proxy server found on common ports",
        }

    except Exception as e:
        return {"status": "error", "error": str(e), "accessible": False}


async def _get_plugin_information() -> Dict:
    """Get information about registered plugins and hooks."""
    try:
        # This would ideally connect to the proxy to get real plugin info
        # For now, return static information about expected plugins
        return {
            "registered_count": 2,
            "active_hooks": ["prompt:", "sys:"],
            "expected_plugins": [
                {"name": "prompt_chat", "hook": "prompt:", "status": "expected"},
                {"name": "sys_chat", "hook": "sys:", "status": "expected"},
            ],
            "statistics": {"prompt_commands_processed": 0, "sys_commands_processed": 0},
        }
    except Exception as e:
        logger.error(f"Error getting plugin information: {e}")
        return {"error": str(e), "registered_count": 0, "active_hooks": []}


async def _get_session_information() -> Dict:
    """Get information about active sessions."""
    try:
        # This would connect to the MCP server to get session info
        # For now, return basic session information
        return {
            "active_count": 0,
            "total_processed": 0,
            "message": "Session data requires MCP server connection",
        }
    except Exception as e:
        return {"error": str(e), "active_count": 0}


async def _check_upstream_health() -> Dict:
    """Check health of upstream services (Anthropic, OpenAI, etc.)."""
    upstreams = {"anthropic": "https://api.anthropic.com", "openai": "https://api.openai.com"}

    health_results = {}

    for name, base_url in upstreams.items():
        try:
            # Simple connectivity check
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(
                    f"{base_url}/v1/health", headers={"User-Agent": "CodeGuard-Status-Check"}
                ) as response:
                    health_results[name] = {
                        "status": "reachable" if response.status < 500 else "degraded",
                        "response_time_ms": 0,  # Would measure actual time
                        "status_code": response.status,
                    }
        except Exception as e:
            health_results[name] = {"status": "unreachable", "error": str(e)}

    return health_results


def _get_system_information() -> Dict:
    """Get system resource information."""
    try:
        import platform

        import psutil

        # Get basic system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
            "resources": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": round((disk.used / disk.total) * 100, 1),
                },
            },
            "network": {"hostname": socket.gethostname(), "fqdn": socket.getfqdn()},
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not collect system information"}


def _display_status_table(status_data: Dict, verbose: bool = False, quiet: bool = False):
    """Display status information in a formatted table for console output."""
    if quiet:
        # Quiet mode: just show basic status
        proxy_status = status_data.get("proxy", {}).get("status", "unknown")
        console.print(f"Proxy: {proxy_status}")
        return

    # Main status table
    table = Table(title="CodeGuard System Status", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Details", style="white")

    # Proxy status
    proxy = status_data.get("proxy", {})
    proxy_status = proxy.get("status", "unknown")
    status_color = (
        "green" if proxy_status == "running" else "red" if proxy_status == "error" else "yellow"
    )

    proxy_details = ""
    if proxy.get("host") and proxy.get("port"):
        proxy_details = f"{proxy['host']}:{proxy['port']}"
    elif proxy.get("message"):
        proxy_details = proxy["message"]

    table.add_row("Proxy Server", f"[{status_color}]{proxy_status}[/{status_color}]", proxy_details)

    # Plugin status
    plugins = status_data.get("plugins", {})
    plugin_count = plugins.get("registered_count", 0)
    hooks = plugins.get("active_hooks", [])
    hooks_str = ", ".join(hooks) if hooks else "none"

    table.add_row("Plugins", f"[blue]{plugin_count} registered[/blue]", f"Hooks: {hooks_str}")

    # Session status
    sessions = status_data.get("sessions", {})
    active_sessions = sessions.get("active_count", 0)
    total_processed = sessions.get("total_processed", 0)

    table.add_row(
        "Sessions", f"[blue]{active_sessions} active[/blue]", f"Total processed: {total_processed}"
    )

    # Upstream status (if included)
    if "upstream" in status_data:
        upstream = status_data["upstream"]
        upstream_statuses = []
        for service, health in upstream.items():
            status = health.get("status", "unknown")
            color = "green" if status == "reachable" else "red"
            upstream_statuses.append(f"[{color}]{service}[/{color}]")

        table.add_row("Upstream", "Health Check", ", ".join(upstream_statuses))

    # System resources (if included and verbose)
    if verbose and "system" in status_data:
        system = status_data["system"]
        if "resources" in system:
            resources = system["resources"]
            cpu = resources.get("cpu_percent", 0)
            memory = resources.get("memory", {})
            memory_pct = memory.get("percent_used", 0)

            cpu_color = "green" if cpu < 50 else "yellow" if cpu < 80 else "red"
            memory_color = "green" if memory_pct < 50 else "yellow" if memory_pct < 80 else "red"

            table.add_row(
                "System Resources",
                f"[{cpu_color}]CPU: {cpu}%[/{cpu_color}]",
                f"[{memory_color}]Memory: {memory_pct}%[/{memory_color}]",
            )

    console.print(table)

    # Additional information if verbose
    if verbose:
        console.print(f"\n[bold]Timestamp:[/bold] {status_data.get('timestamp', 'unknown')}")

        if "system" in status_data and "platform" in status_data["system"]:
            platform_info = status_data["system"]["platform"]
            console.print(
                f"[bold]Platform:[/bold] {platform_info.get('system', 'unknown')} {platform_info.get('release', '')}"
            )
