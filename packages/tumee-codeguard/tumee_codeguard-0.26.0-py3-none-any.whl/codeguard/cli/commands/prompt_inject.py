"""
CLI commands for prompt injection management.

Provides command-line interface to add, list, and remove prompt injection rules
using natural language commands that mirror the MCP prompt_inject tool.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ...core.formatters import FormatterRegistry
from ...core.formatters.base import DataType
from ...core.runtime import get_default_console
from ...servers.mcp_server.tools.modules.prompt_inject_core import PromptInjectManager
from ...servers.mcp_server.tools.prompt_inject import PromptInjectParser

logger = logging.getLogger(__name__)
console = get_default_console()

# Create prompt injection CLI group
prompt_app = typer.Typer(name="prompt", help="Manage prompt injection rules with natural language")


@prompt_app.command("add")
async def add_prompt_rule(
    rule: str = typer.Argument(help="Natural language rule (e.g., 'use staging database (24h)')"),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    force_category: Optional[str] = typer.Option(
        None, "--force-category", help="Override auto-detected category"
    ),
    force_priority: Optional[int] = typer.Option(
        None, "--force-priority", help="Override auto-detected priority (1-5)"
    ),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    Add a new prompt injection rule using natural language.

    The rule text is parsed for duration, priority, and category automatically.

    Examples:
      codeguard prompt add "use staging database (24h)"
      codeguard prompt add "never commit secrets (permanent)"
      codeguard prompt add "activate virtual environment"
      codeguard prompt add "run tests after changes (session)"
    """

    async def _add_rule():
        try:
            manager = PromptInjectManager()
            parser = PromptInjectParser()

            # Parse the natural language rule
            command = f"add: {rule}"
            parsed = parser.parse_command(command)

            if parsed["action"] != "add":
                console.print(f"[red]Error: Failed to parse rule as add command[/red]")
                raise typer.Exit(1)

            # Apply force overrides if provided
            category = force_category or parsed.get("category", "general")
            priority = force_priority or parsed.get("priority", 1)
            expires_in_hours = parsed.get("expires_in_hours")

            # Add the rule
            prompt_rule = await manager.add_rule(
                session_id=session_id,
                content=parsed["content"],
                expires_in_hours=expires_in_hours,
                category=category,
                priority=max(1, min(5, priority)),  # Clamp to 1-5
            )

            # Prepare output data
            expiry_info = "session"
            if prompt_rule.expires_at:
                expiry_info = f"expires {prompt_rule.expires_at.strftime('%Y-%m-%d %H:%M UTC')}"
            elif expires_in_hours:
                expiry_info = f"expires in {expires_in_hours} hours"

            result_data = {
                "status": "success",
                "rule_id": prompt_rule.id,
                "content": parsed["content"],
                "category": category,
                "priority": priority,
                "expiration": expiry_info,
                "created_at": prompt_rule.created_at.isoformat(),
                "parsed_from": rule,
            }

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if not formatter:
                formatter = FormatterRegistry.get_formatter("json")

            if not formatter:
                raise RuntimeError("No formatter available")

            formatted_output = await formatter.format_collection(
                [result_data], DataType.PROMPT_INJECT_RULES
            )

            if output:
                output.write_text(formatted_output)
                if not quiet:
                    console.print(f"Rule added and saved to {output}")
            else:
                if output_format.lower() == "text" and not quiet:
                    console.print(
                        f"[green]✓[/green] Added prompt rule: [bold]{parsed['content']}[/bold]"
                    )
                    console.print(f"  Category: {category} | Priority: {priority} | {expiry_info}")
                    if rule != parsed["content"]:
                        console.print(f"  [dim]Parsed from: {rule}[/dim]")
                else:
                    console.print(formatted_output)

        except Exception as e:
            console.print(f"[red]Error adding prompt rule: {e}[/red]")
            if verbose:
                console.print(f"[dim]Rule text: {rule}[/dim]")
            raise typer.Exit(1)

    await _add_rule()


@prompt_app.command("list")
async def list_prompt_rules(
    show_all: bool = typer.Option(False, "--all", help="Show all rules including expired"),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    List prompt injection rules for the session.

    Examples:
      codeguard prompt list
      codeguard prompt list --all
      codeguard prompt list --session my-project
    """

    async def _list_rules():
        try:
            manager = PromptInjectManager()
            rules = await manager.list_rules(
                session_id=session_id, active_only=not show_all, include_expired=show_all
            )

            # Prepare data for output
            rules_data = []
            now = datetime.now()
            categories = {}

            for rule in rules:
                # Status
                if not rule.active:
                    status = "inactive"
                elif rule.expires_at and rule.expires_at < now:
                    status = "expired"
                else:
                    status = "active"

                # Expiration
                expires_str = (
                    rule.expires_at.strftime("%Y-%m-%d %H:%M") if rule.expires_at else "session"
                )

                rule_data = {
                    "id": rule.id,
                    "content": rule.content,
                    "category": rule.category,
                    "priority": rule.priority,
                    "status": status,
                    "expires": expires_str,
                    "created_at": rule.created_at.isoformat(),
                }
                rules_data.append(rule_data)
                categories[rule.category] = categories.get(rule.category, 0) + 1

            result_data = {
                "rules": rules_data,
                "total_count": len(rules_data),
                "categories": categories,
                "filters": {"show_all": show_all, "session_id": session_id},
            }

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if formatter:
                if output:
                    formatted_output = await formatter.format_collection(
                        [result_data], DataType.PROMPT_INJECT_RULES
                    )
                    output.write_text(formatted_output)
                    if not quiet:
                        console.print(f"Output written to {output}")
                elif output_format.lower() != "text":
                    formatted_output = await formatter.format_collection(
                        [result_data], DataType.PROMPT_INJECT_RULES
                    )
                    console.print(formatted_output)
                else:
                    # Text format (Rich console) - show table
                    if not rules:
                        if not quiet:
                            console.print("[yellow]No prompt rules found.[/yellow]")
                            console.print(f'[dim]Try: codeguard prompt add "your rule here"[/dim]')
                        return

                    if not quiet:
                        # Create table
                        table = Table(title=f"Prompt Injection Rules ({len(rules)} total)")
                        table.add_column("ID", style="cyan", no_wrap=True)
                        table.add_column("Priority", justify="center")
                        table.add_column("Category", style="magenta")
                        table.add_column("Content", style="white")
                        table.add_column("Status", justify="center")
                        table.add_column("Expires", style="yellow")

                        # Add rows
                        for rule_data in rules_data:
                            # Status with color
                            status = rule_data["status"]
                            if status == "inactive":
                                status_display = "[red]Inactive[/red]"
                            elif status == "expired":
                                status_display = "[red]Expired[/red]"
                            else:
                                status_display = "[green]Active[/green]"

                            # Priority with color
                            priority = rule_data["priority"]
                            if priority >= 4:
                                priority_display = f"[red]{priority}[/red]"
                            elif priority >= 3:
                                priority_display = f"[yellow]{priority}[/yellow]"
                            else:
                                priority_display = f"[green]{priority}[/green]"

                            # Expires with color
                            expires = rule_data["expires"]
                            if expires != "session" and status == "expired":
                                expires_display = f"[red]{expires}[/red]"
                            else:
                                expires_display = expires

                            table.add_row(
                                rule_data["id"][:8] + "...",  # Truncate ID
                                priority_display,
                                rule_data["category"],
                                rule_data["content"][:60]
                                + ("..." if len(rule_data["content"]) > 60 else ""),
                                status_display,
                                expires_display,
                            )

                        console.print(table)

                        # Category summary
                        if categories:
                            console.print(
                                f"\n[bold]By category:[/bold] {', '.join(f'{cat}: {count}' for cat, count in categories.items())}"
                            )

                        # Usage hints
                        console.print(
                            f'\n[dim]💡 Add rules: codeguard prompt add "use staging db (24h)"[/dim]'
                        )
            else:
                if not quiet:
                    console.print(f"[red]Error: Unknown output format '{output_format}'[/red]")
                    console.print(
                        f"Available formats: {', '.join(FormatterRegistry.get_available_formats())}"
                    )
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error listing prompt rules: {e}[/red]")
            raise typer.Exit(1)

    await _list_rules()


@prompt_app.command("remove")
async def remove_prompt_rules(
    search_term: str = typer.Argument(help="Search term to find rules to remove"),
    rule_id: Optional[str] = typer.Option(None, "--id", help="Specific rule ID to remove"),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    Remove prompt injection rules by search term or ID.

    Examples:
      codeguard prompt remove "staging"
      codeguard prompt remove "database" --yes
      codeguard prompt remove --id abc123def
    """

    async def _remove_rules():
        try:
            manager = PromptInjectManager()

            # Use either rule_id or search_term
            search_criteria = rule_id or search_term

            # Preview what will be removed
            if not confirm:
                # List matching rules first
                all_rules = await manager.list_rules(
                    session_id=session_id, active_only=False, include_expired=True
                )

                matching_rules = []
                for rule in all_rules:
                    if rule_id and rule.id == rule_id:
                        matching_rules.append(rule)
                    elif not rule_id and search_term.lower() in rule.content.lower():
                        matching_rules.append(rule)

                if not matching_rules:
                    console.print(f"[yellow]No rules found matching '{search_criteria}'.[/yellow]")
                    return

                console.print(f"[yellow]Found {len(matching_rules)} matching rule(s):[/yellow]")
                for rule in matching_rules:
                    console.print(
                        f"  • {rule.content[:80]}{'...' if len(rule.content) > 80 else ''}"
                    )

                if not typer.confirm("Remove these rules?"):
                    console.print("Cancelled.")
                    return

            # Remove the rules
            removed_rules = await manager.remove_rule(
                session_id=session_id,
                rule_id=rule_id,
                content_contains=search_term if not rule_id else None,
            )

            if removed_rules:
                console.print(f"[green]✓[/green] Removed {len(removed_rules)} prompt rule(s):")
                for rule in removed_rules:
                    console.print(f"  • {rule.content}")
            else:
                console.print(f"[yellow]No rules found matching '{search_criteria}'.[/yellow]")

        except Exception as e:
            console.print(f"[red]Error removing prompt rules: {e}[/red]")
            raise typer.Exit(1)

    await _remove_rules()


@prompt_app.command("clear")
async def clear_prompt_rules(
    target: str = typer.Argument(
        default="temp",
        help="What to clear: 'temp' (temporary), 'all' (everything), 'expired' (expired only)",
    ),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """
    Clear prompt injection rules by type.

    Examples:
      codeguard prompt clear temp    # Clear temporary rules
      codeguard prompt clear all     # Clear all rules
      codeguard prompt clear expired # Clear expired rules only
    """
    if target not in ["temp", "all", "expired"]:
        console.print(f"[red]Error: Invalid target '{target}'. Use: temp, all, or expired[/red]")
        raise typer.Exit(1)

    if not confirm:
        if target == "all":
            if not typer.confirm("[red]Remove ALL prompt rules? This cannot be undone.[/red]"):
                console.print("Cancelled.")
                return
        else:
            if not typer.confirm(f"Remove all {target} prompt rules?"):
                console.print("Cancelled.")
                return

    async def _clear_rules():
        try:
            manager = PromptInjectManager()

            # Get all rules first to filter by target
            all_rules = await manager.list_rules(
                session_id=session_id, active_only=False, include_expired=True
            )

            if not all_rules:
                console.print("[yellow]No prompt rules to clear.[/yellow]")
                return

            # Determine which rules to remove based on target
            rules_to_remove = []
            now = datetime.now()

            for rule in all_rules:
                if target == "all":
                    rules_to_remove.append(rule)
                elif target == "temp" and rule.expires_at:
                    rules_to_remove.append(rule)
                elif target == "expired" and rule.expires_at and rule.expires_at < now:
                    rules_to_remove.append(rule)

            if not rules_to_remove:
                console.print(f"[yellow]No {target} prompt rules found.[/yellow]")
                return

            # Remove rules one by one (PromptInjectManager doesn't have bulk clear)
            removed_count = 0
            for rule in rules_to_remove:
                removed_rules = await manager.remove_rule(session_id=session_id, rule_id=rule.id)
                if removed_rules:
                    removed_count += len(removed_rules)

            console.print(f"[green]✓[/green] Cleared {removed_count} {target} prompt rule(s)")

        except Exception as e:
            console.print(f"[red]Error clearing prompt rules: {e}[/red]")
            raise typer.Exit(1)

    await _clear_rules()
