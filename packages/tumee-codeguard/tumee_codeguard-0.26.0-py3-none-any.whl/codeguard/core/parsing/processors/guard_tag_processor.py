"""
Guard Tag Processor for Unified Parser.

Extracts guard tags during unified document parsing.
"""

import logging
from typing import Any, List, Literal, Optional, cast

from ...infrastructure.processor import CoreConfiguration
from ...types import GuardTag, PermissionRange
from ...validation.guard_tag_parser import extract_guard_tag_matches, parse_guard_tag
from ..unified_types import UnifiedParseResult

logger = logging.getLogger(__name__)


class GuardTagProcessor:
    """Processor that extracts guard tags during unified parsing."""

    def __init__(self, config: Optional[CoreConfiguration] = None):
        self.config = config or CoreConfiguration()
        self.guard_tags = []

    async def process_line(
        self,
        line_num: int,
        line_text: str,
        node_context: Optional[Any],
        unified_result: UnifiedParseResult,
    ) -> None:
        """Process a single line for guard tags."""
        # Check if line has guard tags
        guard_matches = extract_guard_tag_matches(line_text)
        if not guard_matches:
            return

        # Mark line context as having guard tags
        if line_num in unified_result.line_contexts:
            unified_result.line_contexts[line_num].has_guard_tag = True

        # Process each guard tag on this line
        for start_pos, end_pos in guard_matches:
            guard_text = line_text[start_pos:end_pos]
            tag_info = parse_guard_tag(guard_text)

            if tag_info:
                # Create guard tag
                guard_tag = GuardTag(
                    lineNumber=line_num,
                    identifier=tag_info.identifier,
                    scope=tag_info.scope or self._get_default_scope(tag_info),
                    lineCount=tag_info.lineCount,
                    addScopes=tag_info.addScopes,
                    removeScopes=tag_info.removeScopes,
                    aiPermission=(
                        cast(
                            Optional[Literal["r", "w", "n", "contextWrite"]], tag_info.aiPermission
                        )
                        if tag_info.aiPermission in ["r", "w", "n", "contextWrite"]
                        else None
                    ),
                    humanPermission=(
                        cast(
                            Optional[Literal["r", "w", "n", "contextWrite"]],
                            tag_info.humanPermission,
                        )
                        if tag_info.humanPermission in ["r", "w", "n", "contextWrite"]
                        else None
                    ),
                    aiIsContext=tag_info.aiIsContext,
                    humanIsContext=tag_info.humanIsContext,
                )

                self.guard_tags.append(guard_tag)

    async def finalize(self, unified_result: UnifiedParseResult) -> None:
        """Finalize guard tag processing - calculate scope boundaries."""
        # Set scope boundaries for all guard tags
        total_lines = unified_result.line_count

        for guard_tag in self.guard_tags:
            if guard_tag.lineCount:
                # Line count based scope
                guard_tag.scopeStart = guard_tag.lineNumber
                guard_tag.scopeEnd = min(
                    guard_tag.lineNumber + guard_tag.lineCount - 1, total_lines
                )
            elif guard_tag.scope == "context":
                # Context scope - simplified implementation for now
                guard_tag.scopeStart = guard_tag.lineNumber + 1
                guard_tag.scopeEnd = self._find_context_end(guard_tag.lineNumber, unified_result)
            elif guard_tag.scope == "block":
                # Block scope - simplified implementation for now
                guard_tag.scopeStart = guard_tag.lineNumber + 1
                guard_tag.scopeEnd = self._find_block_end(guard_tag.lineNumber, unified_result)
            else:
                # Default to single line
                guard_tag.scopeStart = guard_tag.lineNumber
                guard_tag.scopeEnd = guard_tag.lineNumber

        # Store guard tags in unified result
        unified_result.guard_tags = self.guard_tags

        # Generate permission ranges (optimized for performance)
        unified_result.permission_ranges = self._generate_permission_ranges(unified_result)

    def _get_default_scope(self, tag_info) -> str:
        """Get default scope for a guard tag."""
        if tag_info.lineCount:
            return "line"
        return "context"

    def _find_context_end(self, guard_line: int, unified_result: UnifiedParseResult) -> int:
        """Find end of context scope using optimized range-based lookup."""
        total_lines = unified_result.line_count

        # Since guard tags are processed in order, find the next guard tag after this one
        next_guard_line = None
        for guard_tag in self.guard_tags:
            if guard_tag.lineNumber > guard_line:
                next_guard_line = guard_tag.lineNumber
                break

        # If found next guard tag, end before it; otherwise end at EOF
        return (next_guard_line - 1) if next_guard_line else total_lines

    def _find_block_end(self, guard_line: int, unified_result: UnifiedParseResult) -> int:
        """Find end of block scope (simplified implementation)."""
        # For now, treat block scope like context scope
        # TODO: Use tree-sitter AST to find actual block boundaries
        return self._find_context_end(guard_line, unified_result)

    def _generate_permission_ranges(
        self, _unified_result: UnifiedParseResult
    ) -> List[PermissionRange]:
        """Generate permission ranges from guard tags (optimized with range extension)."""
        ranges = []

        # Default permissions
        default_perms = {"ai": "r", "human": "w"}
        default_context = {"ai": False, "human": False}

        # Cache for permission combinations to avoid redundant dictionary copying
        permission_cache = {}

        # Apply guard tag permissions to their scope ranges
        for guard_tag in self.guard_tags:
            if guard_tag.scopeStart and guard_tag.scopeEnd:
                # Create cache key from guard tag permission values
                cache_key = f"{guard_tag.aiPermission}:{guard_tag.humanPermission}:{guard_tag.aiIsContext}:{guard_tag.humanIsContext}"

                if cache_key in permission_cache:
                    # Reuse cached dictionaries for this permission combination
                    permissions = permission_cache[cache_key]["permissions"]
                    is_context = permission_cache[cache_key]["context"]
                else:
                    # First time seeing this combination - create and cache
                    permissions = default_perms.copy()
                    is_context = default_context.copy()

                    # Apply guard tag permissions
                    if guard_tag.aiPermission:
                        permissions["ai"] = guard_tag.aiPermission
                    if guard_tag.humanPermission:
                        permissions["human"] = guard_tag.humanPermission
                    if guard_tag.aiIsContext:
                        is_context["ai"] = guard_tag.aiIsContext
                    if guard_tag.humanIsContext:
                        is_context["human"] = guard_tag.humanIsContext

                    # Cache this combination for reuse
                    permission_cache[cache_key] = {
                        "permissions": permissions,
                        "context": is_context,
                    }

                # Check if we can extend the last range instead of creating a new one
                if ranges and ranges[-1].can_extend(
                    guard_tag.scopeStart, permissions, is_context, guard_tag.identifier
                ):
                    # Extend existing range
                    ranges[-1].extend_to(guard_tag.scopeEnd)
                else:
                    # Create new range
                    ranges.append(
                        PermissionRange(
                            start_line=guard_tag.scopeStart,
                            end_line=guard_tag.scopeEnd,
                            permissions=permissions,
                            isContext=is_context,
                            identifier=guard_tag.identifier,
                        )
                    )

        return ranges
