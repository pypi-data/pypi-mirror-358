"""
Manager for prompt injection operations.

High-level interface for managing prompt injection rules with formatting
and integration with the LLM proxy.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from .core import PromptRule
from .storage import PromptInjectStorage

logger = logging.getLogger(__name__)


class PromptInjectManager:
    """
    High-level manager for prompt injection rule operations.
    """

    _instance = None
    _initialized = False

    def __new__(cls, storage: Optional[PromptInjectStorage] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, storage: Optional[PromptInjectStorage] = None):
        # Only initialize once
        if not PromptInjectManager._initialized:
            self.storage = storage or PromptInjectStorage()
            PromptInjectManager._initialized = True

    async def add_rule(
        self,
        session_id: str,
        content: str,
        expires_in_hours: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        category: str = "general",
        priority: int = 1,
    ) -> PromptRule:
        """
        Add a new prompt injection rule.

        Args:
            session_id: Session identifier
            content: Rule content
            expires_in_hours: Hours from now to expire (optional)
            expires_at: Specific expiration datetime (optional)
            category: Rule category
            priority: Rule priority (1-5)

        Returns:
            Created PromptRule
        """
        session = await self.storage.load_session(session_id)

        # Validate content - reject empty or whitespace-only content
        cleaned_content = content.strip()
        if not cleaned_content:
            raise ValueError("Rule content cannot be empty or contain only whitespace")

        # Calculate expiration
        expiration = None
        if expires_in_hours:
            expiration = datetime.now() + timedelta(hours=expires_in_hours)
        elif expires_at:
            expiration = expires_at

        # Create rule
        rule = PromptRule(
            content=cleaned_content,
            category=category,
            priority=max(1, min(5, priority)),  # Clamp to 1-5
            expires_at=expiration,
        )

        # Add to session personal rules
        session.personal_rules[rule.id] = rule

        # Save session
        await self.storage.save_session(session)

        logger.info(f"Added prompt rule {rule.id} for session {session_id}")
        return rule

    async def remove_rule(
        self, session_id: str, rule_id: Optional[str] = None, content_contains: Optional[str] = None
    ) -> List[PromptRule]:
        """
        Remove prompt rules by ID or content match.

        Args:
            session_id: Session identifier
            rule_id: Specific rule ID to remove
            content_contains: Remove rules containing this text

        Returns:
            List of removed rules
        """
        session = await self.storage.load_session(session_id)

        removed_rules = []
        to_remove = []

        # Check personal rules
        for rid, rule in session.personal_rules.items():
            should_remove = False

            if rule_id and rid == rule_id:
                should_remove = True
            elif content_contains and content_contains.lower() in rule.content.lower():
                should_remove = True

            if should_remove:
                to_remove.append(rid)
                removed_rules.append(rule)

        # Remove personal rules
        for rid in to_remove:
            del session.personal_rules[rid]

        if removed_rules:
            await self.storage.save_session(session)
            logger.info(f"Removed {len(removed_rules)} prompt rules from session {session_id}")

        return removed_rules

    async def list_rules(
        self, session_id: str, active_only: bool = True, include_expired: bool = False
    ) -> List[PromptRule]:
        """
        List prompt rules for a session.

        Args:
            session_id: Session identifier
            active_only: Only return active rules
            include_expired: Include expired rules

        Returns:
            List of prompt rules
        """
        if active_only and not include_expired:
            return await self.storage.get_active_rules(session_id)

        session = await self.storage.load_session(session_id)

        # Get all rules from both personal and template packs
        all_rules = []
        all_rules.extend(session.personal_rules.values())

        # Add template pack rules (only from enabled packs)
        for pack in session.template_packs.values():
            if pack.enabled:
                all_rules.extend(pack.rules.values())

        if active_only:
            all_rules = [r for r in all_rules if r.active]

        if not include_expired:
            now = datetime.now()
            all_rules = [r for r in all_rules if not r.expires_at or r.expires_at > now]

        # Sort by priority and creation date
        all_rules.sort(key=lambda r: (-r.priority, r.created_at))

        return all_rules

    async def format_rules_for_prompt(self, session_id: str) -> Optional[str]:
        """
        Format active prompt rules for injection into LLM prompts.

        Args:
            session_id: Session identifier

        Returns:
            Formatted rules content or None if no active rules
        """
        active_rules = await self.storage.get_active_rules(session_id)

        if not active_rules:
            return None

        # Group by category
        categories = {}
        for rule in active_rules:
            if rule.category not in categories:
                categories[rule.category] = []
            categories[rule.category].append(rule)

        # Format rules
        sections = []
        for category, rules in categories.items():
            if category != "general":
                sections.append(f"## {category.upper()} RULES")

            for rule in rules:
                prefix = f"[PRIORITY {rule.priority}]" if rule.priority > 1 else ""
                expiry = ""
                if rule.expires_at:
                    expiry = f" (expires {rule.expires_at.strftime('%Y-%m-%d %H:%M')})"

                sections.append(f"{prefix} {rule.content}{expiry}")

        return "\n".join(sections)

    async def clear_expired_rules(self, session_id: str) -> List[PromptRule]:
        """
        Remove expired rules from a session.

        Args:
            session_id: Session identifier

        Returns:
            List of removed rules
        """
        return await self.storage.cleanup_expired_rules(session_id)

    async def clear_all_rules(self, session_id: str) -> List[PromptRule]:
        """
        Remove all rules from a session (destructive operation).

        Args:
            session_id: Session identifier

        Returns:
            List of removed rules
        """
        session = await self.storage.load_session(session_id)

        # Get all rules from both personal and template packs
        all_rules = []
        all_rules.extend(session.personal_rules.values())

        # Add template pack rules
        for pack in session.template_packs.values():
            all_rules.extend(pack.rules.values())

        # Clear everything
        session.personal_rules.clear()
        session.template_packs.clear()

        if all_rules:
            await self.storage.save_session(session)
            logger.info(f"Cleared all {len(all_rules)} rules from session {session_id}")

        return all_rules
