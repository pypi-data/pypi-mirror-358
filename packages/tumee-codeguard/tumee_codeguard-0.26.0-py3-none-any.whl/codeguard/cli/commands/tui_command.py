#!/usr/bin/env python3
"""
TUI Command Implementation - Standalone Interactive Interface
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    ProgressBar,
    RichLog,
    Static,
    Tree,
)

from ...context.analyzers.static_analyzer import StaticAnalyzer
from ...context.models import AnalysisMode, OutputLevel
from ...context.scanner import CodeGuardContextScanner
from ...core.caching.centralized import CentralizedCacheManager
from ...core.caching.manager import get_cache_manager as get_global_cache_manager
from ...core.exit_codes import SUCCESS, UNEXPECTED_ERROR
from ...core.filesystem.access import FileSystemAccess
from ...core.security.roots import RootsSecurityManager
from ...utils.logging_config import get_logger

logger = get_logger(__name__)


class CodeGuardTUI(App):
    """Interactive TUI for CodeGuard operations."""

    CSS = """
    .left-panel {
        width: 40%;
        border-right: solid $accent;
    }
    
    .right-panel {
        width: 60%;
    }
    
    .panel-title {
        background: $accent;
        color: $text;
        text-align: center;
        padding: 1;
    }
    
    .menu-container {
        height: 1fr;
    }
    
    .status-bar {
        background: $accent;
        color: $text;
        text-align: center;
        height: 1;
    }
    
    Tree {
        height: 1fr;
        scrollbar-size-vertical: 1;
    }
    
    DataTable {
        height: 50%;
    }
    
    RichLog {
        height: 50%;
        scrollbar-size-vertical: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c,q", "quit", "Quit"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("a", "analyze", "Analyze"),
        Binding("h", "help", "Help"),
    ]

    current_directory = reactive(Path.cwd())
    analysis_data = reactive(None)

    def __init__(self):
        super().__init__()
        self.title = "CodeGuard Interactive Terminal"
        self.sub_title = f"Directory: {self.current_directory}"

    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        yield Header()

        with Container():
            with Horizontal():
                # Left panel - Navigation and Controls
                with Vertical(classes="left-panel"):
                    yield Static("📁 Directory Navigation", classes="panel-title")
                    yield Tree("📁 Safe Directory Tree", id="dir-tree")

                    yield Static("🎯 Actions", classes="panel-title")
                    with Container(classes="menu-container"):
                        yield Button(
                            "🔍 Analyze & Show Summary", id="btn-analyze", variant="primary"
                        )
                        yield Button(
                            "📊 Analyze & Show Detailed Data",
                            id="btn-analyze-json",
                            variant="success",
                        )
                        yield Button(
                            "🔄 Refresh Directory Tree", id="btn-refresh", variant="default"
                        )
                        yield Button("⚙️ Settings", id="btn-settings", variant="default")
                        yield ProgressBar(id="progress-bar", show_eta=True)

                # Right panel - Results and Details
                with Vertical(classes="right-panel"):
                    yield Static("📋 Analysis Results", classes="panel-title")
                    yield DataTable(id="results-table")
                    yield Static("📝 Details", classes="panel-title")
                    yield RichLog(id="details-log", markup=True)

            yield Static(
                "Ready - Select a directory and choose an action", classes="status-bar", id="status"
            )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the TUI when mounted."""
        self.setup_results_table()
        self.log_welcome_message()
        self.hide_progress_bar()
        # Update directory tree in background
        self.run_worker(self.update_directory_tree)

    async def update_directory_tree(self) -> None:
        """Update the directory tree widget using safe_glob."""
        try:
            tree = self.query_one("#dir-tree", Tree)
            tree.clear()

            # Initialize filesystem access with proper security
            resolved_dir = self.current_directory.resolve()
            security_manager = RootsSecurityManager([str(resolved_dir)])
            filesystem_access = FileSystemAccess(security_manager)

            # Use safe_glob to enumerate directories safely
            all_paths = await filesystem_access.safe_glob(
                directory_path=resolved_dir,
                pattern="**/*",
                recursive=True,
                max_depth=3,  # Limit depth for UI performance
                respect_gitignore=True,
            )

            # Build tree structure using only safe directories
            directories = sorted({p.parent for p in all_paths if p.is_file()})
            directories.insert(0, resolved_dir)  # Add root directory

            # Create tree nodes for safe directories only
            root_node = tree.root.add(f"📁 {resolved_dir.name}", data=str(resolved_dir))
            dir_nodes = {str(resolved_dir): root_node}

            for directory in directories[1:]:  # Skip root which we already added
                rel_path = directory.relative_to(resolved_dir)
                parent_path = str(directory.parent)

                if parent_path in dir_nodes:
                    node = dir_nodes[parent_path].add(f"📁 {directory.name}", data=str(directory))
                    dir_nodes[str(directory)] = node

        except Exception as e:
            self.update_status(f"Safe directory tree update failed: {e}")

    def setup_results_table(self) -> None:
        """Setup the results table columns."""
        table = self.query_one("#results-table", DataTable)
        table.add_column("Module", width=20)
        table.add_column("Files", width=10)
        table.add_column("Importance", width=15)
        table.add_column("Language", width=15)

    def log_welcome_message(self) -> None:
        """Log welcome message to details panel."""
        log = self.query_one("#details-log", RichLog)
        log.write("[bold blue]Welcome to CodeGuard Interactive Terminal[/bold blue]")
        log.write("Navigate directories on the left and use actions to analyze your code.")
        log.write("Press 'a' to analyze the current directory, or use the buttons.")

    def on_tree_node_selected(self, event) -> None:
        """Handle directory selection from safe tree."""
        if event.node.data:
            self.current_directory = Path(event.node.data)
            self.sub_title = f"Directory: {self.current_directory}"
            self.update_status(f"Selected: {self.current_directory}")
            # Refresh tree for new directory
            self.run_worker(self.update_directory_tree)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-analyze":
            self.analyze_directory()
        elif button_id == "btn-analyze-json":
            self.analyze_directory_json()
        elif button_id == "btn-refresh":
            self.action_refresh()
        elif button_id == "btn-settings":
            self.show_settings()

    def update_status(self, message: str) -> None:
        """Update the status bar."""
        status = self.query_one("#status", Static)
        status.update(message)

    def show_progress_bar(self) -> None:
        """Show the progress bar."""
        progress = self.query_one("#progress-bar", ProgressBar)
        progress.display = True

    def hide_progress_bar(self) -> None:
        """Hide the progress bar."""
        progress = self.query_one("#progress-bar", ProgressBar)
        progress.display = False

    def update_progress(self, completed: int, total: int, message: str = "") -> None:
        """Update progress bar."""
        progress = self.query_one("#progress-bar", ProgressBar)
        progress.total = total
        progress.advance(completed - progress.progress)
        if message:
            self.update_status(message)

    def analyze_directory(self) -> None:
        """Analyze the current directory and show summary."""
        self.update_status(f"Analyzing {self.current_directory}...")
        self.show_progress_bar()
        log = self.query_one("#details-log", RichLog)
        log.clear()
        log.write(f"[bold]Starting analysis of: {self.current_directory}[/bold]")
        log.write("📊 This will show a summary view of the analysis results")

        # Run analysis in background (uses JSON internally)
        self.run_worker(self._run_analysis_summary, exclusive=True)

    def analyze_directory_json(self) -> None:
        """Analyze the current directory and show detailed data."""
        self.update_status(f"Analyzing {self.current_directory} (detailed mode)...")
        self.show_progress_bar()
        log = self.query_one("#details-log", RichLog)
        log.clear()
        log.write(f"[bold]Starting detailed analysis of: {self.current_directory}[/bold]")
        log.write("🔍 This will populate the table with detailed module information")

        # Run analysis in background with JSON format
        self.run_worker(self._run_analysis_detailed, exclusive=True)

    async def _run_analysis_summary(self) -> None:
        """Background worker for analysis with summary presentation."""
        try:
            log = self.query_one("#details-log", RichLog)
            log.write("🔄 Running context analysis...")

            # Get JSON data first (internal method)
            analysis_data = await self._get_analysis_data()

            if analysis_data:
                # Show summary information in log
                modules = analysis_data.get("modules", {})
                total_modules = len(modules)
                total_files = sum(mod.get("file_count", 0) for mod in modules.values())

                log.write(f"[green]✅ Analysis completed successfully[/green]")
                log.write(f"[bold]Summary:[/bold]")
                log.write(f"  📁 Modules found: {total_modules}")
                log.write(f"  📄 Total files: {total_files}")
                log.write(f"  📂 Directory: {self.current_directory}")

                # Show filesystem enumeration info
                fs_info = analysis_data.get("filesystem_info", {})
                if fs_info:
                    log.write(
                        f"[bold]Filesystem Enumeration (via {fs_info.get('filtering_method', 'unknown')}):[/bold]"
                    )
                    log.write(f"  📄 Files enumerated: {fs_info.get('files_enumerated', 0)}")
                    log.write(
                        f"  📁 Directories enumerated: {fs_info.get('directories_enumerated', 0)}"
                    )
                    log.write(f"  📊 Total paths found: {fs_info.get('total_paths_found', 0)}")
                    log.write(
                        f"  🚫 Respects .gitignore: {fs_info.get('respects_gitignore', False)}"
                    )
                    log.write(
                        f"  🤖 Respects .ai modules: {fs_info.get('respects_ai_modules', False)}"
                    )

                # Show top modules by importance
                if modules:
                    log.write(f"\n[bold]Top modules by importance:[/bold]")
                    sorted_modules = sorted(
                        modules.items(), key=lambda x: x[1].get("importance_score", 0), reverse=True
                    )[:5]

                    for name, data in sorted_modules:
                        importance = data.get("importance_score", 0)
                        files = data.get("file_count", 0)
                        lang = data.get("primary_language", "unknown")
                        log.write(
                            f"  • {name}: {importance:.2f} importance, {files} files ({lang})"
                        )

                self.analysis_data = analysis_data
                self.update_status("Summary analysis completed")
            else:
                log.write("[red]❌ Analysis failed - no data returned[/red]")
                self.update_status("Analysis failed")

        except Exception as e:
            log = self.query_one("#details-log", RichLog)
            log.write(f"[red]Error during analysis: {str(e)}[/red]")
            self.update_status("Analysis error")
        finally:
            self.hide_progress_bar()

    async def _run_analysis_detailed(self) -> None:
        """Background worker for analysis with detailed table presentation."""
        try:
            log = self.query_one("#details-log", RichLog)
            table = self.query_one("#results-table", DataTable)

            # Clear previous results
            table.clear()
            log.write("🔄 Running context analysis...")

            # Get JSON data first (internal method)
            analysis_data = await self._get_analysis_data()

            if analysis_data:
                self.analysis_data = analysis_data
                self.populate_results_table()

                modules = analysis_data.get("modules", {})
                log.write("[green]✅ Detailed analysis completed successfully[/green]")
                log.write(f"📊 Found {len(modules)} modules")
                log.write("💡 Click on a row in the table above to see detailed file information")
                self.update_status("Detailed analysis completed")
            else:
                log.write("[red]❌ Analysis failed - no data returned[/red]")
                self.update_status("Analysis failed")

        except Exception as e:
            log = self.query_one("#details-log", RichLog)
            log.write(f"[red]Error during detailed analysis: {str(e)}[/red]")
            self.update_status("Analysis error")
        finally:
            self.hide_progress_bar()

    async def _get_analysis_data(self) -> Optional[Dict]:
        """Internal method to get analysis data using proper filesystem enumeration."""
        try:
            # Log the analysis attempt
            logger.info(f"Starting analysis of: {self.current_directory}")

            # Initialize filesystem access with proper security
            resolved_dir = self.current_directory.resolve()
            security_manager = RootsSecurityManager([str(resolved_dir)])
            filesystem_access = FileSystemAccess(security_manager)

            # Use safe_glob to enumerate files properly
            # This automatically handles gitignore, AI modules, and system exclusions
            all_paths = await filesystem_access.safe_glob(
                directory_path=resolved_dir,
                pattern="**/*",  # All files and directories recursively
                recursive=True,
                max_depth=10,
                respect_gitignore=True,  # ✅ Respects .gitignore
            )

            # Separate files and directories
            files_found = [p for p in all_paths if p.is_file()]
            directories_found = [p for p in all_paths if p.is_dir()]

            logger.info(
                f"safe_glob found {len(files_found)} files and {len(directories_found)} directories (total: {len(all_paths)} paths)"
            )

            # Now analyze the properly enumerated files using the scanner
            cache_manager = get_global_cache_manager()
            static_analyzer = StaticAnalyzer(filesystem_access)
            scanner = CodeGuardContextScanner(
                project_root=str(resolved_dir),
                cache_manager=cache_manager,
                filesystem_access=filesystem_access,
                static_analyzer=static_analyzer,
                component_specs=[],
            )

            # Parse analysis parameters
            mode = AnalysisMode.FULL
            level = OutputLevel.STRUCTURE

            # Run the analysis with properly enumerated files
            result = await scanner.analyze_project(
                mode=mode, output_level=level, force_refresh=False, cache_only=False
            )

            # Convert AnalysisResults to dict if needed
            if hasattr(result, "to_dict"):
                data = result.to_dict()
            elif isinstance(result, dict):
                data = result
            else:
                # Log the type for debugging
                logger.warning(f"Unexpected result type: {type(result)}")
                # Try to extract useful data
                if hasattr(result, "__dict__"):
                    data: Dict[str, Any] = {
                        k: v for k, v in result.__dict__.items() if not k.startswith("_")
                    }
                else:
                    data: Dict[str, Any] = {"raw_result": str(result)}

            # Ensure data is a dict before proceeding
            if not isinstance(data, dict):
                logger.error(f"Could not convert result to dict: {type(result)}")
                return None

            # Add filesystem enumeration info to the data
            data["filesystem_info"] = {
                "files_enumerated": len(files_found),
                "directories_enumerated": len(directories_found),
                "total_paths_found": len(all_paths),
                "respects_gitignore": True,
                "respects_ai_modules": True,
                "filtering_method": "safe_glob",
            }

            logger.info(
                f"Successfully got analysis data with {len(data.get('modules', {}))} modules"
            )
            return data

        except Exception as e:
            logger.error(f"Exception in _get_analysis_data: {e}", exc_info=True)
            return None

    def populate_results_table(self) -> None:
        """Populate the results table with analysis data."""
        if not self.analysis_data:
            return

        table = self.query_one("#results-table", DataTable)
        table.clear()

        modules = self.analysis_data.get("modules", {})
        for module_name, module_data in modules.items():
            table.add_row(
                module_name,
                str(module_data.get("file_count", 0)),
                f"{module_data.get('importance_score', 0.0):.2f}",
                module_data.get("primary_language", "unknown"),
            )

    def on_data_table_row_selected(self, event) -> None:
        """Handle row selection in results table."""
        if not self.analysis_data:
            return

        table = self.query_one("#results-table", DataTable)
        log = self.query_one("#details-log", RichLog)

        if event.cursor_row < len(table.rows):
            row_data = table.get_row_at(event.cursor_row)
            module_name = row_data[0]

            # Show module details
            log.clear()
            self.show_module_details(module_name)

    def show_module_details(self, module_name: str) -> None:
        """Show detailed information about a selected module."""
        if not self.analysis_data:
            return

        log = self.query_one("#details-log", RichLog)
        modules = self.analysis_data.get("modules", {})

        if module_name in modules:
            module_data = modules[module_name]

            log.write(f"[bold blue]Module: {module_name}[/bold blue]")
            log.write(f"📁 Files: {module_data.get('file_count', 0)}")
            log.write(f"⭐ Importance: {module_data.get('importance_score', 0.0):.2f}")
            log.write(f"🔤 Language: {module_data.get('primary_language', 'unknown')}")

            # Show file details if available
            metadata = self.analysis_data.get("metadata", {})
            module_contexts = metadata.get("module_contexts", {})

            if module_name in module_contexts:
                module_context = module_contexts[module_name]
                if isinstance(module_context, dict) and "file_analyses" in module_context:
                    log.write("\n[bold]📄 Files in module:[/bold]")
                    file_analyses = module_context["file_analyses"]

                    for file_path, file_data in file_analyses.items():
                        if isinstance(file_data, dict):
                            lines = file_data.get("line_count", 0)
                            size = file_data.get("size_bytes", 0)
                            complexity = file_data.get("complexity_score", 0.0)
                            log.write(
                                f"  • {file_path} ({lines} lines, {size} bytes, {complexity:.1f} complexity)"
                            )

    def show_settings(self) -> None:
        """Show settings/configuration options."""
        log = self.query_one("#details-log", RichLog)
        log.clear()
        log.write("[bold blue]⚙️ Settings & Help[/bold blue]")
        log.write("Current directory: " + str(self.current_directory))
        log.write("\n[bold]Available actions:[/bold]")
        log.write(
            "  🔍 [bold]Analyze & Show Summary[/bold] - Shows overview with top modules and stats"
        )
        log.write("      (Both options use JSON internally for data accuracy)")
        log.write(
            "  📊 [bold]Analyze & Show Detailed Data[/bold] - Populates table with all modules"
        )
        log.write("      Click rows in the table to see detailed file information")
        log.write("  🔄 [bold]Refresh[/bold] - Refresh directory tree")
        log.write("\n[bold]Keyboard shortcuts:[/bold]")
        log.write("  • 'a' - Quick analyze (detailed mode)")
        log.write("  • 'h' - Show this help")
        log.write("  • 'q' or Ctrl+C - Quit")
        log.write("  • Ctrl+R - Refresh")
        log.write("\n[bold]How it works:[/bold]")
        log.write("The TUI uses FileSystemAccess.safe_glob() for ALL file operations:")
        log.write("  • Directory tree navigation uses safe_glob (NO .git exposure)")
        log.write("  • Respects .gitignore patterns automatically")
        log.write("  • Honors .ai module directory boundaries")
        log.write("  • Excludes system directories (.git, __pycache__, etc.)")
        log.write("  • Enforces security boundaries via RootsSecurityManager")
        log.write("  • Uses the same filtering logic as CLI commands")
        log.write("Both directory navigation AND analysis use this safe enumerated data.")

    async def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_refresh(self) -> None:
        """Refresh the directory tree."""
        self.run_worker(self.update_directory_tree)
        self.update_status("Directory tree refreshed")

    def action_analyze(self) -> None:
        """Analyze current directory (keyboard shortcut)."""
        self.analyze_directory_json()

    def action_help(self) -> None:
        """Show help information."""
        self.show_settings()


async def run_tui() -> int:
    """Run the CodeGuard TUI application."""
    try:
        app = CodeGuardTUI()
        await app.run_async()
        return SUCCESS
    except Exception as e:
        logger.error(f"TUI error: {e}")
        return UNEXPECTED_ERROR


def main() -> int:
    """Main entry point for the TUI command."""
    return asyncio.run(run_tui())
