"""
Context Scanner CLI Command

Provides CLI interface for intelligent code context analysis and management,
using the shared context engine that's also used by MCP and chat commands.
"""

import asyncio
import io
import json
import logging
import os
from pathlib import Path
from typing import Optional

from rich.table import Table

# Import component system
from ...cli.components import ComponentArgumentParser, ComponentDisplay
from ...context import components  # This auto-registers all context components
from ...context.models import AnalysisMode
from ...context.modules import (
    get_module_primary_language_display,
    get_module_primary_language_from_dict,
)
from ...context.scanner import CodeGuardContextScanner
from ...core.caching.manager import get_cache_manager as get_global_cache_manager
from ...core.components import ComponentParameterError
from ...core.console_shared import cprint
from ...core.decorators.filesystem import with_filesystem_access
from ...core.exit_codes import (
    CONFIG_VALIDATION_FAILED,
    DIRECTORY_NOT_FOUND,
    GENERAL_ERROR,
    SUCCESS,
    USAGE_ERROR,
    VALIDATION_FAILED,
)
from ...core.filesystem.path_utils import normalize_path_for_storage
from ...core.formatters import DataType, FormatterRegistry
from ...core.formatters.console import ConsoleFormatter
from ...core.infrastructure.cli_utils import handle_cli_errors, is_python_src_invocation
from ...core.interfaces import IFileSystemAccess, IStaticAnalyzer
from ...core.output import OutputManager
from ...core.progress.progress_factory import setup_unified_progress
from ...core.runtime import get_current_command_id, get_default_console, is_worker_process
from ...utils.logging_config import get_logger

logger = get_logger(__name__)
console = OutputManager()


async def display_results_with_components(
    analysis_result, component_specs, output_format, output_file, console_instance
):
    """Shared function to display results using component system - eliminates code duplication."""
    component_display = ComponentDisplay()
    command_id = get_current_command_id()  # None for local execution

    if output_format.lower() == "json":
        # JSON: stream each component individually via streaming protocol
        for idx, (component_name, params) in enumerate(component_specs):
            await component_display.generate_streaming_single_component(
                analysis_result, component_name, params, command_id
            )
            # Clear spinner after each component completes (consistent with non-JSON mode)
            cprint("")  # Clear spinner and move to new line
    else:
        # All other formats: process component by component using formatter system
        registry = FormatterRegistry()
        formatter = registry.get_formatter(output_format)

        if formatter:
            file_handle = output_file.open("w") if output_file else None
            try:
                for idx, (component_name, params) in enumerate(component_specs):
                    # First component: clear any spinner and move to new line
                    if idx == 0:
                        cprint("")  # Clear spinner and move to new line

                    # Get component data
                    component_json = await component_display.generate_json_single_component(
                        analysis_result, component_name, params
                    )

                    # Use formatter to render - this handles row_mapping/transforms correctly
                    formatted_output = await formatter.format_collection(
                        component_json, DataType.ANALYSIS_RESULTS
                    )

                    if file_handle:
                        file_handle.write(formatted_output + "\n")
                        file_handle.flush()  # Immediate write
                    else:
                        console_instance.print(formatted_output, end="")
            finally:
                if file_handle:
                    file_handle.close()
                    console_instance.print(f"[green]Results saved to {output_file}[/green]")
                else:
                    cprint("")
        else:
            console_instance.print(f"[red]Formatter for {output_format} not available[/red]")


@handle_cli_errors
@with_filesystem_access()
async def cmd_context_analyze(
    directory: Path,
    filesystem_access: IFileSystemAccess,
    components: Optional[str] = None,
    output_level: Optional[str] = None,  # Legacy support
    analysis_mode: str = "FULL",
    max_depth: int = 3,
    output_format: str = "console",
    output_file: Optional[Path] = None,
    no_cache: bool = False,
    cache_only: bool = False,
    sort_by: str = "importance",
    verbose: bool = False,
    show_progress: Optional[bool] = None,
) -> int:
    """
    Analyze project context using the intelligent context scanner.

    Args:
        directory: Project directory to analyze
        components: Component specifications (e.g., "summary,dependency_graph" or "project_summary,ai_modules:20")
        output_level: Legacy output level (deprecated, use --components instead)
        analysis_mode: Analysis mode (FULL, INCREMENTAL)
        max_depth: Maximum directory traversal depth
        output_format: Output format (console, json, yaml, text)
        output_file: Optional file to save results
        no_cache: Skip cache and force fresh analysis
        cache_only: Only use cached data, fail if no cache available
        sort_by: Sort modules by 'files' or 'importance' (deprecated, use component parameters)
        verbose: Show all modules without truncation (deprecated, use component parameters)
        show_progress: Show progress during analysis (defaults based on output format)
    """
    try:
        # Validate directory
        if not directory.exists() or not directory.is_dir():
            console.print(
                f"[red]Error: Directory {directory} does not exist or is not a directory[/red]"
            )
            return DIRECTORY_NOT_FOUND

        # Validate conflicting flags
        if no_cache and cache_only:
            console.print("[red]Error: Cannot use both --no-cache and --cache-only[/red]")
            return USAGE_ERROR

        # Handle component arguments vs legacy output_level
        if components and output_level:
            console.print(
                "[red]Error: Cannot use both --components and --output-level. Use --components for new syntax.[/red]"
            )
            return USAGE_ERROR

        # Set up component parsing
        component_parser = ComponentArgumentParser()
        component_display = ComponentDisplay()

        # Parse components argument or use default
        if components:
            try:
                component_specs = component_parser.parse_components_argument(components)
            except ComponentParameterError as e:
                console.print(f"[red]Error in --components argument: {e}[/red]")
                available_components = component_parser.list_available_components()
                available_presets = component_parser.list_available_presets()
                console.print(f"Available components: {', '.join(available_components)}")
                console.print(f"Available presets: {', '.join(available_presets)}")
                return USAGE_ERROR
        elif output_level:
            console.print(
                "[red]Error: --output-level is deprecated. Use --components instead.[/red]"
            )
            console.print("Examples:")
            console.print("  --components summary")
            console.print("  --components project_summary,ai_modules:limit=10")
            console.print("Use 'context list-components' to see available components.")
            return USAGE_ERROR
        else:
            # Default to summary preset
            component_specs = component_parser.parse_components_argument("summary")

        display_path = normalize_path_for_storage(str(directory))
        console.print(
            f"# Analyzing [cyan]{analysis_mode}[/cyan] project context: [bright_yellow]{display_path}[/bright_yellow]"
        )
        # Format components display with brighter colors
        components_display = []
        for name, params in component_specs:
            if params:
                param_str = ";".join(
                    f"[bright_yellow]{k}[/bright_yellow]=[bright_green]{v}[/bright_green]"
                    for k, v in params.items()
                )
                components_display.append(f"[cyan]{name}[/cyan]:[white]{param_str}[/white]")
            else:
                components_display.append(f"[cyan]{name}[/cyan]")
        console.print(f"# Components: {', '.join(components_display)}")
        console.print("")

        # Initialize components
        cache_manager = get_global_cache_manager()

        # Always create progress formatter - it will auto-detect worker mode
        if show_progress is None:
            show_progress = output_format.lower() in ["console", "table"]

        # Get worker mode from environment (set by worker service)
        worker_mode = os.environ.get("CODEGUARD_WORKER_MODE", "")

        # Calculate total expected work including scanner's built-in stages
        SCANNER_BUILTIN_STAGES = (
            4  # file_counting, structure_analysis, static_analysis, dependency_analysis
        )
        total_expected_work = SCANNER_BUILTIN_STAGES + len(component_specs)

        formatter = setup_unified_progress(
            worker_mode=worker_mode,
            component_specs=component_specs,
            show_progress=show_progress,
            total_expected_work=total_expected_work,
        )
        progress_callback = formatter.create_progress_callback()

        # Create static analyzer (filesystem_access injected by decorator)
        from ...context.analyzers.static_analyzer import StaticAnalyzer

        static_analyzer = StaticAnalyzer(filesystem_access)

        scanner = CodeGuardContextScanner(
            project_root=str(directory),
            cache_manager=cache_manager,
            filesystem_access=filesystem_access,
            static_analyzer=static_analyzer,
            max_breadth_depth=max_depth,
            progress_callback=progress_callback,
            component_specs=component_specs,
        )

        # Convert analysis mode
        try:
            mode = getattr(AnalysisMode, analysis_mode.upper())
        except AttributeError:
            console.print(f"[red]Invalid analysis mode: {analysis_mode}[/red]")
            console.print(f"Valid modes: {[m.value for m in AnalysisMode]}")
            return CONFIG_VALIDATION_FAILED

        # Perform analysis
        if cache_only:
            result = await scanner.get_cached_project_context()
            if not result:
                console.print(
                    "[yellow]No cached context found. Run without --cache-only to perform analysis.[/yellow]"
                )
                return VALIDATION_FAILED
        else:
            result = await scanner.analyze_project(
                mode=mode,
                force_refresh=no_cache,
            )

        # Clean up progress display
        if progress_callback and formatter:
            await formatter.finish_progress()

        # Display results using component system

        try:
            await display_results_with_components(
                result, component_specs, output_format, output_file, console
            )
        except Exception as e:
            console.print(f"[red]Error displaying results: {e}[/red]")
            logger.exception("Display error")
            return GENERAL_ERROR
        return SUCCESS

    except Exception as e:
        console.print(f"[red]Context analysis failed: {e}[/red]")
        logger.exception("Context analysis error")
        return GENERAL_ERROR


@handle_cli_errors
@with_filesystem_access()
async def cmd_context_query(
    directory: Path,
    filesystem_access: IFileSystemAccess,
    components: str = "summary",
    output_format: str = "console",
    output_file: Optional[Path] = None,
) -> int:
    """
    Query cached project context without performing new analysis.

    Args:
        directory: Project directory to query
        components: Component specifications to display
        output_format: Output format (console, json, yaml, text)
        output_file: Optional file to save results
    """
    try:
        # Initialize components
        cache_manager = get_global_cache_manager()

        # Set up component parsing
        component_parser = ComponentArgumentParser()
        component_display = ComponentDisplay()

        try:
            component_specs = component_parser.parse_components_argument(components)
        except ComponentParameterError as e:
            console.print(f"[red]Error in --components argument: {e}[/red]")
            return USAGE_ERROR

        # Create static analyzer (filesystem_access injected by decorator)
        from ...context.analyzers.static_analyzer import StaticAnalyzer

        static_analyzer = StaticAnalyzer(filesystem_access)

        scanner = CodeGuardContextScanner(
            project_root=str(directory),
            cache_manager=cache_manager,
            filesystem_access=filesystem_access,
            static_analyzer=static_analyzer,
            component_specs=component_specs,
        )

        # Query cached context
        console.print(f"[blue]Querying cached context...[/blue]")

        # Get cached context (we'll get all data and filter with components)
        result = await scanner.get_cached_project_context()

        if result:
            # Use shared display function - eliminates code duplication
            await display_results_with_components(
                result, component_specs, output_format, output_file, console
            )
            console.print("[green]✓ Retrieved cached context[/green]")
        else:
            console.print("[yellow]No cached context found. Run 'analyze' first.[/yellow]")
            return 1

        return 0

    except Exception as e:
        console.print(f"[red]Context query failed: {e}[/red]")
        logger.exception("Context query error")
        return GENERAL_ERROR


@handle_cli_errors
@with_filesystem_access()
def cmd_context_stats(
    directory: Path,
    filesystem_access: IFileSystemAccess,
    output_format: str = "table",
) -> int:
    """
    Display statistics about cached project context.

    Args:
        directory: Project directory to get stats for
        output_format: Output format (table, json)
    """
    try:
        # Initialize components
        cache_manager = get_global_cache_manager()

        # Get cache statistics
        console.print(f"[blue]Retrieving context statistics...[/blue]")

        # Create static analyzer (filesystem_access injected by decorator)
        from ...context.analyzers.static_analyzer import StaticAnalyzer

        static_analyzer = StaticAnalyzer(filesystem_access)

        scanner = CodeGuardContextScanner(
            project_root=str(directory),
            cache_manager=cache_manager,
            filesystem_access=filesystem_access,
            static_analyzer=static_analyzer,
            component_specs=[],
        )

        stats = scanner.get_cache_stats()

        if stats:
            console.print("[green]✓ Context statistics retrieved[/green]")
            # Display stats in requested format
            if output_format == "json":
                console.print(json.dumps(stats, indent=2, default=str))
            else:
                # Table format
                table = Table(title="📊 Context Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                for key, value in stats.items():
                    table.add_row(str(key), str(value))

                console.print(table)
        else:
            console.print("[yellow]No cached context found[/yellow]")
            return 1

        return 0

    except Exception as e:
        console.print(f"[red]Context stats failed: {e}[/red]")
        logger.exception("Context stats error")
        return 1


@handle_cli_errors
@with_filesystem_access()
def cmd_context_invalidate(directory: Path, filesystem_access: IFileSystemAccess) -> int:
    """
    Invalidate cached project context.

    Args:
        directory: Project directory to invalidate cache for
    """
    try:
        # Initialize components
        cache_manager = get_global_cache_manager()

        # Create static analyzer (filesystem_access injected by decorator)
        from ...context.analyzers.static_analyzer import StaticAnalyzer

        static_analyzer = StaticAnalyzer(filesystem_access)

        scanner = CodeGuardContextScanner(
            project_root=str(directory),
            cache_manager=cache_manager,
            filesystem_access=filesystem_access,
            static_analyzer=static_analyzer,
            component_specs=[],
        )

        # Invalidate cache
        console.print(f"[blue]Invalidating project context cache...[/blue]")

        scanner.invalidate_cache()

        console.print("[green]✓ Context cache invalidated successfully[/green]")
        console.print("Run 'analyze' to rebuild context.")
        return 0

    except Exception as e:
        console.print(f"[red]Context invalidation failed: {e}[/red]")
        logger.exception("Context invalidation error")
        return 1


def cmd_list_components(verbose: bool = False) -> int:
    """
    List all available analysis components.

    Args:
        verbose: Show detailed component information

    Returns:
        Exit code
    """
    try:
        # Import here to ensure components are registered
        from ...context import components  # This auto-registers all context components

        component_display = ComponentDisplay()

        if verbose:
            # Show detailed information for each component
            component_parser = ComponentArgumentParser()
            available_components = component_parser.list_available_components()

            console.print("[bold blue]📋 Available Analysis Components[/bold blue]\n")

            for component_name in sorted(available_components):
                help_text = component_display.show_component_help(component_name)
                console.print(f"[cyan]{help_text}[/cyan]")
                console.print()  # Add spacing between components

        else:
            # Show simple list with descriptions
            components_info = component_display.list_components_with_descriptions()

            if not components_info:
                console.print("[yellow]No components available.[/yellow]")
                return SUCCESS

            table = Table(title="📋 Available Analysis Components")
            table.add_column("Component", style="cyan", width=25)
            table.add_column("Description", style="white", width=55)

            for component_name in sorted(components_info.keys()):
                description = components_info[component_name]
                table.add_row(component_name, description)

            console.print(table)
            console.print()
            console.print("[dim]Use --verbose for detailed component information[/dim]")
            console.print(
                "[dim]Use components with: --components component1,component2:key=value;key2=value2[/dim]"
            )

        return SUCCESS

    except Exception as e:
        console.print(f"[red]Error listing components: {e}[/red]")
        logger.exception("Error listing components")
        return GENERAL_ERROR


def cmd_list_presets() -> int:
    """
    List all available component presets.

    Returns:
        Exit code
    """
    try:
        # Import here to ensure components are registered
        from ...context import components  # This auto-registers all context components

        component_display = ComponentDisplay()

        # Show presets help
        presets_help = component_display.show_presets_help()
        console.print(f"[cyan]{presets_help}[/cyan]")
        console.print()

        # Also show detailed preset expansions
        component_parser = ComponentArgumentParser()
        available_presets = component_parser.list_available_presets()

        if available_presets:
            console.print("[bold blue]📋 Preset Details[/bold blue]\n")

            for preset_name in sorted(available_presets):
                try:
                    # Parse the preset to show what components it expands to
                    component_specs = component_parser.parse_components_argument(preset_name)
                    components_list = [
                        (
                            f"{name}:{';'.join(f'{k}={v}' for k, v in params.items())}"
                            if params
                            else name
                        )
                        for name, params in component_specs
                    ]

                    console.print(f"[cyan]{preset_name}[/cyan]:")
                    for component in components_list:
                        console.print(f"  • {component}")
                    console.print()

                except Exception as e:
                    console.print(f"[red]Error expanding preset '{preset_name}': {e}[/red]")

        return SUCCESS

    except Exception as e:
        console.print(f"[red]Error listing presets: {e}[/red]")
        logger.exception("Error listing presets")
        return GENERAL_ERROR
