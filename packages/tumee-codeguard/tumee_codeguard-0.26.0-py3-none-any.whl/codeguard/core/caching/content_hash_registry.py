"""
Content Hash Registry for CodeGuard.

This module tracks content hashes across files to detect content movement
and prevent false positives when guarded content moves between files.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ...utils.hash_calculator import HashCalculator
from ..validation.guard_tag_parser import GuardTag


@dataclass
class ContentHashEntry:
    """Entry in the content hash registry."""

    content_hash: str
    file_path: str
    guard_tag: GuardTag
    start_line: int
    end_line: int
    content: str
    identifier: str = None


class ContentHashRegistry:
    """
    Registry for tracking content hashes across files to detect movement.

    This class maintains a registry of content hashes for all guarded regions
    to detect when content moves between files vs when it's actually modified.
    """

    def __init__(self, hash_calculator: HashCalculator = None):
        """Initialize the content hash registry."""
        self.hash_calculator = hash_calculator or HashCalculator()

        # Registry of content hashes: hash -> list of entries
        self._hash_registry: Dict[str, List[ContentHashEntry]] = {}

        # File tracking: file_path -> set of hashes in that file
        self._file_hashes: Dict[str, Set[str]] = {}

        # Identifier tracking: identifier -> list of hashes
        self._identifier_hashes: Dict[str, List[str]] = {}

    def register_guard_content(
        self, file_path: str, guard_tag: GuardTag, content: str, start_line: int, end_line: int
    ) -> str:
        """
        Register guard content in the hash registry.

        Args:
            file_path: Path to the file containing the guard
            guard_tag: The guard tag object
            content: The content protected by the guard
            start_line: Start line of the guarded content
            end_line: End line of the guarded content

        Returns:
            The calculated content hash
        """
        # Calculate semantic content hash
        content_hash = self.hash_calculator.calculate_semantic_content_hash(
            content=content, identifier=guard_tag.identifier
        )

        # Create registry entry
        entry = ContentHashEntry(
            content_hash=content_hash,
            file_path=file_path,
            guard_tag=guard_tag,
            start_line=start_line,
            end_line=end_line,
            content=content,
            identifier=guard_tag.identifier,
        )

        # Add to hash registry
        if content_hash not in self._hash_registry:
            self._hash_registry[content_hash] = []
        self._hash_registry[content_hash].append(entry)

        # Track file hashes
        if file_path not in self._file_hashes:
            self._file_hashes[file_path] = set()
        self._file_hashes[file_path].add(content_hash)

        # Track identifier hashes
        if guard_tag.identifier:
            if guard_tag.identifier not in self._identifier_hashes:
                self._identifier_hashes[guard_tag.identifier] = []
            self._identifier_hashes[guard_tag.identifier].append(content_hash)

        return content_hash

    def check_content_movement(
        self, original_hash: str, modified_hash: str, current_file: str
    ) -> Tuple[bool, Optional[str], Optional[ContentHashEntry]]:
        """
        Check if content has moved vs been modified.

        Args:
            original_hash: Hash of original content
            modified_hash: Hash of modified content
            current_file: Current file being validated

        Returns:
            Tuple of (is_movement, source_file, source_entry)
            - is_movement: True if this is content movement, not modification
            - source_file: File path where the content was found (if movement)
            - source_entry: Original registry entry (if movement)
        """
        # If hashes are the same, no change occurred
        if original_hash == modified_hash:
            return False, None, None

        # Check if the modified hash exists in a different file
        if modified_hash in self._hash_registry:
            entries = self._hash_registry[modified_hash]

            # Look for entries from different files
            for entry in entries:
                if entry.file_path != current_file:
                    return True, entry.file_path, entry

        return False, None, None

    def get_content_locations(self, content_hash: str) -> List[ContentHashEntry]:
        """
        Get all locations where specific content appears.

        Args:
            content_hash: Hash of the content to find

        Returns:
            List of entries where this content appears
        """
        return self._hash_registry.get(content_hash, [])

    def get_file_hashes(self, file_path: str) -> Set[str]:
        """
        Get all content hashes for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            Set of content hashes in the file
        """
        return self._file_hashes.get(file_path, set())

    def get_identifier_hashes(self, identifier: str) -> List[str]:
        """
        Get all content hashes for a specific guard identifier.

        Args:
            identifier: Guard identifier

        Returns:
            List of content hashes for this identifier
        """
        return self._identifier_hashes.get(identifier, [])

    def clear_file_hashes(self, file_path: str):
        """
        Clear all hash registry entries for a specific file.

        This should be called when reprocessing a file to avoid stale entries.

        Args:
            file_path: Path to the file to clear
        """
        if file_path not in self._file_hashes:
            return

        # Get hashes for this file
        file_hashes = self._file_hashes[file_path].copy()

        # Remove entries from hash registry
        for content_hash in file_hashes:
            if content_hash in self._hash_registry:
                # Remove entries matching this file
                self._hash_registry[content_hash] = [
                    entry
                    for entry in self._hash_registry[content_hash]
                    if entry.file_path != file_path
                ]

                # If no entries left, remove the hash entirely
                if not self._hash_registry[content_hash]:
                    del self._hash_registry[content_hash]

        # Clear file tracking
        del self._file_hashes[file_path]

        # Clean up identifier tracking
        for identifier, hashes in list(self._identifier_hashes.items()):
            self._identifier_hashes[identifier] = [h for h in hashes if h not in file_hashes]
            if not self._identifier_hashes[identifier]:
                del self._identifier_hashes[identifier]

    def has_hash(self, content_hash: str) -> bool:
        """
        Check if a content hash exists in the registry.

        Args:
            content_hash: Hash to check

        Returns:
            True if hash exists in registry
        """
        return content_hash in self._hash_registry

    def get_registry_stats(self) -> Dict:
        """
        Get statistics about the hash registry.

        Returns:
            Dictionary with registry statistics
        """
        return {
            "total_hashes": len(self._hash_registry),
            "total_files": len(self._file_hashes),
            "total_identifiers": len(self._identifier_hashes),
            "average_entries_per_hash": (
                sum(len(entries) for entries in self._hash_registry.values())
                / len(self._hash_registry)
                if self._hash_registry
                else 0
            ),
        }
