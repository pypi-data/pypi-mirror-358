"""
System chat plugin implementation for the hook system.

This plugin handles sys: prefixed messages by mirroring CLI sys commands,
providing system status and management functionality through chat interface.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

from ...servers.llm_proxy.payload_context import PayloadContext
from ...servers.llm_proxy.processors.hook_types import (
    HookResult,
    create_block_result,
    create_continue_result,
)
from ...shared.chat import command
from ..shared.cli_bridge import CLIBridge


class SysPlugin:
    """
    Plugin that implements sys chat functionality by mirroring CLI commands.

    This plugin handles messages starting with "sys:" by processing them
    locally and returning responses without involving the LLM, mirroring
    the behavior of CLI sys commands.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Plugin statistics
        self.stats = {
            "commands_processed": 0,
            "commands_blocked": 0,
            "commands_continued": 0,
            "errors": 0,
        }

    async def sys_hook_callback(self, message: str, payload: PayloadContext) -> HookResult:
        """
        Handle sys: prefixed messages.

        Args:
            message: Full message text starting with "sys:"
            payload: PayloadContext for the request

        Returns:
            HookResult indicating whether to block or continue the request
        """
        try:
            self.stats["commands_processed"] += 1

            self.logger.info(f"Processing sys command: {message[:50]}...")

            # Process the sys command directly
            response_data, should_block = await self._process_sys_command(message, payload)

            if should_block:
                self.stats["commands_blocked"] += 1

                # Ensure response_data is not None
                if response_data is None:
                    response_data = self._create_error_response("No response generated")

                # Return a BLOCK result with the local response
                return create_block_result(
                    response_data=response_data, message=f"Processed sys command locally"
                )
            else:
                self.stats["commands_continued"] += 1

                # Some sys commands might want to continue to LLM
                return create_continue_result(message="Sys command processed, continuing to LLM")

        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Error processing sys command: {e}", exc_info=True)

            # On error, create a local error response and block
            error_response = self._create_error_response(str(e))
            return create_block_result(
                response_data=error_response, message=f"Error processing sys command: {e}"
            )

    async def _process_sys_command(
        self, message: str, payload: PayloadContext
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Process a sys command message by mirroring CLI behavior.

        Args:
            message: Full message text starting with 'sys:'
            payload: PayloadContext for the request

        Returns:
            Tuple of (response_dict, should_block)
        """
        try:
            # Parse command from message
            if not message.lower().startswith("sys:"):
                return None, False

            command_text = message[4:].strip()  # Remove "sys:" prefix

            if not command_text:
                return self._create_help_response(), True

            # Parse command and arguments
            parts = command_text.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            # Handle built-in commands
            if command == "help":
                return await self._handle_help(args, payload), True
            elif command == "status":
                return await self._handle_status(args, payload), True
            else:
                # Unknown command
                return self._create_unknown_command_response(command), True

        except Exception as e:
            self.logger.error(f"Error processing sys command: {e}", exc_info=True)
            return self._create_error_response(f"Command processing error: {e}"), True

    async def _handle_help(self, args: List[str], _payload: PayloadContext) -> Dict[str, Any]:
        """Handle help command using CLI bridge."""
        try:
            if args:
                # Help for specific command
                specific_command = args[0].lower()
                help_text = CLIBridge.generate_command_help("sys", specific_command)
            else:
                # General help
                help_text = CLIBridge.generate_command_help("sys")

            return self._create_text_response(help_text)

        except Exception as e:
            self.logger.error(f"Error generating help: {e}")
            return self._create_text_response(f"Error generating help: {e}")

    async def _handle_status(self, args: List[str], payload: PayloadContext) -> Dict[str, Any]:
        """Handle status command by mirroring CLI sys status functionality."""
        try:
            # Import the CLI status collection function
            from ...cli.commands.sys import _collect_system_status

            # Parse arguments (basic argument parsing for chat interface)
            include_health_check = "--no-health-check" not in args
            include_system_info = "--no-system-info" not in args
            verbose = "--verbose" in args or "-v" in args

            # Collect status data using the same function as CLI
            status_data = await _collect_system_status(
                include_health_check=include_health_check,
                include_system_info=include_system_info,
                verbose=verbose,
            )

            # Format for chat response
            status_text = self._format_status_for_chat(status_data, verbose=verbose)

            return self._create_text_response(status_text)

        except Exception as e:
            self.logger.error(f"Error getting system status: {e}", exc_info=True)
            return self._create_error_response(f"Error getting system status: {e}")

    def _format_status_for_chat(self, status_data: Dict[str, Any], verbose: bool = False) -> str:
        """
        Format status data for chat response.

        Args:
            status_data: Status data from CLI function
            verbose: Whether to include verbose information

        Returns:
            Formatted status text
        """
        try:
            lines = ["System Status Report", "=" * 20, ""]

            # Proxy status
            proxy = status_data.get("proxy", {})
            proxy_status = proxy.get("status", "unknown")
            lines.append(f"Proxy Server: {proxy_status}")

            if proxy.get("host") and proxy.get("port"):
                lines.append(f"  Location: {proxy['host']}:{proxy['port']}")
            elif proxy.get("message"):
                lines.append(f"  Details: {proxy['message']}")

            lines.append("")

            # Plugin status
            plugins = status_data.get("plugins", {})
            plugin_count = plugins.get("registered_count", 0)
            hooks = plugins.get("active_hooks", [])

            lines.append(f"Plugins: {plugin_count} registered")
            if hooks:
                lines.append(f"  Active hooks: {', '.join(hooks)}")

            lines.append("")

            # Session status
            sessions = status_data.get("sessions", {})
            active_sessions = sessions.get("active_count", 0)
            total_processed = sessions.get("total_processed", 0)

            lines.append(f"Sessions: {active_sessions} active")
            lines.append(f"  Total processed: {total_processed}")

            # Upstream status (if included)
            if "upstream" in status_data:
                lines.append("")
                lines.append("Upstream Services:")
                upstream = status_data["upstream"]
                for service, health in upstream.items():
                    status = health.get("status", "unknown")
                    lines.append(f"  {service}: {status}")

            # System information (if included and verbose)
            if verbose and "system" in status_data:
                system = status_data["system"]
                if "error" in system:
                    lines.append("")
                    lines.append(f"System Info: {system['error']}")
                elif "resources" in system:
                    lines.append("")
                    lines.append("System Resources:")
                    resources = system["resources"]
                    cpu = resources.get("cpu_percent", 0)
                    memory = resources.get("memory", {})
                    memory_pct = memory.get("percent_used", 0)
                    lines.append(f"  CPU: {cpu}%")
                    lines.append(f"  Memory: {memory_pct}%")

            # Timestamp
            timestamp = status_data.get("timestamp", "unknown")
            lines.extend(["", f"Generated: {timestamp}"])

            return "\n".join(lines)

        except Exception as e:
            self.logger.error(f"Error formatting status: {e}")
            return f"Error formatting status: {e}"

    def _create_text_response(self, text: str) -> Dict[str, Any]:
        """Create a text response in Anthropic format."""
        return {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": text}],
            "model": "local-sys-chat",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }

    def _create_help_response(self) -> Dict[str, Any]:
        """Create response for empty sys command."""
        help_text = CLIBridge.generate_command_help("sys")
        return self._create_text_response(help_text)

    def _create_unknown_command_response(self, command: str) -> Dict[str, Any]:
        """Create response for unknown command."""
        available_commands = ["status", "help"]
        return self._create_text_response(
            f"Unknown sys command: {command}\n\nAvailable commands: {', '.join(available_commands)}\n\nType 'sys:help' for more information."
        )

    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """
        Create an error response in the expected format.

        Args:
            error_msg: Error message to include

        Returns:
            Error response dictionary
        """
        return {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": f"Error processing sys command: {error_msg}"}],
            "model": "local-sys-chat",
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin statistics."""
        return {
            "plugin_name": "sys_chat",
            "stats": self.stats.copy(),
            "registered_commands": ["status", "help"],
            "command_count": 2,
        }

    def clear_statistics(self) -> None:
        """Clear plugin statistics."""
        self.stats = {
            "commands_processed": 0,
            "commands_blocked": 0,
            "commands_continued": 0,
            "errors": 0,
        }
        self.logger.info("Cleared sys chat plugin statistics")

    def get_registered_commands(self) -> list:
        """Get list of registered sys commands."""
        return ["status", "help"]

    def __str__(self) -> str:
        """String representation for debugging."""
        return f"SysPlugin(commands={len(self.get_registered_commands())})"


# Create plugin instance for method binding
_plugin_instance = SysPlugin()


@command("sys:")
async def sys_command_handler(message: str, payload: PayloadContext) -> HookResult:
    """Handle sys: prefixed messages via decorator."""
    return await _plugin_instance.sys_hook_callback(message, payload)
