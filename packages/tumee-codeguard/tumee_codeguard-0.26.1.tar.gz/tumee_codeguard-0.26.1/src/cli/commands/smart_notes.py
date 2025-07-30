"""
CLI commands for smart notes management.

Provides command-line interface to add, list, snooze, remove, and toggle smart notes
that show contextually based on conditions and frequency.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import typer
from rich.console import Console
from rich.table import Table

from ...core.formatters import FormatterRegistry
from ...core.formatters.base import DataType
from ...core.runtime import get_default_console

logger = logging.getLogger(__name__)
console = get_default_console()

# Create smart notes CLI group
smart_app = typer.Typer(name="smart", help="Manage smart notes with contextual display")


@smart_app.command("add")
async def add_smart_note(
    content: str = typer.Argument(help="The smart note content"),
    category: str = typer.Option(
        "general",
        "--category",
        "-c",
        help="Note category (general, warning, setup, cleanup, process)",
    ),
    priority: int = typer.Option(
        1, "--priority", "-p", help="Priority level 1-5 (higher = more important)"
    ),
    show_every: int = typer.Option(1, "--show-every", "-e", help="Show note every N tool calls"),
    conditions: Optional[str] = typer.Option(
        None, "--conditions", help="JSON conditions for when to show note"
    ),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    Add a new smart note that shows based on conditions and frequency.

    Examples:
      codeguard smart add "Check staging DB connection" --show-every 5
      codeguard smart add "Warning: Test environment" --category warning --priority 3
      codeguard smart add "Setup: Run migrations" --category setup --conditions '{"tools": ["database"]}'
    """

    async def _add_note():
        try:
            # Import MCP tools to interact with smart notes system
            from ...servers.mcp_server.mcp_server import mcp
            from ...servers.mcp_server.tools.smart_planning_notes import smart_note

            # Parse conditions if provided
            parsed_conditions = None
            if conditions:
                import json

                try:
                    parsed_conditions = json.loads(conditions)
                except json.JSONDecodeError:
                    console.print("[red]Error: Invalid JSON format for conditions[/red]")
                    raise typer.Exit(1)

            # Create a mock context for the CLI call
            class MockContext:
                def __init__(self):
                    self.session = {}

                def get_session_state(self):
                    return self.session

                def set_session_state(self, state):
                    self.session = state

            mock_ctx = MockContext()

            # Add the smart note using the MCP tool
            result = await smart_note(
                session_id=session_id,
                content=content,
                category=category,
                priority=max(1, min(5, priority)),  # Clamp to 1-5
                show_every_n_calls=show_every,
                conditions=parsed_conditions,
                ctx=mock_ctx,
            )

            # Check for errors
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

            # Prepare output data
            result_data = {
                "status": "success",
                "note_id": result["note_id"],
                "content": content,
                "category": category,
                "priority": priority,
                "show_frequency": result["show_frequency"],
                "conditions": result["conditions"],
                "message": result["message"],
            }

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if not formatter:
                # Fallback to JSON formatter for unknown formats
                formatter = FormatterRegistry.get_formatter("json")

            if not formatter:
                raise RuntimeError("No formatter available")

            formatted_output = await formatter.format_collection(
                [result_data], DataType.SMART_NOTES
            )

            if output:
                output.write_text(formatted_output)
            else:
                console.print(formatted_output)

        except Exception as e:
            console.print(f"[red]Error adding smart note: {e}[/red]")
            raise typer.Exit(1)

    await _add_note()


@smart_app.command("list")
async def list_smart_notes(
    active_only: bool = typer.Option(True, "--active-only/--all", help="Show only active notes"),
    include_snoozed: bool = typer.Option(False, "--include-snoozed", help="Include snoozed notes"),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    List smart notes for the session.

    Examples:
      codeguard smart list
      codeguard smart list --all --include-snoozed --format json
    """

    async def _list_notes():
        try:
            # Import MCP tools
            from ...servers.mcp_server.tools.smart_planning_notes import smart_list_notes

            # Create mock context
            class MockContext:
                def __init__(self):
                    self.session = {}

                def get_session_state(self):
                    return self.session

                def set_session_state(self, state):
                    self.session = state

            mock_ctx = MockContext()

            # List smart notes using the MCP tool
            result = await smart_list_notes(
                session_id=session_id,
                active_only=active_only,
                include_snoozed=include_snoozed,
                ctx=mock_ctx,
            )

            # Check for errors
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if not formatter:
                formatter = FormatterRegistry.get_formatter("json")

            if not formatter:
                raise RuntimeError("No formatter available")

            formatted_output = await formatter.format_collection([result], DataType.SMART_NOTES)

            if output:
                output.write_text(formatted_output)
            elif output_format.lower() != "text":
                console.print(formatted_output)
            else:
                # Text format (Rich console) - show table
                notes = result.get("notes", [])
                if not notes:
                    if not quiet:
                        console.print("[yellow]No smart notes found.[/yellow]")
                    return

                if not quiet:
                    # Create table
                    table = Table(title=f"Smart Notes ({result['total_count']} total)")
                    table.add_column("ID", style="cyan", no_wrap=True)
                    table.add_column("Priority", justify="center")
                    table.add_column("Category", style="magenta")
                    table.add_column("Content", style="white")
                    table.add_column("Frequency", style="blue")
                    table.add_column("Status", justify="center")

                    # Add rows
                    for note in notes:
                        # Status with color
                        if not note.get("active", True):
                            status_display = "[red]Inactive[/red]"
                        elif note.get("snoozed", False):
                            status_display = "[yellow]Snoozed[/yellow]"
                        else:
                            status_display = "[green]Active[/green]"

                        # Priority with color
                        priority = note["priority"]
                        if priority >= 4:
                            priority_display = f"[red]{priority}[/red]"
                        elif priority >= 3:
                            priority_display = f"[yellow]{priority}[/yellow]"
                        else:
                            priority_display = f"[green]{priority}[/green]"

                        table.add_row(
                            note["id"][:8] + "...",  # Truncate ID
                            priority_display,
                            note["category"],
                            note["content"][:50] + ("..." if len(note["content"]) > 50 else ""),
                            note["show_frequency"],
                            status_display,
                        )

                    console.print(table)

                    # Category and status summary
                    categories = result.get("categories", {})
                    if categories:
                        console.print(
                            f"\\n[bold]By category:[/bold] {', '.join(f'{cat}: {count}' for cat, count in categories.items())}"
                        )

                    snoozed_count = result.get("snoozed_count", 0)
                    if snoozed_count > 0:
                        console.print(f"[bold]Snoozed notes:[/bold] {snoozed_count}")

        except Exception as e:
            console.print(f"[red]Error listing smart notes: {e}[/red]")
            raise typer.Exit(1)

    await _list_notes()


@smart_app.command("snooze")
async def snooze_smart_note(
    note_id: Optional[str] = typer.Option(None, "--id", help="Specific note ID to snooze"),
    content_contains: Optional[str] = typer.Option(
        None, "--contains", help="Snooze notes containing this text"
    ),
    minutes: Optional[int] = typer.Option(None, "--minutes", "-m", help="Snooze for N minutes"),
    calls: Optional[int] = typer.Option(None, "--calls", "-c", help="Snooze for N tool calls"),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    Temporarily hide smart notes by time or call count.

    Examples:
      codeguard smart snooze --id abc123 --minutes 60
      codeguard smart snooze --contains "staging" --calls 10
    """
    if not note_id and not content_contains:
        console.print("[red]Error: Must specify either --id or --contains[/red]")
        raise typer.Exit(1)

    if not minutes and not calls:
        console.print("[red]Error: Must specify either --minutes or --calls[/red]")
        raise typer.Exit(1)

    async def _snooze_note():
        try:
            # Import MCP tools
            from ...servers.mcp_server.tools.smart_planning_notes import smart_snooze_note

            # Create mock context
            class MockContext:
                def __init__(self):
                    self.session = {}

                def get_session_state(self):
                    return self.session

                def set_session_state(self, state):
                    self.session = state

            mock_ctx = MockContext()

            # Snooze smart note using the MCP tool
            result = await smart_snooze_note(
                session_id=session_id,
                note_id=note_id,
                content_contains=content_contains,
                snooze_for_minutes=minutes,
                snooze_for_calls=calls,
                ctx=mock_ctx,
            )

            # Check for errors
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if not formatter:
                formatter = FormatterRegistry.get_formatter("json")

            if not formatter:
                raise RuntimeError("No formatter available")

            formatted_output = await formatter.format_collection([result], DataType.SMART_NOTES)

            if output:
                output.write_text(formatted_output)
            else:
                console.print(formatted_output)

        except Exception as e:
            console.print(f"[red]Error snoozing smart note: {e}[/red]")
            raise typer.Exit(1)

    await _snooze_note()


@smart_app.command("remove")
async def remove_smart_notes(
    note_id: Optional[str] = typer.Option(None, "--id", help="Specific note ID to remove"),
    content_contains: Optional[str] = typer.Option(
        None, "--contains", help="Remove notes containing this text"
    ),
    category: Optional[str] = typer.Option(None, "--category", help="Remove notes by category"),
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
    Remove smart notes by ID, content, or category.

    Examples:
      codeguard smart remove --id abc123
      codeguard smart remove --contains "staging"
      codeguard smart remove --category warning --yes
    """
    if not note_id and not content_contains and not category:
        console.print("[red]Error: Must specify either --id, --contains, or --category[/red]")
        raise typer.Exit(1)

    async def _remove_notes():
        try:
            # Import MCP tools
            from ...servers.mcp_server.tools.smart_planning_notes import smart_remove_note

            # Create mock context
            class MockContext:
                def __init__(self):
                    self.session = {}

                def get_session_state(self):
                    return self.session

                def set_session_state(self, state):
                    self.session = state

            mock_ctx = MockContext()

            # Preview what will be removed if not confirmed
            if not confirm:
                # First list matching notes
                from ...servers.mcp_server.tools.smart_planning_notes import smart_list_notes

                all_notes_result = await smart_list_notes(
                    session_id=session_id, active_only=False, include_snoozed=True, ctx=mock_ctx
                )

                matching_notes = []
                for note in all_notes_result.get("notes", []):
                    if note_id and note["id"] == note_id:
                        matching_notes.append(note)
                    elif content_contains and content_contains.lower() in note["content"].lower():
                        matching_notes.append(note)
                    elif category and note["category"] == category:
                        matching_notes.append(note)

                if not matching_notes:
                    console.print("[yellow]No matching notes found.[/yellow]")
                    return

                console.print(f"[yellow]Found {len(matching_notes)} matching note(s):[/yellow]")
                for note in matching_notes:
                    console.print(
                        f"  • {note['content'][:80]}{'...' if len(note['content']) > 80 else ''}"
                    )

                if not typer.confirm("Remove these notes?"):
                    console.print("Cancelled.")
                    return

            # Remove smart notes using the MCP tool
            result = await smart_remove_note(
                session_id=session_id,
                note_id=note_id,
                content_contains=content_contains,
                category=category,
                ctx=mock_ctx,
            )

            # Check for errors
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if not formatter:
                formatter = FormatterRegistry.get_formatter("json")

            if not formatter:
                raise RuntimeError("No formatter available")

            formatted_output = await formatter.format_collection([result], DataType.SMART_NOTES)

            if output:
                output.write_text(formatted_output)
            else:
                console.print(formatted_output)

        except Exception as e:
            console.print(f"[red]Error removing smart notes: {e}[/red]")
            raise typer.Exit(1)

    await _remove_notes()


@smart_app.command("toggle")
async def toggle_smart_note(
    note_id: str = typer.Argument(help="Note ID to toggle"),
    active: Optional[bool] = typer.Option(None, "--active/--inactive", help="Set active state"),
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    output_format: str = typer.Option(
        "text", "--format", "-f", help="Output format: text, json, yaml"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Quiet mode (minimal output)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode (detailed output)"),
):
    """
    Toggle smart note active/inactive state.

    Examples:
      codeguard smart toggle abc123
      codeguard smart toggle abc123 --active
      codeguard smart toggle abc123 --inactive
    """

    async def _toggle_note():
        try:
            # Import MCP tools
            from ...servers.mcp_server.tools.smart_planning_notes import smart_toggle_note

            # Create mock context
            class MockContext:
                def __init__(self):
                    self.session = {}

                def get_session_state(self):
                    return self.session

                def set_session_state(self, state):
                    self.session = state

            mock_ctx = MockContext()

            # Toggle smart note using the MCP tool
            result = await smart_toggle_note(
                session_id=session_id, note_id=note_id, active=active, ctx=mock_ctx
            )

            # Check for errors
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

            # Use CodeGuard formatter system
            formatter = FormatterRegistry.get_formatter(output_format.lower())
            if not formatter:
                formatter = FormatterRegistry.get_formatter("json")

            if not formatter:
                raise RuntimeError("No formatter available")

            formatted_output = await formatter.format_collection([result], DataType.SMART_NOTES)

            if output:
                output.write_text(formatted_output)
            else:
                console.print(formatted_output)

        except Exception as e:
            console.print(f"[red]Error toggling smart note: {e}[/red]")
            raise typer.Exit(1)

    await _toggle_note()


@smart_app.command("clear")
async def clear_all_smart_notes(
    session_id: str = typer.Option("default", "--session", "-s", help="Session ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """
    Remove ALL smart notes from the session.

    This is a destructive operation that cannot be undone.
    """
    if not confirm:
        if not typer.confirm("[red]Remove ALL smart notes? This cannot be undone.[/red]"):
            console.print("Cancelled.")
            return

    async def _clear_notes():
        try:
            # Import MCP tools
            from ...servers.mcp_server.tools.smart_planning_notes import smart_remove_note

            # Create mock context
            class MockContext:
                def __init__(self):
                    self.session = {}

                def get_session_state(self):
                    return self.session

                def set_session_state(self, state):
                    self.session = state

            mock_ctx = MockContext()

            # Remove all notes by using empty content filter (matches all)
            result = await smart_remove_note(
                session_id=session_id,
                note_id=None,
                content_contains="",  # This will match all notes
                category=None,
                ctx=mock_ctx,
            )

            # Check for errors
            if "error" in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                raise typer.Exit(1)

            console.print(f"[green]✓[/green] Cleared {result['removed_count']} smart note(s)")

        except Exception as e:
            console.print(f"[red]Error clearing smart notes: {e}[/red]")
            raise typer.Exit(1)

    await _clear_notes()
