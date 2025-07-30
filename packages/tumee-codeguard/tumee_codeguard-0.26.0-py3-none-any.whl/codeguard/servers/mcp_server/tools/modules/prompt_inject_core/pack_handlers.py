"""
Template pack action handlers for import/export and management operations.

This module contains the implementation for template pack operations that
were too large to keep in the main prompt_inject.py file.
"""

import logging
from typing import Dict

from .core import TemplatePack
from .manager import PromptInjectManager
from .pack_utils import PackFileManager, PackSessionManager

logger = logging.getLogger(__name__)


async def handle_export_pack(
    session_id: str, parsed: Dict, prompt_manager: PromptInjectManager
) -> Dict:
    """Handle export pack action."""
    try:
        pack_name = parsed.get("pack_name")
        session = await prompt_manager.storage.load_session(session_id)

        # Find pack by name
        pack_to_export, pack_id = PackSessionManager.find_pack_by_name(session, pack_name)

        if not pack_to_export:
            return {
                "status": "not_found",
                "message": f"Template pack '{pack_name}' not found",
                "suggestion": "💡 List packs: prompt_inject(session_id, 'list packs')",
            }

        # Generate export path
        export_path = PackFileManager.get_export_path(pack_to_export.name)

        # Save pack to file
        try:
            PackFileManager.save_pack_to_file(pack_to_export, export_path)
        except ValueError as e:
            return {
                "error": str(e),
                "tool": "prompt_inject",
            }

        return {
            "status": "success",
            "action": "exported_pack",
            "pack_name": pack_to_export.name,
            "export_path": str(export_path),
            "rules_exported": len(pack_to_export.rules),
            "message": f"Exported template pack '{pack_to_export.name}' to {export_path}",
            "suggestions": [
                f"📤 Share file: {export_path}",
                f"📋 View pack: prompt_inject(session_id, 'list')",
            ],
        }

    except Exception as e:
        return {
            "error": f"Failed to export pack: {str(e)}",
            "tool": "prompt_inject",
        }


async def handle_create_pack(
    session_id: str, parsed: Dict, prompt_manager: PromptInjectManager
) -> Dict:
    """Handle create pack action."""
    try:
        pack_name = parsed.get("pack_name")

        if not pack_name or not pack_name.strip():
            return {
                "error": "Pack name is required",
                "tool": "prompt_inject",
                "suggestion": "Try: prompt_inject(session_id, 'create pack: my-development-rules')",
            }

        pack_name = pack_name.strip()
        session = await prompt_manager.storage.load_session(session_id)

        # Check for name conflicts
        if PackSessionManager.check_name_conflict(session, pack_name):
            return {
                "error": f"Template pack '{pack_name}' already exists",
                "tool": "prompt_inject",
                "suggestion": f"Try a different name or use: prompt_inject(session_id, 'uninstall pack: {pack_name}') first",
            }

        # Create new empty template pack
        new_pack = TemplatePack(
            name=pack_name,
            description=f"Custom template pack: {pack_name}",
            version="1.0",
            author="user",
        )

        # Add to session
        session.template_packs[new_pack.id] = new_pack
        await prompt_manager.storage.save_session(session)

        return {
            "status": "success",
            "action": "created_pack",
            "pack_name": new_pack.name,
            "pack_id": new_pack.id,
            "pack_version": new_pack.version,
            "message": f"Created empty template pack '{new_pack.name}'",
            "suggestions": [
                f"➕ Add rules: prompt_inject(session_id, 'add: your rule here')",
                f"📋 View packs: prompt_inject(session_id, 'list packs')",
                f"📤 Export when ready: prompt_inject(session_id, 'export pack: {new_pack.name}')",
            ],
            "next_steps": [
                "Add rules to your new pack using the normal 'add:' command",
                "Rules will be automatically associated with the most recently created pack",
                "Export the pack when you're ready to share it",
            ],
        }

    except Exception as e:
        return {
            "error": f"Failed to create pack: {str(e)}",
            "tool": "prompt_inject",
        }
