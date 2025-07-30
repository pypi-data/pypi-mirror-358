"""
Component-based display logic for CLI output.
"""

import asyncio
import base64
import json
import logging
import time
from typing import Any, Dict, List, Tuple, Union

from rich.console import Console
from rich.table import Table

from ...context.models import AnalysisResults
from ...core.components import ComponentError, get_component_registry
from ...core.console_shared import clear_console_line, spinner_print
from ...core.runtime import get_default_console, is_worker_process
from ...core.streaming.protocol import ComponentComplete
from ...core.streaming.protocol import ComponentError as StreamingComponentError
from ...core.streaming.protocol import StreamJson
from ...core.streaming.stdout import StdoutMessageSender
from ...servers.p2p_server.p2p_manager.streaming_cache import StreamingServerCache

logger = logging.getLogger(__name__)


class ComponentDisplay:
    """Handles component-based output display."""

    def __init__(self):
        self.registry = get_component_registry()
        self.console = get_default_console()
        self._shared_message_sender = None

    async def _get_or_create_shared_sender(self, command_id: str):
        """Get or create the shared message sender for all components."""
        if self._shared_message_sender is None:
            if is_worker_process():
                if command_id:
                    # Worker with command_id: Try ZMQ cache first (registered streaming server)
                    cache = StreamingServerCache.get_instance()
                    sender = cache.get(command_id)
                    if sender:
                        self._shared_message_sender = sender
                        return self._shared_message_sender

                # Worker without cache hit: Use stdout to communicate with parent process
                sender = StdoutMessageSender()
                await sender.start()
                self._shared_message_sender = sender

            elif command_id:
                # Non-worker with command_id: Invalid state - should not happen
                raise ValueError(f"Non-worker process has command_id {command_id}")

            else:
                # Local execution: No sender needed, will use console display
                self._shared_message_sender = None

        return self._shared_message_sender

    async def generate_json_single_component(
        self,
        results: AnalysisResults,
        component_name: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate JSON output for a single component."""
        try:
            # Get the component
            component = self.registry.get_component(component_name)

            # Extract data
            data = await component.extract(results, **params)

            # All components must use self-describing format
            if not (isinstance(data, dict) and "data" in data and "display" in data):
                raise ValueError(
                    f"Component '{component_name}' must return self-describing format with 'data' and 'display' keys"
                )

            # Use the same format as streaming output
            return {"component": component_name, **data, "status": "completed"}

        except ComponentError as e:
            logger.error(f"Component error: {e}")
            return {"component": component_name, "error": str(e), "status": "error"}
        except Exception as e:
            logger.exception(f"Unexpected error in component {component_name}")
            return {
                "component": component_name,
                "error": f"Unexpected error: {e}",
                "status": "error",
            }

    async def generate_streaming_single_component(
        self,
        results: AnalysisResults,
        component_name: str,
        params: Dict[str, Any],
        command_id: Union[str, None] = None,
    ) -> None:
        """
        Generate streaming JSON output for a single component.
        Component calls send() to emit its JSON result.

        Args:
            results: Analysis results to display
            component_name: Name of the component
            params: Component parameters
            command_id: Command ID for streaming context
        """
        import json

        logger.info(
            f"🔧 GENERATE_STREAMING: Starting component {component_name} with command_id={command_id}"
        )

        class ProgressReporter:
            """Handles progress and status reporting for component execution."""

            def __init__(self, command_id: str, message_sender=None):
                self.command_id = command_id
                self.message_sender = message_sender
                self._initialized = message_sender is not None

            async def setup(self):
                """Setup the message sender. Must be called after initialization."""
                if not self._initialized:
                    await self._setup_sender()
                return self

            async def _setup_sender(self):
                """Set up message sender based on execution context."""
                if self._initialized:
                    return

                if is_worker_process():
                    if self.command_id:
                        # Worker with command_id: Try ZMQ cache first (registered streaming server)
                        cache = StreamingServerCache.get_instance()
                        sender = cache.get(self.command_id)
                        if sender:
                            self.message_sender = sender
                            self._initialized = True
                            return

                    # Worker without cache hit: Use stdout to communicate with parent process
                    sender = StdoutMessageSender()
                    await sender.start()
                    self.message_sender = sender

                elif self.command_id:
                    # Non-worker with command_id: Invalid state - should not happen
                    raise ValueError(f"Non-worker process has command_id {self.command_id}")

                else:
                    # Local execution: No sender needed, will use console display
                    self.message_sender = None

                self._initialized = True

            async def report_progress(self, comp_name: str, progress: int, message: str):
                """Report progress using the configured message sender."""
                if self.message_sender:
                    try:
                        await self.message_sender.send_progress(
                            command_id=self.command_id,
                            progress=progress,
                            total=100,
                            message=message,
                            stage=comp_name,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send progress via message sender: {e}")
                else:
                    # Local execution: Use console progress display
                    if message:
                        spinner_print("🔄", f"{comp_name}: {progress}% - {message}")
                        # Auto-clear spinner when progress reaches 100%
                        if progress >= 100:
                            clear_console_line()

            async def report_status(self, level: str, message: str, source: str = "component"):
                """Report status using the configured message sender."""
                if self.message_sender:
                    try:
                        await self.message_sender.send_status(
                            command_id=self.command_id, level=level, message=message, source=source
                        )
                    except Exception as e:
                        logger.error(f"Failed to send status via message sender: {e}")
                # No local fallback for status messages

            async def report_component_start(self, comp_name: str):
                """Report component start event using the configured message sender."""
                logger.info(
                    f"🔧 DISPLAY_COMPONENT_START: About to send start event for {comp_name}"
                )
                if self.message_sender:
                    try:
                        await self.message_sender.send_progress(
                            command_id=self.command_id,
                            progress=0,
                            total=100,
                            message=f"Starting {comp_name}",
                            stage=comp_name,
                            component_event="start",
                            component_id=comp_name,
                        )
                        logger.info(
                            f"🔧 DISPLAY_COMPONENT_START: Successfully sent start event for {comp_name}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to send component start via message sender: {e}")
                else:
                    # Local execution: Use console progress display
                    logger.info(
                        f"🔧 DISPLAY_COMPONENT_START: Local mode - showing spinner for {comp_name}"
                    )
                    spinner_print("🔄", f"Starting {comp_name}...")

        async def send(json_data: dict) -> None:
            """Send a complete JSON structure through the message sender queue"""
            if progress_reporter.message_sender:
                # Use StreamJson envelope for complete JSON data
                # Base64 encode to prevent JSON parsing conflicts with Rich markup tags
                json_str = json.dumps(json_data, separators=(",", ":"))
                encoded_data = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
                json_msg = StreamJson(
                    command_id=progress_reporter.command_id, data=encoded_data, encoding="base64"
                )
                await progress_reporter.message_sender.send_message(json_msg)
            else:
                # Fallback to direct print for local execution
                to_print = json.dumps(json_data, separators=(",", ":"))
                print(to_print, end="\n\n", flush=True)

        # Set up progress reporter once for this execution using shared sender
        shared_sender = await self._get_or_create_shared_sender(command_id or "default")
        progress_reporter = await ProgressReporter(command_id or "default", shared_sender).setup()

        async def progress_callback(comp_name: str, progress: int, message: str) -> None:
            """Report component progress using pre-configured reporter."""
            await progress_reporter.report_progress(comp_name, progress, message)

        async def status_callback(level: str, message: str) -> None:
            """Report component status using pre-configured reporter."""
            await progress_reporter.report_status(level, message)

        try:
            # Get the component
            component = self.registry.get_component(component_name)

            # Send component START event before execution
            await progress_reporter.report_component_start(component_name)

            # Set up streaming callbacks
            component.set_streaming_callbacks(progress_callback, status_callback)

            # Extract data
            start_time = time.time()
            data = await component.extract(results, **params)
            execution_time = time.time() - start_time

            # All components must use self-describing format
            if not (isinstance(data, dict) and "data" in data and "display" in data):
                raise ValueError(
                    f"Component '{component_name}' must return self-describing format with 'data' and 'display' keys"
                )

            # Send the complete self-describing structure
            component_data = {
                "component": component_name,
                "data": data["data"],
                "display": data["display"],
                "status": "completed",
            }
            await send(component_data)

            # Send ComponentComplete signal to clear spinner and signal completion
            if progress_reporter.message_sender:
                complete_msg = ComponentComplete(
                    command_id=progress_reporter.command_id,
                    component_name=component_name,
                    data=component_data,
                    execution_time=execution_time,
                )
                await progress_reporter.message_sender.send_message(complete_msg)

        except ComponentError as e:
            error_data = {"component": component_name, "error": str(e), "status": "error"}
            await send(error_data)
            # Send ComponentError signal to clear spinner
            if progress_reporter.message_sender:
                error_msg = StreamingComponentError(
                    command_id=progress_reporter.command_id,
                    component_name=component_name,
                    error=str(e),
                )
                await progress_reporter.message_sender.send_message(error_msg)
            logger.error(f"Component error: {e}")
        except Exception as e:
            error_data = {
                "component": component_name,
                "error": f"Unexpected error: {e}",
                "status": "error",
            }
            await send(error_data)
            # Send ComponentError signal to clear spinner
            if progress_reporter.message_sender:
                error_msg = StreamingComponentError(
                    command_id=progress_reporter.command_id,
                    component_name=component_name,
                    error=f"Unexpected error: {e}",
                )
                await progress_reporter.message_sender.send_message(error_msg)
            logger.exception(f"Unexpected error in component {component_name}")

    def list_components_with_descriptions(self) -> Dict[str, str]:
        """
        Get all components with their descriptions.

        Returns:
            Dictionary mapping component names to descriptions
        """
        components_info = {}

        for component_name in self.registry.list_components():
            try:
                component = self.registry.get_component(component_name)
                components_info[component_name] = component.description
            except Exception as e:
                components_info[component_name] = f"Error: {e}"

        return components_info

    def show_component_help(self, component_name: str) -> str:
        """
        Show help information for a specific component.

        Args:
            component_name: Name of the component

        Returns:
            Help text for the component
        """
        try:
            component = self.registry.get_component(component_name)

            help_lines = [
                f"Component: {component.name}",
                f"Description: {component.description}",
                "",
                "Default Parameters:",
            ]

            if component.default_params:
                for param, value in component.default_params.items():
                    help_lines.append(f"  {param}: {value}")
            else:
                help_lines.append("  None")

            return "\n".join(help_lines)

        except ComponentError as e:
            return f"Component '{component_name}' not found: {e}"
        except Exception as e:
            return f"Error getting help for '{component_name}': {e}"

    def show_presets_help(self) -> str:
        """
        Show help information for available presets.

        Returns:
            Help text for presets
        """
        try:
            presets = self.registry.list_presets()

            if not presets:
                return "No presets available."

            help_lines = ["Available Presets:", ""]

            for preset_name in sorted(presets):
                help_lines.append(f"  {preset_name}")

            help_lines.extend(
                [
                    "",
                    "Use presets with: --components preset_name",
                    "Combine with other components: --components preset_name,additional_component",
                ]
            )

            return "\n".join(help_lines)

        except Exception as e:
            return f"Error getting presets help: {e}"
