"""
Core data structures for prompt injection system.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


class RuleType(Enum):
    """Type of prompt rule."""

    PERSONAL = "personal"
    TEMPLATE = "template"


@dataclass
class PromptRule:
    """
    A high-priority rule that gets injected into LLM prompts.

    Prompt rules are date-based temporary or permanent instructions
    that take precedence over other prompts (priority 2).
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    category: str = "general"  # general, security, setup, process
    priority: int = 1  # 1-5, higher = more important
    created_at: datetime = field(default_factory=datetime.now)

    # Date-only expiration (simplified from count-based)
    expires_at: Optional[datetime] = None  # When rule expires

    # Template pack support
    rule_type: RuleType = RuleType.PERSONAL
    pack_id: Optional[str] = None  # Template pack this rule belongs to

    # State
    active: bool = True


@dataclass
class TemplatePack:
    """
    A collection of related prompt rules that can be managed as a unit.

    Template packs allow organizing rules by project, team, or purpose
    and can be shared via import/export.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0"
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    # Rules contained in this pack
    rules: Dict[str, PromptRule] = field(default_factory=dict)

    # Pack state
    enabled: bool = True

    def to_export_format(self) -> Dict:
        """Convert pack to exportable JSON format."""
        return {
            "pack_meta": {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "author": self.author,
                "created_at": self.created_at.isoformat(),
            },
            "rules": [
                {
                    "content": rule.content,
                    "category": rule.category,
                    "priority": rule.priority,
                    "expires_in_hours": (
                        None
                        if not rule.expires_at
                        else int((rule.expires_at - datetime.now()).total_seconds() / 3600)
                    ),
                }
                for rule in self.rules.values()
            ],
        }

    @classmethod
    def from_import_format(
        cls, data: Dict, author_override: Optional[str] = None
    ) -> "TemplatePack":
        """Create pack from imported JSON format."""
        meta = data["pack_meta"]

        pack = cls(
            name=meta["name"],
            description=meta.get("description", ""),
            version=meta.get("version", "1.0"),
            author=author_override or meta.get("author", ""),
        )

        # Create rules from import data
        for rule_data in data.get("rules", []):
            expires_at = None
            if rule_data.get("expires_in_hours"):
                expires_at = datetime.now() + timedelta(hours=rule_data["expires_in_hours"])

            rule = PromptRule(
                content=rule_data["content"],
                category=rule_data.get("category", "general"),
                priority=rule_data.get("priority", 1),
                expires_at=expires_at,
                rule_type=RuleType.TEMPLATE,
                pack_id=pack.id,
            )
            pack.rules[rule.id] = rule

        return pack


@dataclass
class PromptInjectSession:
    """
    Container for prompt injection rules and template packs in a session.

    Separate from planning sessions to keep features independent.
    Now supports both personal rules and template packs.
    """

    session_id: str
    created_at: datetime = field(default_factory=datetime.now)

    # Separated storage for clean pack management
    personal_rules: Dict[str, PromptRule] = field(default_factory=dict)
    template_packs: Dict[str, TemplatePack] = field(default_factory=dict)

    last_cleanup: datetime = field(default_factory=datetime.now)

    def get_all_active_rules(self) -> List[PromptRule]:
        """Get all active rules from both personal and template packs."""
        all_rules = []

        # Add personal rules
        now = datetime.now()
        for rule in self.personal_rules.values():
            if rule.active and (not rule.expires_at or rule.expires_at > now):
                all_rules.append(rule)

        # Add template pack rules (only from enabled packs)
        for pack in self.template_packs.values():
            if pack.enabled:
                for rule in pack.rules.values():
                    if rule.active and (not rule.expires_at or rule.expires_at > now):
                        all_rules.append(rule)

        # Sort by priority (highest first) then by creation time
        all_rules.sort(key=lambda r: (-r.priority, r.created_at))
        return all_rules
