"""
Storage backend for prompt injection rules.

Provides file-based and Redis storage options for prompt rule persistence.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .core import PromptInjectSession, PromptRule, RuleType, TemplatePack

logger = logging.getLogger(__name__)


class PromptInjectStorage:
    """
    Storage backend for prompt injection rules with auto-cleanup.
    """

    def __init__(self, storage_type: str = "file", storage_path: Optional[str] = None):
        self.storage_type = storage_type

        if storage_type == "file":
            self.storage_path = Path(storage_path or Path.home() / ".codeguard" / "prompt_inject")
            self.storage_path.mkdir(parents=True, exist_ok=True)
        else:
            # TODO: Redis implementation
            raise NotImplementedError(f"Storage type '{storage_type}' not implemented")

    async def load_session(self, session_id: str) -> PromptInjectSession:
        """
        Load session data from storage.

        Args:
            session_id: Session identifier

        Returns:
            PromptInjectSession (empty if not found)
        """
        if self.storage_type == "file":
            file_path = self.storage_path / f"{session_id}.json"
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    # Load personal rules
                    personal_rules = {}
                    for rule_id, rule_data in data.get("personal_rules", {}).items():
                        rule = self._load_rule_from_data(rule_data)
                        personal_rules[rule_id] = rule

                    # Load template packs
                    template_packs = {}
                    for pack_id, pack_data in data.get("template_packs", {}).items():
                        pack = self._load_template_pack_from_data(pack_data)
                        template_packs[pack_id] = pack

                    session = PromptInjectSession(
                        session_id=session_id,
                        created_at=datetime.fromisoformat(data["created_at"]),
                        personal_rules=personal_rules,
                        template_packs=template_packs,
                        last_cleanup=datetime.fromisoformat(
                            data.get("last_cleanup", data["created_at"])
                        ),
                    )

                    return session

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.error(f"Error loading session {session_id}: {e}")

        # Return empty session if not found or error
        return PromptInjectSession(session_id=session_id)

    async def save_session(self, session: PromptInjectSession) -> bool:
        """
        Save session data to storage.

        Args:
            session: Session to save

        Returns:
            True if saved successfully
        """
        if self.storage_type == "file":
            file_path = self.storage_path / f"{session.session_id}.json"

            try:
                # Convert session to JSON-serializable format
                personal_rules_data = {}
                for rule_id, rule in session.personal_rules.items():
                    personal_rules_data[rule_id] = self._rule_to_data(rule)

                template_packs_data = {}
                for pack_id, pack in session.template_packs.items():
                    template_packs_data[pack_id] = self._template_pack_to_data(pack)

                session_data = {
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "personal_rules": personal_rules_data,
                    "template_packs": template_packs_data,
                    "last_cleanup": session.last_cleanup.isoformat(),
                }

                with open(file_path, "w") as f:
                    json.dump(session_data, f, indent=2)

                return True

            except Exception as e:
                logger.error(f"Error saving session {session.session_id}: {e}")
                return False

        return False

    async def get_active_rules(self, session_id: str) -> List[PromptRule]:
        """
        Get active rules for a session (non-expired and active=True).

        Args:
            session_id: Session identifier

        Returns:
            List of active rules
        """
        session = await self.load_session(session_id)
        return session.get_all_active_rules()

    async def cleanup_expired_rules(self, session_id: str) -> List[PromptRule]:
        """
        Remove expired rules from a session.

        Args:
            session_id: Session identifier

        Returns:
            List of removed rules
        """
        session = await self.load_session(session_id)
        now = datetime.now()

        # Find expired rules in personal rules
        expired_rules = []
        expired_personal_rule_ids = []
        for rule_id, rule in session.personal_rules.items():
            if rule.expires_at and rule.expires_at <= now:
                expired_rules.append(rule)
                expired_personal_rule_ids.append(rule_id)

        # Find expired rules in template packs
        expired_pack_rule_ids = {}  # pack_id -> [rule_ids]
        for pack_id, pack in session.template_packs.items():
            expired_in_pack = []
            for rule_id, rule in pack.rules.items():
                if rule.expires_at and rule.expires_at <= now:
                    expired_rules.append(rule)
                    expired_in_pack.append(rule_id)
            if expired_in_pack:
                expired_pack_rule_ids[pack_id] = expired_in_pack

        # Remove expired personal rules
        for rule_id in expired_personal_rule_ids:
            del session.personal_rules[rule_id]

        # Remove expired pack rules
        for pack_id, rule_ids in expired_pack_rule_ids.items():
            for rule_id in rule_ids:
                del session.template_packs[pack_id].rules[rule_id]

        # Update last cleanup time
        session.last_cleanup = now

        # Save if we removed anything
        if expired_rules:
            await self.save_session(session)
            logger.info(f"Cleaned up {len(expired_rules)} expired rules from session {session_id}")

        return expired_rules

    async def cleanup_all_expired(self) -> Dict[str, int]:
        """
        Clean up expired rules from all sessions.

        Returns:
            Dictionary mapping session_id to number of rules cleaned
        """
        cleanup_results = {}

        if self.storage_type == "file":
            # Find all session files
            for file_path in self.storage_path.glob("*.json"):
                session_id = file_path.stem
                try:
                    cleaned_rules = await self.cleanup_expired_rules(session_id)
                    if cleaned_rules:
                        cleanup_results[session_id] = len(cleaned_rules)
                except Exception as e:
                    logger.error(f"Error cleaning session {session_id}: {e}")

        return cleanup_results

    async def get_all_sessions(self) -> List[str]:
        """
        Get list of all session IDs that have stored data.

        Returns:
            List of session IDs
        """
        sessions = []

        if self.storage_type == "file":
            for file_path in self.storage_path.glob("*.json"):
                sessions.append(file_path.stem)

        return sessions

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete all data for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully
        """
        if self.storage_type == "file":
            file_path = self.storage_path / f"{session_id}.json"
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted session {session_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting session {session_id}: {e}")
                return False

        return False

    def _load_rule_from_data(self, rule_data: Dict) -> PromptRule:
        """Load a PromptRule from JSON data."""
        expires_at = None
        if rule_data.get("expires_at"):
            expires_at = datetime.fromisoformat(rule_data["expires_at"])

        return PromptRule(
            id=rule_data["id"],
            content=rule_data["content"],
            category=rule_data.get("category", "general"),
            priority=rule_data.get("priority", 1),
            created_at=datetime.fromisoformat(rule_data["created_at"]),
            expires_at=expires_at,
            rule_type=RuleType(rule_data.get("rule_type", RuleType.PERSONAL.value)),
            pack_id=rule_data.get("pack_id"),
            active=rule_data.get("active", True),
        )

    def _load_template_pack_from_data(self, pack_data: Dict) -> TemplatePack:
        """Load a TemplatePack from JSON data."""
        pack = TemplatePack(
            id=pack_data["id"],
            name=pack_data["name"],
            description=pack_data.get("description", ""),
            version=pack_data.get("version", "1.0"),
            author=pack_data.get("author", ""),
            created_at=datetime.fromisoformat(pack_data["created_at"]),
            enabled=pack_data.get("enabled", True),
        )

        # Load rules in the pack
        for rule_id, rule_data in pack_data.get("rules", {}).items():
            rule = self._load_rule_from_data(rule_data)
            pack.rules[rule_id] = rule

        return pack

    def _rule_to_data(self, rule: PromptRule) -> Dict:
        """Convert a PromptRule to JSON-serializable data."""
        return {
            "id": rule.id,
            "content": rule.content,
            "category": rule.category,
            "priority": rule.priority,
            "created_at": rule.created_at.isoformat(),
            "expires_at": rule.expires_at.isoformat() if rule.expires_at else None,
            "rule_type": rule.rule_type.value,
            "pack_id": rule.pack_id,
            "active": rule.active,
        }

    def _template_pack_to_data(self, pack: TemplatePack) -> Dict:
        """Convert a TemplatePack to JSON-serializable data."""
        rules_data = {}
        for rule_id, rule in pack.rules.items():
            rules_data[rule_id] = self._rule_to_data(rule)

        return {
            "id": pack.id,
            "name": pack.name,
            "description": pack.description,
            "version": pack.version,
            "author": pack.author,
            "created_at": pack.created_at.isoformat(),
            "enabled": pack.enabled,
            "rules": rules_data,
        }
