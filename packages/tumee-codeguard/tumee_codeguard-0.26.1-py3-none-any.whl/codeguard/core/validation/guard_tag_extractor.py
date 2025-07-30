"""
Shared guard tag extraction functionality for CodeGuard.

This module provides a simple interface for extracting guard tags from file content
that can be used by both fs_walker and validate_directory without duplication.
"""

import asyncio
from typing import List, Tuple

from ..infrastructure.processor import CoreConfiguration, detect_language, process_document
from ..types import GuardTag


async def extract_guard_tags_from_content(content: str, file_path: str) -> List[GuardTag]:
    """
    Extract guard tags from file content.

    Args:
        content: File content as string
        file_path: Path to the file (used for language detection)

    Returns:
        List of GuardTag objects found in the content
    """
    # Detect language from file extension
    language_id = detect_language(file_path)

    # Add periodic yield for responsiveness during CPU-intensive parsing
    await asyncio.sleep(0)

    # Use the existing process_document function to parse guard tags
    guard_tags, _ = await process_document(content, language_id, CoreConfiguration())

    return guard_tags


async def extract_guard_tags_with_target_filter(
    content: str, file_path: str, target: str = "*"
) -> List[GuardTag]:
    """
    Extract guard tags from file content with target filtering.

    Args:
        content: File content as string
        file_path: Path to the file (used for language detection)
        target: Target filter ("ai", "human", "*" for all)

    Returns:
        List of GuardTag objects matching the target filter
    """
    all_tags = await extract_guard_tags_from_content(content, file_path)

    if target == "*":
        return all_tags

    # Filter by target
    filtered_tags = []
    for tag in all_tags:
        if target == "ai" and (tag.aiPermission or tag.aiIsContext):
            filtered_tags.append(tag)
        elif target == "human" and (tag.humanPermission or tag.humanIsContext):
            filtered_tags.append(tag)

    return filtered_tags
