"""
Console formatter for CodeGuard reports.
"""

import asyncio
import math
import os
from enum import Enum
from typing import Any, AsyncGenerator, List, Optional, Protocol, Union

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ...core.console_shared import clear_console_line, spinner_print
from ...core.runtime import get_default_console
from ..filesystem.path_utils import smart_truncate_path
from ..output import OutputManager
from ..progress.component_tracker import ComponentProgressTracker
from ..runtime import is_worker_process
from .base import DataType, FormatterRegistry, UniversalFormatter


class StreamingProgressSender(Protocol):
    """Protocol for sending streaming progress updates."""

    async def send_progress(
        self,
        command_id: str,
        progress: int,
        total: Optional[int] = None,
        message: str = "",
        stage: Optional[str] = None,
        component_id: Optional[str] = None,
        component_event: Optional[str] = None,
        cumulative_current: Optional[float] = None,
        cumulative_total: Optional[float] = None,
    ) -> None:
        """Send progress update message."""
        ...


class ConsoleStyle(Enum):
    """
    Console output styling options for the CONSOLE format.

    Values:
        PLAIN: No special formatting, plain text
        MINIMAL: Basic formatting with minimal decorations
        DETAILED: Full details with code snippets and diffs
        COMPACT: Condensed output for many violations
    """

    PLAIN = "plain"
    MINIMAL = "minimal"
    DETAILED = "detailed"
    COMPACT = "compact"


@FormatterRegistry.register
class ConsoleFormatter(UniversalFormatter):
    """Formatter for rich console output supporting all data types."""

    def __init__(
        self,
        console_style: ConsoleStyle = ConsoleStyle.DETAILED,
        display_callback=None,
        streaming_sender: Optional[StreamingProgressSender] = None,
        command_id: Optional[str] = None,
        show_progress: bool = True,
    ):
        super().__init__()
        self.console_style = console_style
        self._console = None
        self.display_callback = display_callback
        self._progress_live = None
        self._progress_task = None
        self._streaming_sender = streaming_sender
        self._command_id = command_id
        self._show_progress = show_progress
        # Initialize component tracker for client-side progress aggregation
        self._component_tracker = ComponentProgressTracker()
        # Initialize expected total for component count display
        self._expected_total = 0

    @property
    def format_name(self) -> str:
        return "console"

    @property
    def console(self):
        """Get the OutputManager (acting as console), initializing if needed."""
        if self._console is None:
            self._console = OutputManager(get_default_console())
        return self._console

    def supports_progress(self) -> bool:
        """Console formatter supports progress display."""
        return True

    async def _send_streaming_progress_if_worker(
        self, progress_data: dict, cumulative_current: float, cumulative_total: float
    ) -> None:
        """Send streaming progress update if streaming sender is available."""
        if not self._streaming_sender or not self._command_id:
            return

        await self._streaming_sender.send_progress(
            command_id=self._command_id,
            progress=progress_data.get("current", 0),
            total=progress_data.get("total"),
            message=progress_data.get("message", ""),
            stage=progress_data.get("phase"),
            component_id=progress_data.get("component_id"),
            component_event=progress_data.get("component_event"),
            cumulative_current=cumulative_current,
            cumulative_total=cumulative_total,
        )

    async def show_progress(self, **progress_data) -> None:
        # Handle component lifecycle events from scanner
        component_event = progress_data.get("component_event")
        if component_event:
            component_id = progress_data.get("component_id")
            if component_id is None:
                raise ValueError(
                    f"component_id is required for component_event '{component_event}'"
                )

            if component_event == "start":
                total = progress_data.get("total", 0)
                phase = progress_data.get("phase") or component_id

                # Don't update expected_total from scanner - it's set at initialization
                self._component_tracker.component_start(component_id, total, phase)
            elif component_event == "update":
                current = progress_data.get("current", 0)
                self._component_tracker.component_update(component_id, current)
            elif component_event == "stop":
                self._component_tracker.component_stop(component_id)
            # Continue to display progress after updating tracker state

        phase = progress_data.get("phase", "Processing")
        current = progress_data.get("current")
        total = progress_data.get("total")
        message = progress_data.get("message", phase)

        # Get cumulative progress from component tracker
        if self._component_tracker:
            cumulative_current_raw, cumulative_total_raw = (
                self._component_tracker.get_cumulative_progress()
            )
        else:
            cumulative_current_raw, cumulative_total_raw = 0, 0

        # Convert to phase-based display (each 100 units = 1 phase)
        cumulative_current = cumulative_current_raw / 100
        # Use expected total if available, otherwise fall back to tracker total
        expected_total = self._expected_total
        cumulative_total = (
            expected_total
            if expected_total and expected_total > 0
            else (cumulative_total_raw / 100)
        )

        if is_worker_process():
            # Send streaming progress update if running on worker process
            await self._send_streaming_progress_if_worker(
                progress_data, cumulative_current, cumulative_total
            )
        else:
            """Display progress using component tracker and Rich progress bars or spinners."""
            if not self.console or not self._show_progress:
                return

            # Get progress style from environment or default to "bar"
            progress_style = os.getenv("CODEGUARD_PROGRESS_STYLE", "bar").lower()
            if progress_style == "none":
                return

            # Build display message with cumulative progress
            if cumulative_total > 0:
                # Backstop: ensure total is never less than current
                # If current > total, set total to ceil(current)
                if cumulative_current > cumulative_total:
                    cumulative_total = math.ceil(cumulative_current)

                # Show cumulative progress: (2.5/4) Phase: message
                cumulative_prefix = f"({cumulative_current:.1f}/{cumulative_total:.0f})"
                if message and message != phase:
                    spinner_print("🔄", f"{cumulative_prefix} {message}")
                elif current is not None and total is not None:
                    spinner_print("🔄", f"{cumulative_prefix} {phase}: {current}/{total}")
                else:
                    spinner_print("🔄", f"{cumulative_prefix} {phase}")
            else:
                # Fallback to original behavior when no cumulative data
                if message and message != phase:
                    spinner_print("🔄", message)
                elif current is not None and total is not None:
                    spinner_print("🔄", f"{phase}: Processing... ({current}/{total})")
                else:
                    spinner_print("🔄", message or phase)

    def _show_spinner_progress(self, message: str) -> None:
        """Show spinner-style progress."""
        if self._progress_live is None:
            spinner = Spinner("dots", text=message)
            self._progress_live = Live(spinner, refresh_per_second=10)
            self._progress_live.start()
        else:
            # Update existing spinner
            spinner = Spinner("dots", text=message)
            self._progress_live.update(spinner)

    def _show_dots_progress(self, message: str) -> None:
        """Show simple dots progress."""
        if self.console:
            self.console.print(".", end="", style="dim")

    def _show_bar_progress(
        self,
        phase: str,
        current: Optional[int],
        total: Optional[int],
        message: str,
        percentage: Optional[float],
    ) -> None:
        """Show progress bar."""
        if self._progress_live is None and total is not None:
            # Create new progress bar
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                refresh_per_second=4,
            )
            self._progress_task = progress.add_task(message, total=total)
            self._progress_live = Live(progress, refresh_per_second=4)
            self._progress_live.start()
        elif self._progress_live is not None and current is not None:
            # Update existing progress bar
            progress = self._progress_live.renderable
            if isinstance(progress, Progress) and self._progress_task is not None:
                progress.update(self._progress_task, completed=current, description=message)

    def create_progress_callback_deferr_to_base_class(self):
        """Create a progress callback function for the context scanner."""

        async def progress_callback(**kwargs):
            await self.show_progress(**kwargs)
            await asyncio.sleep(0)  # Yield control to event loop

        return progress_callback

    async def finish_progress(self) -> None:
        """Finish and cleanup progress display."""
        clear_console_line()  # Clear any active spinner from console_shared
        if self._progress_live is not None:
            self._progress_live.stop()
            self._progress_live = None
            self._progress_task = None

    async def format_stream(
        self, items: AsyncGenerator[Any, None], data_type: DataType, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Format items as streaming console output using universal self-describing format."""
        async for item in items:
            yield await self._format_self_describing_item(item, **kwargs)

    async def format_collection(
        self, items: Union[Any, List[Any]], data_type: DataType, **kwargs
    ) -> str:
        """Format a complete collection or single item using universal self-describing format."""
        # Convert single item to list for uniform processing
        if not isinstance(items, list):
            items = [items]

        chunks = []
        for item in items:
            chunks.append(await self._format_self_describing_item(item, **kwargs))
        return "".join(chunks)

    async def format_validation_stream(
        self, items: AsyncGenerator[Any, None], **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Format items as streaming console output.

        Args:
            items: AsyncGenerator yielding ValidationResult or violation objects
            **kwargs: Additional formatting options

        Yields:
            Console output chunks for streaming
        """
        include_content = kwargs.get("include_content", True)
        include_diff = kwargs.get("include_diff", True)
        max_content_lines = kwargs.get("max_content_lines", 10)
        console_style = kwargs.get("console_style", None)

        # Handle console style override
        if console_style:
            try:
                style = ConsoleStyle(console_style.lower())
            except ValueError:
                style = self.console_style
        else:
            style = self.console_style

        if not self.console:
            # Fallback to text formatter
            from .text import TextFormatter

            text_formatter = TextFormatter()
            async for chunk in text_formatter.format_stream(items, **kwargs):
                yield chunk
            return

        violation_count = 0

        async for item in items:
            # Handle both ValidationResult and individual violations
            if hasattr(item, "violations"):
                # ValidationResult object - show summary first
                summary_table = Table(title="CodeGuard Validation Summary")
                summary_table.add_column("Metric")
                summary_table.add_column("Value")

                summary_table.add_row("Files Checked", str(item.files_checked))
                summary_table.add_row("Violations Found", str(item.violations_found))
                summary_table.add_row("Critical Violations", str(item.critical_count))
                summary_table.add_row("Warning Violations", str(item.warning_count))
                summary_table.add_row("Info Violations", str(item.info_count))

                status_color = "green" if item.status == "SUCCESS" else "red"
                status_text = Text(item.status, style=f"bold {status_color}")
                summary_table.add_row("Status", status_text)

                # Capture console output
                console_capture = self.console.capture()
                with console_capture:
                    self.console.print(summary_table)
                    self.console.print()
                    if item.violations_found > 0:
                        self.console.print("[bold]Violations:[/bold]")
                        self.console.print()

                yield console_capture.get()

                # Process individual violations
                for i, violation in enumerate(item.violations, 1):
                    violation_count = i
                    yield await self._format_violation(
                        violation,
                        violation_count,
                        style,
                        include_content,
                        include_diff,
                        max_content_lines,
                    )
            else:
                # Individual violation object
                violation_count += 1
                yield await self._format_violation(
                    item, violation_count, style, include_content, include_diff, max_content_lines
                )

    async def _format_violation(
        self, violation, index, style, include_content, include_diff, max_content_lines
    ):
        """Format a single violation for console output."""
        console_capture = self.console.capture()

        with console_capture:
            severity_color = {"critical": "red", "warning": "yellow", "info": "blue"}.get(
                violation.severity, "white"
            )

            if style == ConsoleStyle.COMPACT:
                # Compact style
                self.console.print(
                    f"[bold {severity_color}]#{index}[/bold {severity_color}] [{severity_color}]{violation.severity.upper()}[/{severity_color}] {violation.file}:{violation.line} - {violation.message}"
                )
            else:
                # Detailed style
                panel_title = f"Violation #{index} - {violation.severity.upper()}"

                content = []
                content.append(f"[bold]File:[/bold] {violation.file}:{violation.line}")
                content.append(f"[bold]Guard Type:[/bold] {violation.guard_type}")
                if hasattr(violation, "violated_by") and violation.violated_by:
                    content.append(f"[bold]Violated By:[/bold] {violation.violated_by}")
                content.append(f"[bold]Message:[/bold] {violation.message}")
                if hasattr(violation, "guard_source") and violation.guard_source:
                    content.append(f"[bold]Guard Source:[/bold] {violation.guard_source}")

                if include_diff and violation.diff_summary:
                    content.append("")
                    content.append("[bold]Diff:[/bold]")

                    diff_syntax = Syntax(
                        violation.diff_summary,
                        "diff",
                        theme="monokai",
                        line_numbers=False,
                        word_wrap=True,
                    )
                    content.append(diff_syntax)

                if include_content and style == ConsoleStyle.DETAILED:
                    content.append("")
                    content.append("[bold]Original Content:[/bold]")

                    # Determine language for syntax highlighting
                    language = "python"  # Default
                    if violation.file.endswith((".js", ".jsx")):
                        language = "javascript"
                    elif violation.file.endswith((".ts", ".tsx")):
                        language = "typescript"
                    elif violation.file.endswith(".java"):
                        language = "java"
                    elif violation.file.endswith(".cs"):
                        language = "csharp"
                    elif violation.file.endswith((".c", ".cpp", ".h", ".hpp")):
                        language = "cpp"

                    orig_lines = violation.original_content.splitlines()[:max_content_lines]
                    orig_content = "\n".join(orig_lines)

                    original_syntax = Syntax(
                        orig_content,
                        language,
                        theme="monokai",
                        line_numbers=True,
                        start_line=violation.line,
                        word_wrap=True,
                    )
                    content.append(original_syntax)

                    if len(violation.original_content.splitlines()) > max_content_lines:
                        content.append(
                            f"... ({len(violation.original_content.splitlines()) - max_content_lines} more lines)"
                        )

                    content.append("")
                    content.append("[bold]Modified Content:[/bold]")

                    mod_lines = violation.modified_content.splitlines()[:max_content_lines]
                    mod_content = "\n".join(mod_lines)

                    modified_syntax = Syntax(
                        mod_content,
                        language,
                        theme="monokai",
                        line_numbers=True,
                        start_line=violation.line,
                        word_wrap=True,
                    )
                    content.append(modified_syntax)

                    if len(violation.modified_content.splitlines()) > max_content_lines:
                        content.append(
                            f"... ({len(violation.modified_content.splitlines()) - max_content_lines} more lines)"
                        )

                panel = Panel(
                    "\n".join(str(item) for item in content),
                    title=panel_title,
                    border_style=severity_color,
                )
                self.console.print(panel)

        return console_capture.get()

    async def format_validation_collection(self, items: List[Any], **kwargs) -> str:
        """Format a complete collection of validation results."""
        chunks = []
        async for chunk in self.format_validation_stream(
            self._items_to_async_generator(items), **kwargs
        ):
            chunks.append(chunk)
        return "".join(chunks)

    async def _format_self_describing_item(self, item: Any, **kwargs) -> str:
        """Format a single self-describing item using universal format."""
        if not isinstance(item, dict):
            raise ValueError(f"Console formatter expects dict objects, got {type(item)}")

        # Check if this is streaming format: {component: "name", data: {...}, display: {...}}
        if "component" in item and "data" in item and "display" in item:
            # Streaming format - single component
            component_name = item["component"]
            component_data = {"data": item["data"], "display": item["display"]}
            self._render_self_describing_component(component_name, component_data)
            return ""  # Return empty since we rendered directly to console
        else:
            raise ValueError(f"Invalid component format: {list(item.keys())}")

    def _display_simple_analysis_tables(
        self, result: dict, sort_by: str, verbose: bool, output_level: str
    ):
        """Display analysis results for all components."""
        # Process each component in the result
        for component_name, component_data in result.items():
            # ALL components must have self-describing display instructions
            if isinstance(component_data, dict) and "display" in component_data:
                self._render_self_describing_component(component_name, component_data)
            else:
                raise ValueError(
                    f"Component '{component_name}' must provide 'data' and 'display' structure"
                )

    def _render_self_describing_component(self, component_name: str, component_data: dict):
        """Render a component using its self-describing display instructions."""
        display_spec = component_data.get("display", {})
        raw_data = component_data.get("data", {})

        display_type = display_spec.get("type", "")

        if display_type == "table":
            self._render_table_from_spec(raw_data, display_spec)
        elif display_type == "text":
            self._render_text_from_spec(raw_data, display_spec)
        else:
            raise ValueError(
                f"Unknown display type '{display_type}' for component '{component_name}'"
            )

    def _render_table_from_spec(self, raw_data: dict, display_spec: dict):
        """Render a table using display specification."""
        # Extract table configuration
        title = display_spec.get("title", "")
        columns = display_spec.get("columns", [])
        row_mapping = display_spec.get("row_mapping", {})
        transforms = display_spec.get("transforms", {})

        # Create Rich table
        table = Table(title=title)

        # Calculate table overhead and adjust widths (borrowed from display.py)
        num_columns = len(columns)
        if num_columns > 1:
            table_overhead = 2 + (num_columns - 1) + (num_columns * 2) + 1

            # Find first column > 40 chars and subtract all overhead from it
            for i, col in enumerate(columns):
                if isinstance(col, dict) and col.get("width", 0) > 40:
                    col["_adjusted_width"] = max(1, col["width"] - table_overhead)
                    break

        # Add columns with adjusted widths
        for col in columns:
            if isinstance(col, dict):
                width = col.get("_adjusted_width") or col.get("width")
                table.add_column(col.get("name", ""), style=col.get("style", ""), width=width)
            else:
                table.add_column(str(col))

        # Add rows based on mapping
        if "rows" in display_spec:
            # Static rows with template substitution
            for row_template in display_spec["rows"]:
                row = []
                for cell_template in row_template:
                    # Simple template substitution
                    cell_value = self._substitute_template(cell_template, raw_data)
                    row.append(str(cell_value))
                table.add_row(*row)
        elif row_mapping:
            # Dynamic rows from any array data - find the first array in raw_data
            data_array = None
            for key, value in raw_data.items():
                if isinstance(value, list) and value:
                    data_array = value
                    break

            if data_array:
                for item in data_array:
                    row = []
                    for col_idx, col in enumerate(columns):
                        col_name = col.get("name", "") if isinstance(col, dict) else str(col)
                        col_width = (
                            col.get("_adjusted_width") or col.get("width")
                            if isinstance(col, dict)
                            else None
                        )
                        # Find mapping for this column
                        mapped_value = ""
                        for field, mapping in row_mapping.items():
                            if (isinstance(mapping, str) and mapping == col_name) or (
                                isinstance(mapping, dict) and mapping.get("column") == col_name
                            ):
                                # Get value and apply transform if needed
                                value = item.get(field, "")
                                if isinstance(mapping, dict) and "transform" in mapping:
                                    transform_name = mapping["transform"]
                                    if transform_name in transforms:
                                        value = self._apply_transform(
                                            value, transforms[transform_name], item, col_width
                                        )
                                mapped_value = str(value)
                                break
                        row.append(mapped_value)
                    table.add_row(*row)

        self.console.print(table)
        self.console.print()

    def _substitute_template(self, template: str, data: dict) -> str:
        """Simple template substitution for static rows."""
        if not isinstance(template, str):
            return template

        # Handle simple field substitutions like {total_files}
        import re

        def replacer(match):
            field_path = match.group(1)
            # Handle nested fields like category_counts.critical
            parts = field_path.split(".")
            value = data
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, 0)
                else:
                    value = 0
                    break

            # Handle formatting like {average_score:.1f}
            if ":" in field_path:
                field_name, format_spec = field_path.split(":", 1)
                parts = field_name.split(".")
                value = data
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part, 0)
                    else:
                        value = 0
                        break
                try:
                    return f"{value:{format_spec}}"
                except:
                    return str(value)

            return str(value)

        return re.sub(r"\{([^}]+)\}", replacer, template)

    def _apply_transform(
        self, value, transform_spec: dict, item: dict, column_width: Optional[int] = None
    ) -> str:
        """Apply transformation to a value based on transform specification."""
        transform_type = transform_spec.get("type", "")

        if transform_type == "mapping":
            mapping = transform_spec.get("map", {})
            return mapping.get(value, str(value))
        elif transform_type == "format":
            format_str = transform_spec.get("format", "{}")
            try:
                # Generic format string evaluation using the item data
                return format_str.format(**item)
            except:
                return str(value)
        elif transform_type == "truncate_path":
            # Use the actual column width from the table spec
            if column_width is None:
                raise ValueError("truncate_path transform requires column_width to be provided")
            # Use existing smart_truncate_path from path_utils
            return smart_truncate_path(str(value), column_width)
        elif transform_type == "conditional_format":
            conditions = transform_spec.get("conditions", [])
            for condition in conditions:
                if "if" in condition:
                    # Simple condition evaluation
                    condition_str = condition["if"]
                    # Evaluate the condition
                    condition_met = False
                    if "urgency_category == 'critical'" in condition_str:
                        condition_met = item.get("urgency_category") == "critical"

                    if condition_met:
                        format_str = condition["format"]
                        try:
                            # Handle special formatting like {total_score/1000:.0f}
                            if "{total_score/1000:" in format_str:
                                score_k = item.get("total_score", 0) / 1000
                                emoji = "🚨" if "🚨" in format_str else "⚠️"
                                return f"{emoji}{score_k:.0f}k"
                            else:
                                return format_str.format(**item)
                        except:
                            return str(value)
                elif "default" in condition:
                    format_str = condition["default"]
                    try:
                        # Handle special formatting like {total_score/1000:.0f}
                        if "{total_score/1000:" in format_str:
                            score_k = item.get("total_score", 0) / 1000
                            emoji = "🚨" if "🚨" in format_str else "⚠️"
                            return f"{emoji}{score_k:.0f}k"
                        else:
                            return format_str.format(**item)
                    except:
                        return str(value)

        return str(value)

    def _render_text_from_spec(self, raw_data: dict, display_spec: dict):
        """Render text using display specification."""
        # Simple text rendering - can be expanded later
        text = display_spec.get("text", "")
        self.console.print(text)

    def _display_dependency_metrics_table(self, dep_data: dict):
        """Display dependency metrics component."""
        if not dep_data:
            return

        table = Table(title="📊 Dependency Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        # Display various dependency metrics
        for key, value in dep_data.items():
            if isinstance(value, (int, float, str)):
                display_key = key.replace("_", " ").title()
                table.add_row(display_key, str(value))

        self.console.print(table)
        self.console.print()

    def _display_top_files_table(self, component_name: str, files_data: dict):
        """Display top files component (context, lines, complexity)."""
        if not files_data:
            return

        # Extract display info from component name
        if "context" in component_name:
            title = "📄 Top Files by Context"
            score_col = "Context Score"
        elif "lines" in component_name:
            title = "📏 Top Files by Lines"
            score_col = "Lines"
        elif "complexity" in component_name:
            title = "🧩 Top Files by Complexity"
            score_col = "Complexity"
        else:
            title = f"📋 {component_name.replace('_', ' ').title()}"
            score_col = "Score"

        table = Table(title=title)
        table.add_column("File", style="cyan")
        table.add_column(score_col, style="yellow")

        # Handle component JSON structure
        if isinstance(files_data, dict) and "files" in files_data:
            files_list = files_data["files"]
            if isinstance(files_list, list):
                for file_data in files_list:
                    if isinstance(file_data, dict):
                        file_path = file_data.get("file_path", "Unknown")
                        score = file_data.get(
                            "score", file_data.get("lines", file_data.get("complexity", 0))
                        )
                        table.add_row(file_path, str(score))
        else:
            self.console.print(
                f"[yellow]Warning: Unexpected {component_name} data structure[/yellow]"
            )
            return

        self.console.print(table)
        self.console.print()

    def _display_generic_component_table(self, component_name: str, component_data):
        """Display any component as a generic table."""
        if not component_data:
            return

        # Clean up component name for display
        display_name = component_name.replace("_", " ").title()

        if isinstance(component_data, dict):
            table = Table(title=f"📋 {display_name}")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")

            for key, value in component_data.items():
                if isinstance(value, (list, dict)):
                    table.add_row(
                        str(key),
                        (
                            f"{type(value).__name__} ({len(value)} items)"
                            if hasattr(value, "__len__")
                            else str(type(value).__name__)
                        ),
                    )
                else:
                    table.add_row(str(key), str(value))

            self.console.print(table)
        elif isinstance(component_data, list):
            table = Table(title=f"📋 {display_name}")
            table.add_column("Index", style="cyan")
            table.add_column("Value", style="green")

            for i, item in enumerate(component_data[:10]):  # Limit to first 10 items
                table.add_row(str(i), str(item))

            if len(component_data) > 10:
                table.add_row("...", f"({len(component_data) - 10} more items)")

            self.console.print(table)
        else:
            # Simple value
            self.console.print(f"📋 {display_name}: {component_data}")

        self.console.print()

    async def _items_to_async_generator(self, items: List[Any]):
        """Convert list to async generator."""
        for item in items:
            yield item
