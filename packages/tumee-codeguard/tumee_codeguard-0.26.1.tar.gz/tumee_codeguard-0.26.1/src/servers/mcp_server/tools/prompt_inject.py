"""
Unified prompt injection tool for LLM-friendly rule management.

This tool replaces the complex 3-tool urgent_notes system with a single
intuitive interface that uses natural language parsing.
"""

import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

from fastmcp.server.context import Context

from ....core.formatters import FormatterRegistry
from ....core.scope.session_resolver import SessionKeyResolver
from ..mcp_server import mcp
from .modules.prompt_inject_core import (
    PackFileManager,
    PackSessionManager,
    PromptInjectManager,
    TemplatePack,
    handle_create_pack,
    handle_export_pack,
)
from .prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class PromptInjectActions(Enum):
    """Action constants for prompt injection operations."""

    ADD = "add"
    REMOVE = "remove"
    LIST = "list"
    CLEAR_EXPIRED = "clear_expired"
    CLEAR_TEMPORARY = "clear_temporary"
    CLEAR_ALL = "clear_all"

    # Template pack actions (for future implementation)
    INSTALL_PACK = "install_pack"
    UNINSTALL_PACK = "uninstall_pack"
    ENABLE_PACK = "enable_pack"
    DISABLE_PACK = "disable_pack"
    LIST_PACKS = "list_packs"
    EXPORT_PACK = "export_pack"
    CREATE_PACK = "create_pack"


# Global prompt injection manager (reuse existing backend)
_prompt_manager = PromptInjectManager()

# Global parser instance to avoid recreating compiled patterns
_parser_instance = None


class PromptInjectParser:
    """Parser for natural language prompt injection commands."""

    # Priority keywords mapping
    PRIORITY_KEYWORDS = {
        "never": 5,
        "always": 4,
        "critical": 5,
        "important": 4,
        "urgent": 4,
        "must": 4,
        "should": 3,
        "please": 2,
        "remember": 2,
    }

    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        "security": ["secret", "key", "password", "auth", "token", "secure", "permission"],
        "setup": ["environment", "database", "config", "install", "activate", "venv", "virtual"],
        "process": ["test", "build", "deploy", "commit", "push", "validate", "check"],
    }

    def __init__(self):
        """Initialize parser with compiled regex patterns."""
        self._compiled_patterns: List[Tuple[re.Pattern, callable]] = [
            (re.compile(r"\((\d+)\s*h(?:ours?)?\)", re.IGNORECASE), lambda m: int(m.group(1))),
            (re.compile(r"\((\d+)\s*hours?\)", re.IGNORECASE), lambda m: int(m.group(1))),
            (re.compile(r"\(24\s*h(?:ours?)?\)", re.IGNORECASE), lambda m: 24),
            (
                re.compile(r"\(until\s+friday\)", re.IGNORECASE),
                lambda m: self._hours_until_friday(),
            ),
            (re.compile(r"\(session\)", re.IGNORECASE), lambda m: None),
            (re.compile(r"\(permanent\)", re.IGNORECASE), lambda m: None),
            (re.compile(r"\(never\)", re.IGNORECASE), lambda m: None),
        ]

    def parse_command(self, command: str) -> Dict:
        """
        Parse a natural language command into structured data.

        Examples:
        - "add: use staging database (24h)"
        - "add: never commit secrets (permanent)"
        - "list"
        - "remove: staging"
        """
        command = command.strip()

        # Determine action
        if command.startswith("add:"):
            return self._parse_add_command(command[4:].strip())
        elif command.startswith("remove:"):
            return self._parse_remove_command(command[7:].strip())
        elif command in ["list", "list all", "list active"]:
            return self._parse_list_command(command)
        elif command.startswith("clear"):
            return self._parse_clear_command(command)
        # Template pack commands
        elif command.startswith("install pack:"):
            return self._parse_install_pack_command(command[13:].strip())
        elif command.startswith("uninstall pack:"):
            return self._parse_uninstall_pack_command(command[15:].strip())
        elif command.startswith("enable pack:"):
            return self._parse_enable_pack_command(command[12:].strip())
        elif command.startswith("disable pack:"):
            return self._parse_disable_pack_command(command[13:].strip())
        elif command.startswith("export pack:"):
            return self._parse_export_pack_command(command[12:].strip())
        elif command.startswith("create pack:"):
            return self._parse_create_pack_command(command[12:].strip())
        elif command in ["list packs", "list packs all"]:
            return self._parse_list_packs_command(command)
        else:
            # Try to infer action from content
            return self._infer_action(command)

    def _parse_add_command(self, content: str) -> Dict:
        """Parse an add command with content and optional duration."""
        # Extract duration pattern
        expires_in_hours = None
        duration_match = None

        for pattern, parser in self._compiled_patterns:
            match = pattern.search(content)
            if match:
                duration_match = match
                try:
                    expires_in_hours = parser(match)
                except:
                    expires_in_hours = None
                break

        # Remove duration from content
        if duration_match:
            content = content.replace(duration_match.group(0), "").strip()

        # Detect priority from keywords
        priority = 1
        content_lower = content.lower()
        for keyword, prio in self.PRIORITY_KEYWORDS.items():
            if keyword in content_lower:
                priority = max(priority, prio)

        # Detect category
        category = "general"
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in content_lower for kw in keywords):
                category = cat
                break

        return {
            "action": PromptInjectActions.ADD.value,
            "content": content,
            "expires_in_hours": expires_in_hours,
            "priority": priority,
            "category": category,
        }

    def _parse_remove_command(self, content: str) -> Dict:
        """Parse a remove command."""
        return {
            "action": PromptInjectActions.REMOVE.value,
            "content_contains": content,
        }

    def _parse_list_command(self, command: str) -> Dict:
        """Parse a list command."""
        return {
            "action": PromptInjectActions.LIST.value,
            "active_only": "all" not in command,
            "include_expired": "all" in command,
        }

    def _parse_clear_command(self, command: str) -> Dict:
        """Parse a clear command."""
        if "temp" in command or "temporary" in command:
            return {"action": PromptInjectActions.CLEAR_TEMPORARY.value}
        elif "all" in command:
            return {"action": PromptInjectActions.CLEAR_ALL.value}
        else:
            return {"action": PromptInjectActions.CLEAR_EXPIRED.value}

    def _infer_action(self, command: str) -> Dict:
        """Try to infer action from raw content."""
        # If it looks like a rule, assume add
        if len(command) > 10 and any(
            word in command.lower() for word in ["use", "never", "always", "remember"]
        ):
            return self._parse_add_command(command)

        # Otherwise, default to list
        return self._parse_list_command("list")

    def _hours_until_friday(self) -> int:
        """Calculate hours until next Friday."""
        now = datetime.now()
        days_ahead = 4 - now.weekday()  # Friday is 4
        if days_ahead <= 0:  # Today is Friday or later
            days_ahead += 7
        target = now + timedelta(days=days_ahead)
        target = target.replace(hour=23, minute=59, second=59)
        return int((target - now).total_seconds() / 3600)

    def _parse_install_pack_command(self, content: str) -> Dict:
        """Parse an install pack command."""
        return {
            "action": PromptInjectActions.INSTALL_PACK.value,
            "pack_file": content.strip(),
        }

    def _parse_uninstall_pack_command(self, content: str) -> Dict:
        """Parse an uninstall pack command."""
        return {
            "action": PromptInjectActions.UNINSTALL_PACK.value,
            "pack_name": content.strip(),
        }

    def _parse_enable_pack_command(self, content: str) -> Dict:
        """Parse an enable pack command."""
        return {
            "action": PromptInjectActions.ENABLE_PACK.value,
            "pack_name": content.strip(),
        }

    def _parse_disable_pack_command(self, content: str) -> Dict:
        """Parse a disable pack command."""
        return {
            "action": PromptInjectActions.DISABLE_PACK.value,
            "pack_name": content.strip(),
        }

    def _parse_export_pack_command(self, content: str) -> Dict:
        """Parse an export pack command."""
        return {
            "action": PromptInjectActions.EXPORT_PACK.value,
            "pack_name": content.strip(),
        }

    def _parse_create_pack_command(self, content: str) -> Dict:
        """Parse a create pack command."""
        return {
            "action": PromptInjectActions.CREATE_PACK.value,
            "pack_name": content.strip(),
        }

    def _parse_list_packs_command(self, command: str) -> Dict:
        """Parse a list packs command."""
        return {
            "action": PromptInjectActions.LIST_PACKS.value,
            "include_disabled": "all" in command,
        }


@mcp.tool(description=load_prompt("prompt_inject"))
async def prompt_inject(
    session_id: str,
    command: str,
    ctx: Context = None,
) -> Dict:
    """
    Unified prompt injection tool with natural language interface.

    Args:
        session_id: Session identifier
        command: Natural language command (e.g., "add: use staging db (24h)")
        ctx: MCP context
    """
    try:
        # Use SessionKeyResolver for consistent session key generation
        composite_key = SessionKeyResolver.resolve_session_key(ctx, session_id)
        logger.debug(f"Resolved session key: {composite_key}")
    except Exception as e:
        return {"error": f"Session resolution failed: {str(e)}", "tool": "prompt_inject"}

    try:
        global _parser_instance
        if _parser_instance is None:
            _parser_instance = PromptInjectParser()

        parsed = _parser_instance.parse_command(command)

        # Use composite_key for all operations to ensure consistency
        action = parsed["action"]
        if action == PromptInjectActions.ADD.value:
            return await _handle_add(composite_key, parsed)
        elif action == PromptInjectActions.REMOVE.value:
            return await _handle_remove(composite_key, parsed)
        elif action == PromptInjectActions.LIST.value:
            return await _handle_list(composite_key, parsed)
        elif action in [
            PromptInjectActions.CLEAR_EXPIRED.value,
            PromptInjectActions.CLEAR_TEMPORARY.value,
            PromptInjectActions.CLEAR_ALL.value,
        ]:
            return await _handle_clear(composite_key, parsed)
        # Template pack actions
        elif action in [
            PromptInjectActions.INSTALL_PACK.value,
            PromptInjectActions.UNINSTALL_PACK.value,
            PromptInjectActions.ENABLE_PACK.value,
            PromptInjectActions.DISABLE_PACK.value,
            PromptInjectActions.EXPORT_PACK.value,
            PromptInjectActions.CREATE_PACK.value,
            PromptInjectActions.LIST_PACKS.value,
        ]:
            return await _handle_template_pack(composite_key, parsed)
        else:
            return {
                "error": f"Unknown action: {parsed['action']}",
                "tool": "prompt_inject",
                "suggestion": "Try: 'add: your rule here', 'list', 'install pack: file.json', or 'list packs'",
            }

    except Exception as e:
        logger.error(f"Error in prompt_inject: {e}")
        return {
            "error": f"Failed to process command: {str(e)}",
            "tool": "prompt_inject",
            "command": command,
            "help": "Try: prompt_inject(session_id, 'add: your rule (duration)')",
        }


async def _handle_add(session_id: str, parsed: Dict) -> Dict:
    """Handle add action."""
    try:
        note = await _prompt_manager.add_rule(
            session_id=session_id,
            content=parsed["content"],
            expires_in_hours=parsed.get("expires_in_hours"),
            category=parsed.get("category", "general"),
            priority=parsed.get("priority", 1),
        )

        # Format expiry info
        expiry_info = "session"
        if note.expires_at:
            expiry_info = f"expires {note.expires_at.strftime('%Y-%m-%d %H:%M UTC')}"
        elif parsed.get("expires_in_hours"):
            expiry_info = f"expires in {parsed['expires_in_hours']} hours"

        # Count active rules
        active_notes = await _prompt_manager.list_rules(session_id, active_only=True)

        return {
            "status": "success",
            "action": "added_rule",
            "rule": {
                "id": note.id,
                "content": note.content,
                "category": note.category,
                "priority": note.priority,
                "expires": expiry_info,
            },
            "active_rules_count": len(active_notes),
            "suggestions": [
                "💡 View all rules: prompt_inject(session_id, 'list')",
                "🗑️ Remove rule: prompt_inject(session_id, 'remove: keyword')",
                "⏰ Add temporary rule: prompt_inject(session_id, 'add: rule (24h)')",
            ],
        }

    except Exception as e:
        return {
            "error": f"Failed to add rule: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_remove(session_id: str, parsed: Dict) -> Dict:
    """Handle remove action."""
    try:
        removed_notes = await _prompt_manager.remove_rule(
            session_id=session_id,
            content_contains=parsed["content_contains"],
        )

        if not removed_notes:
            return {
                "status": "no_matches",
                "message": f"No rules found containing '{parsed['content_contains']}'",
                "suggestion": "💡 List rules: prompt_inject(session_id, 'list')",
            }

        removed_data = [
            {
                "id": note.id,
                "content": note.content,
                "category": note.category,
            }
            for note in removed_notes
        ]

        return {
            "status": "success",
            "action": "removed_rules",
            "removed_count": len(removed_notes),
            "removed_rules": removed_data,
            "search_term": parsed["content_contains"],
        }

    except Exception as e:
        return {
            "error": f"Failed to remove rules: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_list(session_id: str, parsed: Dict) -> Dict:
    """Handle list action."""
    try:
        notes = await _prompt_manager.list_rules(
            session_id=session_id,
            active_only=parsed.get("active_only", True),
            include_expired=parsed.get("include_expired", False),
        )

        if not notes:
            return {
                "status": "empty",
                "message": "No active rules found",
                "suggestions": [
                    "➕ Add rule: prompt_inject(session_id, 'add: your rule here')",
                    "📚 Examples: 'add: use staging db (24h)', 'add: never commit secrets'",
                ],
            }

        # Format notes
        rules = []
        for note in notes:
            rule_info = {
                "id": note.id,
                "content": note.content,
                "category": note.category,
                "priority": note.priority,
                "active": note.active,
                "created": note.created_at.strftime("%Y-%m-%d %H:%M"),
            }

            if note.expires_at:
                rule_info["expires"] = note.expires_at.strftime("%Y-%m-%d %H:%M")
                rule_info["expired"] = note.expires_at < datetime.now()
            else:
                rule_info["expires"] = "session"
                rule_info["expired"] = False

            rules.append(rule_info)

        # Category summary
        categories = {}
        for note in notes:
            categories[note.category] = categories.get(note.category, 0) + 1

        return {
            "status": "success",
            "action": "listed_rules",
            "rules": rules,
            "total_count": len(rules),
            "categories": categories,
            "quick_actions": [
                "add: new rule",
                "remove: keyword",
                "clear temp",
            ],
        }

    except Exception as e:
        return {
            "error": f"Failed to list rules: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_clear(session_id: str, parsed: Dict) -> Dict:
    """Handle clear actions."""
    try:
        action = parsed["action"]

        if action == PromptInjectActions.CLEAR_TEMPORARY.value:
            # Remove rules with expiration dates that have passed
            removed_notes = await _prompt_manager.clear_expired_rules(session_id)
            action_desc = "temporary/expired"
        elif action == PromptInjectActions.CLEAR_EXPIRED.value:
            # Remove only expired rules
            removed_notes = await _prompt_manager.clear_expired_rules(session_id)
            action_desc = "expired"
        elif action == PromptInjectActions.CLEAR_ALL.value:
            # Remove all rules (destructive)
            removed_notes = await _prompt_manager.clear_all_rules(session_id)
            action_desc = "all"
        else:
            return {
                "error": f"Unknown clear action: {action}",
                "tool": "prompt_inject",
            }

        if not removed_notes:
            return {
                "status": "no_matches",
                "message": f"No {action_desc} rules found to clear",
                "suggestion": "💡 List rules: prompt_inject(session_id, 'list')",
            }

        removed_data = [
            {
                "id": note.id,
                "content": note.content,
                "category": note.category,
            }
            for note in removed_notes
        ]

        return {
            "status": "success",
            "action": f"cleared_{action_desc.replace('/', '_')}_rules",
            "cleared_count": len(removed_notes),
            "cleared_rules": removed_data,
            "message": f"Cleared {len(removed_notes)} {action_desc} rules",
        }

    except Exception as e:
        return {
            "error": f"Failed to clear rules: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_template_pack(session_id: str, parsed: Dict) -> Dict:
    """Handle template pack actions."""
    action = parsed["action"]

    try:
        if action == PromptInjectActions.LIST_PACKS.value:
            return await _handle_list_packs(session_id, parsed)
        elif action == PromptInjectActions.INSTALL_PACK.value:
            return await _handle_install_pack(session_id, parsed)
        elif action == PromptInjectActions.UNINSTALL_PACK.value:
            return await _handle_uninstall_pack(session_id, parsed)
        elif action == PromptInjectActions.ENABLE_PACK.value:
            return await _handle_enable_pack(session_id, parsed)
        elif action == PromptInjectActions.DISABLE_PACK.value:
            return await _handle_disable_pack(session_id, parsed)
        elif action == PromptInjectActions.EXPORT_PACK.value:
            return await handle_export_pack(session_id, parsed, _prompt_manager)
        elif action == PromptInjectActions.CREATE_PACK.value:
            return await handle_create_pack(session_id, parsed, _prompt_manager)
        else:
            return {
                "error": f"Unknown template pack action: {action}",
                "tool": "prompt_inject",
            }

    except Exception as e:
        return {
            "error": f"Failed to process template pack command: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_list_packs(session_id: str, parsed: Dict) -> Dict:
    """Handle list packs action."""
    try:
        session = await _prompt_manager.storage.load_session(session_id)

        packs = []
        for pack in session.template_packs.values():
            if not parsed.get("include_disabled", False) and not pack.enabled:
                continue

            pack_info = {
                "id": pack.id,
                "name": pack.name,
                "description": pack.description,
                "version": pack.version,
                "author": pack.author,
                "enabled": pack.enabled,
                "rule_count": len(pack.rules),
                "created": pack.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            packs.append(pack_info)

        if not packs:
            return {
                "status": "empty",
                "message": "No template packs installed",
                "suggestions": [
                    "📦 Install pack: prompt_inject(session_id, 'install pack: security-rules.json')",
                    "🎯 Create pack: prompt_inject(session_id, 'create pack: my-rules')",
                ],
            }

        # Sort by name
        packs.sort(key=lambda p: p["name"])

        return {
            "status": "success",
            "action": "listed_packs",
            "packs": packs,
            "total_count": len(packs),
            "quick_actions": [
                "install pack: filename.json",
                "enable pack: name",
                "export pack: name",
            ],
        }

    except Exception as e:
        return {
            "error": f"Failed to list packs: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_install_pack(session_id: str, parsed: Dict) -> Dict:
    """Handle install pack action."""
    try:
        pack_file = parsed.get("pack_file")
        if not pack_file:
            return {
                "error": "Pack file name is required",
                "tool": "prompt_inject",
                "suggestion": "Try: prompt_inject(session_id, 'install pack: security-rules.json')",
            }

        # Find the pack file
        pack_path = PackFileManager.find_pack_file(pack_file)
        if not pack_path:
            return {
                "error": f"Pack file '{pack_file}' not found",
                "tool": "prompt_inject",
                "suggestion": "Place the JSON file in current directory or ./packs/ folder",
            }

        # Load and validate pack data
        try:
            pack_data = PackFileManager.load_pack_from_file(pack_path)
        except ValueError as e:
            return {
                "error": str(e),
                "tool": "prompt_inject",
            }

        # Create template pack from import data
        try:
            template_pack = TemplatePack.from_import_format(pack_data)
        except Exception as e:
            return {
                "error": f"Failed to parse pack data: {str(e)}",
                "tool": "prompt_inject",
            }

        # Load session and check for name conflicts
        session = await _prompt_manager.storage.load_session(session_id)

        if PackSessionManager.check_name_conflict(session, template_pack.name):
            return {
                "error": f"Template pack '{template_pack.name}' already installed",
                "tool": "prompt_inject",
                "suggestion": f"Try: prompt_inject(session_id, 'uninstall pack: {template_pack.name}') first",
            }

        # Install the pack
        session.template_packs[template_pack.id] = template_pack
        await _prompt_manager.storage.save_session(session)

        return {
            "status": "success",
            "action": "installed_pack",
            "pack_name": template_pack.name,
            "pack_version": template_pack.version,
            "pack_author": template_pack.author,
            "rules_installed": len(template_pack.rules),
            "pack_id": template_pack.id,
            "message": f"Installed template pack '{template_pack.name}' with {len(template_pack.rules)} rules",
            "suggestions": [
                f"🔍 View rules: prompt_inject(session_id, 'list')",
                f"🔧 Disable if needed: prompt_inject(session_id, 'disable pack: {template_pack.name}')",
            ],
        }

    except Exception as e:
        return {
            "error": f"Failed to install pack: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_uninstall_pack(session_id: str, parsed: Dict) -> Dict:
    """Handle uninstall pack action."""
    try:
        pack_name = parsed.get("pack_name")
        session = await _prompt_manager.storage.load_session(session_id)

        # Find pack by name
        pack_to_remove, pack_id_to_remove = PackSessionManager.find_pack_by_name(session, pack_name)

        if not pack_to_remove:
            return {
                "status": "not_found",
                "message": f"Template pack '{pack_name}' not found",
                "suggestion": "💡 List packs: prompt_inject(session_id, 'list packs')",
            }

        # Remove the pack
        del session.template_packs[pack_id_to_remove]
        await _prompt_manager.storage.save_session(session)

        return {
            "status": "success",
            "action": "uninstalled_pack",
            "pack_name": pack_name,
            "rules_removed": len(pack_to_remove.rules),
            "message": f"Uninstalled template pack '{pack_name}' with {len(pack_to_remove.rules)} rules",
        }

    except Exception as e:
        return {
            "error": f"Failed to uninstall pack: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_enable_pack(session_id: str, parsed: Dict) -> Dict:
    """Handle enable pack action."""
    try:
        pack_name = parsed.get("pack_name")
        session = await _prompt_manager.storage.load_session(session_id)

        # Find pack by name
        pack_found = None
        for pack in session.template_packs.values():
            if pack.name == pack_name:
                pack_found = pack
                break

        if not pack_found:
            return {
                "status": "not_found",
                "message": f"Template pack '{pack_name}' not found",
                "suggestion": "💡 List packs: prompt_inject(session_id, 'list packs all')",
            }

        if pack_found.enabled:
            return {
                "status": "already_enabled",
                "message": f"Template pack '{pack_name}' is already enabled",
            }

        # Enable the pack
        pack_found.enabled = True
        await _prompt_manager.storage.save_session(session)

        return {
            "status": "success",
            "action": "enabled_pack",
            "pack_name": pack_name,
            "active_rules": len([r for r in pack_found.rules.values() if r.active]),
            "message": f"Enabled template pack '{pack_name}' with {len(pack_found.rules)} rules",
        }

    except Exception as e:
        return {
            "error": f"Failed to enable pack: {str(e)}",
            "tool": "prompt_inject",
        }


async def _handle_disable_pack(session_id: str, parsed: Dict) -> Dict:
    """Handle disable pack action."""
    try:
        pack_name = parsed.get("pack_name")
        session = await _prompt_manager.storage.load_session(session_id)

        # Find pack by name
        pack_found = None
        for pack in session.template_packs.values():
            if pack.name == pack_name:
                pack_found = pack
                break

        if not pack_found:
            return {
                "status": "not_found",
                "message": f"Template pack '{pack_name}' not found",
                "suggestion": "💡 List packs: prompt_inject(session_id, 'list packs all')",
            }

        if not pack_found.enabled:
            return {
                "status": "already_disabled",
                "message": f"Template pack '{pack_name}' is already disabled",
            }

        # Disable the pack
        pack_found.enabled = False
        await _prompt_manager.storage.save_session(session)

        return {
            "status": "success",
            "action": "disabled_pack",
            "pack_name": pack_name,
            "message": f"Disabled template pack '{pack_name}' - {len(pack_found.rules)} rules are now inactive",
        }

    except Exception as e:
        return {
            "error": f"Failed to disable pack: {str(e)}",
            "tool": "prompt_inject",
        }
