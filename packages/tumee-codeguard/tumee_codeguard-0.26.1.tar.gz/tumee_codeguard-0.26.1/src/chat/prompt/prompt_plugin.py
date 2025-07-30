"""
Prompt chat plugin implementation for the hook system.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from ...core.session_resolver import SessionKeyResolver
from ...servers.llm_proxy.payload_context import PayloadContext
from ...servers.llm_proxy.processors.hook_types import (
    HookResult,
    create_block_result,
    create_continue_result,
)
from ...servers.mcp_server.tools.modules.prompt_inject_core import PromptInjectManager
from ...servers.mcp_server.tools.prompt_inject import PromptInjectParser
from ...shared.chat import command


class PromptChatPlugin:
    """
    Plugin that implements prompt injection functionality within the hook system.

    This plugin handles messages starting with "prompt:" by processing them
    locally and returning responses without involving the LLM.
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

    async def prompt_hook_callback(self, message: str, payload: PayloadContext) -> HookResult:
        """
        Handle prompt: prefixed messages.

        Args:
            message: Full message text starting with "prompt:"
            payload: PayloadContext for the request

        Returns:
            HookResult indicating whether to block or continue the request
        """
        try:
            self.stats["commands_processed"] += 1

            self.logger.info(f"Processing prompt command: {message[:50]}...")

            # Extract session ID using SessionKeyResolver
            session_id = self._resolve_session_id(payload)

            # Process the prompt command directly
            response_data, should_block = await self._process_prompt_command(
                message, payload, session_id
            )

            if should_block:
                self.stats["commands_blocked"] += 1

                # Ensure response_data is not None
                if response_data is None:
                    response_data = self._create_error_response("No response generated", session_id)

                # Return a BLOCK result with the local response
                return create_block_result(
                    response_data=response_data, message=f"Processed prompt command locally"
                )
            else:
                self.stats["commands_continued"] += 1

                # Some prompt commands might want to continue to LLM
                return create_continue_result(message="Prompt command processed, continuing to LLM")

        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Error processing prompt command: {e}", exc_info=True)

            # Extract session ID for error response
            session_id = self._resolve_session_id(payload)

            # On error, create a local error response and block
            error_response = self._create_error_response(str(e), session_id)
            return create_block_result(
                response_data=error_response, message=f"Error processing prompt command: {e}"
            )

    async def _process_prompt_command(
        self, message: str, payload: PayloadContext, session_id: str
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Process a prompt command message.

        Args:
            message: Full message text starting with 'prompt:'
            payload: PayloadContext for the request

        Returns:
            Tuple of (response_dict, should_block)
        """
        try:
            # Parse command from message
            if not message.lower().startswith("prompt:"):
                return None, False

            command_text = message[7:].strip()  # Remove "prompt:" prefix

            # Handle bare prompt: command
            if not command_text:
                return self._create_help_response(session_id), True

            # Parse command and arguments
            parts = command_text.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            # Handle built-in commands
            if command == "help":
                return await self._handle_help(args, payload, session_id), True
            elif command in ["add", "list", "remove", "clear"]:
                return (
                    await self._handle_cli_mirrored_command(command, args, payload, session_id),
                    True,
                )
            else:
                # Try to parse as natural language command
                return (
                    await self._handle_natural_language_command(command_text, payload, session_id),
                    True,
                )

        except Exception as e:
            self.logger.error(f"Error processing prompt command: {e}", exc_info=True)
            return self._create_error_response(f"Command processing error: {e}", session_id), True

    async def _handle_help(
        self, args: List[str], _payload: PayloadContext, session_id: str
    ) -> Dict[str, Any]:
        """Handle help command using CLI bridge."""
        try:
            from ...chat.shared.cli_bridge import CLIBridge

            if args:
                # Help for specific command
                specific_command = args[0].lower()
                help_text = CLIBridge.generate_command_help("prompt", specific_command)
            else:
                # General help
                help_text = CLIBridge.generate_command_help("prompt")

            return self._create_text_response(help_text, session_id)

        except Exception as e:
            self.logger.error(f"Error generating help: {e}")
            # Fallback help
            help_text = """Prompt Chat Commands

Commands prefixed with 'prompt:' are processed locally without sending to the LLM.
This saves tokens and provides immediate responses.

Available commands:
- prompt:help [command] - Show this help or help for specific command
- prompt:add <rule> - Add a prompt injection rule with natural language
- prompt:list - List all prompt injection rules
- prompt:remove <search> - Remove rules containing search term
- prompt:clear <target> - Clear rules (temp/all/expired)

Natural Language Examples:
- prompt:add use staging database (24h)
- prompt:add never commit secrets (permanent)
- prompt:add activate virtual environment
- prompt:list
- prompt:remove staging
- prompt:clear temp

Auto-Detection Features:
✅ Duration parsing: (24h), (permanent), (session)
✅ Priority keywords: never=critical, always=high
✅ Category detection: database=setup, secrets=security

Use 'prompt:help add' for detailed help on specific commands.
"""
            return self._create_text_response(help_text, session_id)

    async def _handle_cli_mirrored_command(
        self, command: str, args: List[str], payload: PayloadContext, session_id: str
    ) -> Dict[str, Any]:
        """Handle CLI-mirrored commands (add, list, remove, clear)."""
        try:
            manager = PromptInjectManager()

            if command == "add":
                return await self._handle_add_command(args, manager, session_id)
            elif command == "list":
                return await self._handle_list_command(args, manager, session_id)
            elif command in ["remove", "delete"]:
                return await self._handle_remove_command(args, manager, session_id)
            elif command == "clear":
                return await self._handle_clear_command(args, manager, session_id)
            else:
                return self._create_error_response(f"Unknown command: {command}", session_id)

        except Exception as e:
            self.logger.error(f"Error executing CLI command '{command}': {e}")
            return self._create_error_response(f"Command execution failed: {e}", session_id)

    async def _handle_natural_language_command(
        self, command_text: str, payload: PayloadContext, session_id: str
    ) -> Dict[str, Any]:
        """Handle natural language commands like 'add use database (24h)'."""
        try:
            from ...servers.mcp_server.tools.prompt_inject import PromptInjectParser

            parser = PromptInjectParser()

            # Try to parse as natural language
            parsed = parser.parse_command(command_text)

            if parsed["action"] == "add":
                # Convert to CLI command
                return await self._handle_cli_mirrored_command(
                    "add", [parsed["content"]], payload, session_id
                )
            elif parsed["action"] == "list":
                return await self._handle_cli_mirrored_command("list", [], payload, session_id)
            elif parsed["action"] == "remove":
                return await self._handle_cli_mirrored_command(
                    "remove", [parsed["content_contains"]], payload, session_id
                )
            else:
                # Unknown command
                return self._create_unknown_command_response(command_text, session_id)

        except Exception as e:
            self.logger.error(f"Error processing natural language command: {e}")
            return self._create_error_response(f"Natural language parsing failed: {e}", session_id)

    def _create_help_response(self, session_id: str = "default") -> Dict[str, Any]:
        """Create a help response."""
        help_text = """Prompt Injection Commands

Available commands:
- prompt:help - Show this help
- prompt:add <rule> - Add a prompt injection rule
- prompt:list - List all rules
- prompt:remove <search> - Remove rules by search term
- prompt:clear <target> - Clear rules (temp/all/expired)

Examples:
- prompt:add use staging database (24h)
- prompt:add never commit secrets (permanent)
- prompt:list
- prompt:remove database

Use 'prompt:help <command>' for specific help.
"""
        return self._create_text_response(help_text, session_id)

    def _create_text_response(self, text: str, session_id: str = "default") -> Dict[str, Any]:
        """Create a text response."""
        # Add invisible marker for filtering in subsequent requests
        marked_text = f"\u200b[CG:SESSION:{session_id}]{text}\u200b\u200b"
        return {
            "id": "prompt-response",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": marked_text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": "prompt-plugin",
        }

    def _create_cli_result_response(
        self, result: Any, session_id: str = "default"
    ) -> Dict[str, Any]:
        """Create a response from CLI command result."""
        if isinstance(result, dict) and "error" in result:
            return self._create_error_response(result["error"], session_id)

        # Format the result as text
        content = str(result) if result else "Command completed successfully."

        return self._create_text_response(content, session_id)

    def _create_error_response(
        self, error_message: str, session_id: str = "default"
    ) -> Dict[str, Any]:
        """Create an error response."""
        # Add invisible marker for filtering in subsequent requests
        marked_text = (
            f"\u200b[CG:SESSION:{session_id}]❌ Prompt Command Error: {error_message}\u200b\u200b"
        )
        return {
            "id": "prompt-error",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": marked_text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": "prompt-plugin",
        }

    def _create_unknown_command_response(
        self, command: str, session_id: str = "default"
    ) -> Dict[str, Any]:
        """Create a response for unknown commands."""
        return self._create_text_response(
            f"❓ Unknown prompt command: '{command}'\n\n"
            "Available commands: add, list, remove, clear, help\n"
            "Use 'prompt:help' for more information.",
            session_id,
        )

    def _resolve_session_id(self, payload: PayloadContext) -> str:
        """Resolve session ID using the unified SessionKeyResolver."""
        try:
            # Extract base session ID from payload
            base_session_id = "default"

            # Try to get session ID from payload attributes
            if hasattr(payload, "session_id") and payload.session_id:
                base_session_id = payload.session_id
            # Try to get from request metadata
            elif hasattr(payload, "request_data") and payload.request_data:
                metadata = payload.request_data.get("metadata", {})
                if "session_id" in metadata:
                    base_session_id = metadata["session_id"]

            # Use SessionKeyResolver to create composite key with user namespace support
            return SessionKeyResolver.resolve_session_key(payload, base_session_id)

        except Exception as e:
            self.logger.debug(f"Could not resolve session ID: {e}")
            # Fallback with SessionKeyResolver
            return SessionKeyResolver.resolve_session_key(None, "default")

    def get_stats(self) -> Dict[str, int]:
        """Get plugin statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset plugin statistics."""
        self.stats = {
            "commands_processed": 0,
            "commands_blocked": 0,
            "commands_continued": 0,
            "errors": 0,
        }

    async def _handle_add_command(
        self, args: List[str], manager: PromptInjectManager, session_id: str
    ) -> Dict[str, Any]:
        """Handle add command with natural language parsing."""
        try:
            if not args:
                return self._create_error_response("Add command requires rule text", session_id)

            rule_text = " ".join(args)
            parser = PromptInjectParser()

            # Parse the natural language rule
            command_str = f"add: {rule_text}"
            parsed = parser.parse_command(command_str)

            if parsed["action"] != "add":
                return self._create_error_response(
                    "Failed to parse rule as add command", session_id
                )

            # Add the rule
            rule = await manager.add_rule(
                session_id=session_id,
                content=parsed["content"],
                expires_in_hours=parsed.get("expires_in_hours"),
                category=parsed.get("category", "general"),
                priority=parsed.get("priority", 1),
            )

            expiry_info = "session"
            if rule.expires_at:
                expiry_info = f"expires {rule.expires_at.strftime('%Y-%m-%d %H:%M')}"

            return self._create_text_response(
                f"✅ Added prompt rule: {parsed['content']}\n"
                f"Category: {rule.category} | Priority: {rule.priority} | {expiry_info}",
                session_id,
            )

        except Exception as e:
            self.logger.error(f"Error in add command: {e}")
            return self._create_error_response(f"Failed to add rule: {str(e)}", session_id)

    async def _handle_list_command(
        self, args: List[str], manager: PromptInjectManager, session_id: str
    ) -> Dict[str, Any]:
        """Handle list command."""
        try:
            show_all = "all" in args
            rules = await manager.list_rules(
                session_id=session_id, active_only=not show_all, include_expired=show_all
            )

            if not rules:
                return self._create_text_response(
                    "No prompt rules found.\n\nTry: prompt:add use staging database (24h)",
                    session_id,
                )

            response_lines = [f"📋 Prompt Rules ({len(rules)} total):"]

            for rule in rules:
                status = "🟢  Active"
                if not rule.active:
                    status = "🔴  Inactive"

                expiry = "session"
                if rule.expires_at:
                    expiry = rule.expires_at.strftime("%Y-%m-%d %H:%M")

                response_lines.append(
                    f"  • {rule.content[:60]}{'...' if len(rule.content) > 60 else ''}\n"
                    f"    {status} | Priority: {rule.priority} | Category: {rule.category} | Expires: {expiry}"
                )

            return self._create_text_response("\n".join(response_lines), session_id)

        except Exception as e:
            self.logger.error(f"Error in list command: {e}")
            return self._create_error_response(f"Failed to list rules: {str(e)}", session_id)

    async def _handle_remove_command(
        self, args: List[str], manager: PromptInjectManager, session_id: str
    ) -> Dict[str, Any]:
        """Handle remove command."""
        try:
            if not args:
                return self._create_error_response(
                    "Remove command requires search term", session_id
                )

            search_term = " ".join(args)
            removed_rules = await manager.remove_rule(
                session_id=session_id, content_contains=search_term
            )

            if not removed_rules:
                return self._create_text_response(
                    f"No rules found matching '{search_term}'", session_id
                )

            response_lines = [f"✅ Removed {len(removed_rules)} rule(s):"]
            for rule in removed_rules:
                response_lines.append(f"  • {rule.content}")

            return self._create_text_response("\n".join(response_lines), session_id)

        except Exception as e:
            self.logger.error(f"Error in remove command: {e}")
            return self._create_error_response(f"Failed to remove rules: {str(e)}", session_id)

    async def _handle_clear_command(
        self, args: List[str], manager: PromptInjectManager, session_id: str
    ) -> Dict[str, Any]:
        """Handle clear command."""
        try:
            target = args[0] if args else "temp"
            if target not in ["temp", "all", "expired"]:
                return self._create_error_response(
                    "Clear target must be: temp, all, or expired", session_id
                )

            # Get all rules and filter by target
            all_rules = await manager.list_rules(
                session_id=session_id, active_only=False, include_expired=True
            )

            if not all_rules:
                return self._create_text_response("No prompt rules to clear.", session_id)

            removed_count = 0
            from datetime import datetime

            now = datetime.now()

            for rule in all_rules:
                should_remove = False
                if target == "all":
                    should_remove = True
                elif target == "temp" and rule.expires_at:
                    should_remove = True
                elif target == "expired" and rule.expires_at and rule.expires_at < now:
                    should_remove = True

                if should_remove:
                    removed_rules = await manager.remove_rule(
                        session_id=session_id, rule_id=rule.id
                    )
                    removed_count += len(removed_rules)

            return self._create_text_response(
                f"✅ Cleared {removed_count} {target} rule(s)", session_id
            )

        except Exception as e:
            self.logger.error(f"Error in clear command: {e}")
            return self._create_error_response(f"Failed to clear rules: {str(e)}", session_id)


# Create plugin instance for method binding
_plugin_instance = PromptChatPlugin()


@command("prompt:")
async def prompt_command_handler(message: str, payload: PayloadContext) -> HookResult:
    """Handle prompt: prefixed messages via decorator."""
    return await _plugin_instance.prompt_hook_callback(message, payload)
