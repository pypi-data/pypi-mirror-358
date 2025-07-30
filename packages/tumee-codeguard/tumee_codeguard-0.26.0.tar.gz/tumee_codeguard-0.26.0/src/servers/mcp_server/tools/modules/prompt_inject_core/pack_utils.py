"""
Template pack utilities for file operations and common tasks.

This module provides static helper methods for template pack management,
file I/O operations, and common utility functions.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from ......core.formatters import FormatterRegistry
from .core import TemplatePack

logger = logging.getLogger(__name__)


class PackFileManager:
    """Static utility class for template pack file operations."""

    @staticmethod
    def find_pack_file(pack_file: str) -> Optional[Path]:
        """
        Find a template pack file in standard locations.

        Args:
            pack_file: Name of the pack file to find

        Returns:
            Path to the file if found, None otherwise
        """
        search_paths = [
            Path.cwd() / pack_file,  # Current directory
            Path.cwd() / "packs" / pack_file,  # ./packs/ directory
            Path.home() / ".codeguard" / "packs" / pack_file,  # User packs directory
        ]

        for path in search_paths:
            if path.exists():
                logger.debug(f"Found pack file at: {path}")
                return path

        logger.debug(f"Pack file '{pack_file}' not found in: {[str(p) for p in search_paths]}")
        return None

    @staticmethod
    def load_pack_from_file(pack_path: Path) -> Dict:
        """
        Load and validate template pack from file using formatters.

        Args:
            pack_path: Path to the pack file

        Returns:
            Parsed pack data as dictionary

        Raises:
            ValueError: If file cannot be loaded or is invalid format
        """
        try:
            # Use the formatters system to load the file
            formatter = FormatterRegistry.get_formatter("json")
            pack_data = formatter.load(pack_path)

            # Validate pack format
            if not isinstance(pack_data, dict):
                raise ValueError("Pack file must contain a JSON object")

            if "pack_meta" not in pack_data:
                raise ValueError("Invalid pack format: missing 'pack_meta' section")

            if "rules" not in pack_data:
                raise ValueError("Invalid pack format: missing 'rules' section")

            logger.info(f"Successfully loaded pack from: {pack_path}")
            return pack_data

        except Exception as e:
            logger.error(f"Failed to load pack from {pack_path}: {e}")
            raise ValueError(f"Failed to load pack file: {str(e)}")

    @staticmethod
    def save_pack_to_file(pack: TemplatePack, pack_path: Path) -> None:
        """
        Save template pack to file using formatters.

        Args:
            pack: Template pack to save
            pack_path: Path where to save the file

        Raises:
            ValueError: If file cannot be saved
        """
        try:
            # Ensure directory exists
            pack_path.parent.mkdir(parents=True, exist_ok=True)

            # Use the formatters system to save the file
            formatter = FormatterRegistry.get_formatter("json")
            pack_data = pack.to_export_format()
            formatter.save(pack_data, pack_path)

            logger.info(f"Successfully saved pack '{pack.name}' to: {pack_path}")

        except Exception as e:
            logger.error(f"Failed to save pack to {pack_path}: {e}")
            raise ValueError(f"Failed to save pack file: {str(e)}")

    @staticmethod
    def get_export_path(pack_name: str, base_dir: Optional[Path] = None) -> Path:
        """
        Generate a suitable export path for a template pack.

        Args:
            pack_name: Name of the pack
            base_dir: Base directory for export (defaults to current directory)

        Returns:
            Path for the export file
        """
        if base_dir is None:
            base_dir = Path.cwd()

        # Sanitize pack name for filename
        safe_name = "".join(c for c in pack_name if c.isalnum() or c in "-_").lower()
        filename = f"{safe_name}.json"

        return base_dir / filename


class PackSessionManager:
    """Static utility class for template pack session operations."""

    @staticmethod
    def find_pack_by_name(session, pack_name: str) -> Tuple[Optional[TemplatePack], Optional[str]]:
        """
        Find a template pack by name in session.

        Args:
            session: PromptInjectSession instance
            pack_name: Name of the pack to find

        Returns:
            Tuple of (pack, pack_id) or (None, None) if not found
        """
        for pack_id, pack in session.template_packs.items():
            if pack.name == pack_name:
                return pack, pack_id
        return None, None

    @staticmethod
    def check_name_conflict(session, pack_name: str) -> bool:
        """
        Check if a pack name already exists in session.

        Args:
            session: PromptInjectSession instance
            pack_name: Name to check

        Returns:
            True if name conflicts, False otherwise
        """
        pack, _ = PackSessionManager.find_pack_by_name(session, pack_name)
        return pack is not None

    @staticmethod
    def get_pack_summary(pack: TemplatePack) -> Dict:
        """
        Generate a summary dictionary for a template pack.

        Args:
            pack: Template pack to summarize

        Returns:
            Summary dictionary with key pack information
        """
        active_rules = len([r for r in pack.rules.values() if r.active])

        return {
            "id": pack.id,
            "name": pack.name,
            "description": pack.description,
            "version": pack.version,
            "author": pack.author,
            "enabled": pack.enabled,
            "rule_count": len(pack.rules),
            "active_rules": active_rules,
            "created": pack.created_at.strftime("%Y-%m-%d %H:%M"),
        }
