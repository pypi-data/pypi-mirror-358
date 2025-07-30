"""
Core guard processing logic for CodeGuard CLI.
COMPLETE REWRITE with guard stack system - exact port of VSCode processor.ts
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from ..error_handling import get_logger, handle_scope_resolution_error
from ..language.config import get_language_for_file_path
from ..parsing.comment_detector import get_comment_prefixes, is_line_a_comment
from ..parsing.tree_sitter_parser import find_node_at_position, parse_document
from ..scope.resolver import resolve_semantic_scope_sync
from ..types import (
    DEFAULT_PERMISSIONS,
    GuardStackEntry,
    GuardTag,
    ICoreConfiguration,
    IDocument,
    PermissionRange,
)
from ..validation.guard_stack_manager import (
    create_guard_stack_entry,
    pop_guard_with_context_cleanup,
)
from ..validation.guard_tag_parser import extract_guard_tag_matches, parse_guard_tag

logger = logging.getLogger(__name__)


class Document:
    """Document implementation for CLI"""

    def __init__(self, lines: List[str], languageId: str, lineCount: int, text: str):
        self.lines = lines
        self.languageId = languageId
        self.lineCount = lineCount
        self.text = text

    def getText(self) -> str:
        return self.text

    def lineAt(self, line: int) -> Dict[str, Any]:
        """Get line information (0-based for internal use)"""
        if 0 <= line < len(self.lines):
            text = self.lines[line]
            return {
                "text": text,
                "firstNonWhitespaceCharacterIndex": len(text) - len(text.lstrip()),
                "lineNumber": line,
            }
        return {"text": "", "firstNonWhitespaceCharacterIndex": 0, "lineNumber": line}


class CoreConfiguration:
    """Core configuration for processing."""

    def __init__(self, enableDebugLogging: bool = False):
        self.enableDebugLogging = enableDebugLogging

    def get(self, key: str, defaultValue: Any) -> Any:
        return getattr(self, key, defaultValue)


def get_default_scope(tag_info) -> Optional[str]:
    """
    Determine the default scope for a guard tag based on its properties.
    Exact port of VSCode function.
    """
    # If there's a line count, don't set a default scope
    if tag_info.lineCount:
        return None

    # Check if this is a context permission
    is_context_permission = (
        tag_info.aiIsContext
        or tag_info.humanIsContext
        or tag_info.aiPermission == "contextWrite"
        or tag_info.humanPermission == "contextWrite"
    )

    if is_context_permission:
        return "context"

    # Default to block scope for other permissions
    return "block"


def get_default_permissions() -> Dict[str, str]:
    """Get default permissions."""
    return DEFAULT_PERMISSIONS.copy()


class LineContext:
    """Unified access to both text and tree-sitter info for a line."""

    def __init__(
        self, line_number: int, text: str, node_type: str = None, language_id: str = "plaintext"
    ):
        self.line_number = line_number  # 1-based
        self.text = text
        self.node_type = node_type or "unknown"
        self.language_id = language_id

    @property
    def is_comment(self) -> bool:
        return self.node_type in ["comment", "line_comment", "block_comment"]

    @property
    def is_scope_breaking(self) -> bool:
        return self.node_type in [
            "program",
            "module",
            "class_declaration",
            "function_declaration",
            "method_definition",
        ]

    @property
    def is_empty(self) -> bool:
        return self.text.strip() == ""

    @property
    def has_guard_tag(self) -> bool:
        """Check if line has valid guard tags using language-aware comment anchoring."""
        valid_guards = find_guard_tags_in_line(self.text, self.language_id)
        return len(valid_guards) > 0


async def create_line_context_map(parse_result) -> Dict[int, LineContext]:
    """
    Create a map of line numbers to unified line context (text + tree-sitter info).
    Uses progressive parsing strategy to handle corrupted/incomplete files gracefully.
    """
    line_map = {}
    total_lines = len(lines)

    # Track which lines have been successfully parsed with tree-sitter
    parsed_regions = []  # List of (start_line, end_line, parse_result) tuples

    # Progressive parsing with binary search optimization for large files
    current_line = 0
    while current_line < total_lines:
        # Add periodic yield for responsiveness during CPU-intensive parsing
        await asyncio.sleep(0)
        best_parse_result = None
        best_end_line = current_line

        # Binary search to find the largest parseable block from current_line
        async def try_parse_range(start: int, end: int) -> Optional[Any]:
            """Try parsing from start to end line. Returns parse_result or None."""
            if start >= end or start >= total_lines:
                return None
            try:
                partial_lines = lines[start:end]
                partial_text = "\n".join(partial_lines)
                if partial_text.strip():  # Only try parsing non-empty content
                    # Add yield before CPU-intensive tree-sitter parsing
                    await asyncio.sleep(0)
                    parse_result = parse_document(partial_text, document.languageId)
                    if parse_result and parse_result.success and parse_result.root_node:
                        return parse_result
            except Exception:
                pass
            return None

        # First, try parsing from current_line to EOF
        full_parse = await try_parse_range(current_line, total_lines)
        if full_parse:
            # Entire rest of file parses successfully
            best_parse_result = full_parse
            best_end_line = total_lines
        else:
            # Binary search to find largest parseable block
            left = current_line + 1  # Minimum end position (at least 1 line)
            right = total_lines  # Maximum end position (EOF)

            while left <= right:
                mid = (left + right) // 2
                parse_result = await try_parse_range(current_line, mid)

                if parse_result:
                    # Parse succeeded up to mid, try for larger block
                    best_parse_result = parse_result
                    best_end_line = mid
                    left = mid + 1  # Search for even larger valid block
                else:
                    # Parse failed, try smaller block
                    right = mid - 1

        if best_parse_result and best_end_line > current_line:
            # Successfully found a parseable region
            parsed_regions.append((current_line, best_end_line, best_parse_result))
            current_line = best_end_line
        else:
            # Couldn't parse anything from this line, mark as unknown and move forward
            current_line += 1

    # Now create LineContext for each line using the parsed regions
    for i, line in enumerate(lines):
        line_number = i + 1  # Convert to 1-based
        node_type = "unknown"

        # Find which parsed region (if any) contains this line
        for start_line, end_line, parse_result in parsed_regions:
            if start_line <= i < end_line:
                # This line is covered by a valid parse region
                try:
                    # Calculate position within the parsed region
                    relative_line = (i - start_line) + 1  # 1-based within the region
                    node = find_node_at_position(parse_result.root_node, relative_line, 0)
                    if node:
                        node_type = node.type
                except Exception:
                    pass  # Keep "unknown"
                break

        # Fallback: detect comments using text-based detection if tree-sitter didn't work
        if node_type == "unknown" and is_line_a_comment(line, document.languageId):
            node_type = "comment"

        line_map[line_number] = LineContext(line_number, line, node_type, document.languageId)

    return line_map


async def parse_guard_tags_core(
    parse_result,
    config: ICoreConfiguration,
    extension_context: Any = None,
) -> List[GuardTag]:
    """
    semantic scope resolution for guard tag parsing for a document.
    """

    guard_tags = []
    lines = parse_result.content.split("\n") if hasattr(parse_result, "content") else []
    total_lines = len(lines)

    # Create unified line context map with tree-sitter info parsed once upfront
    line_contexts = await create_line_context_map(parse_result)

    # Parse each line for guard tags
    for i in range(total_lines):
        # Add periodic yield for responsiveness during CPU-intensive parsing
        if i % 100 == 0:  # Yield every 100 lines to avoid blocking
            await asyncio.sleep(0)

        line_number = i + 1  # Convert to 1-based indexing
        line_context = line_contexts[line_number]
        line = line_context.text

        try:
            # Only parse lines that have properly anchored guard tags
            valid_guards = find_guard_tags_in_line(line, document.languageId)
            if not valid_guards:
                continue

            # Process each valid guard tag on this line
            for start_pos, end_pos in valid_guards:
                guard_text = line[start_pos:end_pos]
                tag_info = parse_guard_tag(guard_text)

                if tag_info:
                    # Create guard tag with core processing
                    guard_tag = GuardTag(
                        lineNumber=line_number,
                        identifier=tag_info.identifier,
                        scope=tag_info.scope or get_default_scope(tag_info),
                        lineCount=tag_info.lineCount,
                        addScopes=tag_info.addScopes,
                        removeScopes=tag_info.removeScopes,
                        aiPermission=tag_info.aiPermission,
                        humanPermission=tag_info.humanPermission,
                        aiIsContext=tag_info.aiIsContext,
                        humanIsContext=tag_info.humanIsContext,
                    )

                    # Set scope boundaries - simplified logic for now
                    if guard_tag.lineCount:
                        # Line count based scope
                        guard_tag.scopeStart = line_number
                        guard_tag.scopeEnd = min(line_number + guard_tag.lineCount - 1, total_lines)
                    elif guard_tag.scope == "context":
                        # Context scope - greedy forward scan with backward trimming
                        guard_tag.scopeStart = line_number + 1

                        # Step 1: Forward scan - continue greedily until EOF, next identifier, or next guard tag
                        forward_end_line = total_lines  # Default to EOF
                        skip_backward_trim = (
                            False  # Flag to skip backward trimming for definitive boundaries
                        )

                        for search_line_num in range(line_number + 1, total_lines):
                            search_line_context = line_contexts.get(
                                search_line_num + 1
                            )  # +1 for 1-based
                            if not search_line_context:
                                break

                            # Stop at next guard tag
                            if search_line_context.has_guard_tag:
                                forward_end_line = search_line_num  # Stop before the guard tag
                                break

                            # Stop at string_end when in text block (simplified rule)
                            if search_line_context.node_type == "string_end":
                                forward_end_line = (
                                    search_line_num + 1
                                )  # Include the string_end line (convert 0-based to 1-based)
                                skip_backward_trim = True  # String end is definitive boundary
                                break

                        # Step 2: Backward walk from stopping point (skip if we hit a definitive boundary)
                        actual_end_line = forward_end_line
                        if not skip_backward_trim:
                            # Walk backwards through non-whitespace lines until finding blank line or reaching guard tag line
                            for back_line_num in range(
                                forward_end_line, line_number, -1
                            ):  # Walk backwards (1-based line numbers)
                                back_line_context = line_contexts.get(
                                    back_line_num
                                )  # back_line_num is already 1-based
                                if not back_line_context:
                                    continue

                                if back_line_context.is_empty:
                                    # Found blank line - the actual end is the line before this blank line
                                    actual_end_line = back_line_num - 1
                                    break
                                # Continue walking back through non-whitespace lines

                        # Step 3: Continue walking back through whitespace-only lines (skip if definitive boundary)
                        if not skip_backward_trim:
                            for ws_line_num in range(
                                actual_end_line, line_number, -1
                            ):  # Walk backwards from blank line (1-based line numbers)
                                ws_line_context = line_contexts.get(
                                    ws_line_num
                                )  # ws_line_num is already 1-based
                                if not ws_line_context:
                                    continue

                                # Check if line has only whitespace characters
                                if ws_line_context.text.strip() == "":
                                    # Pure whitespace line, continue walking back
                                    continue
                                else:
                                    # Found first line with visible characters, this is our end
                                    actual_end_line = ws_line_num
                                    break

                        guard_tag.scopeEnd = actual_end_line
                    elif guard_tag.scope == "block":
                        # Block scope - apply to next code block using tree-sitter logic like VSCode
                        start_line_number = line_number + 1  # Start from line after guard (1-based)
                        end_line_number = start_line_number

                        # Scan forward to find the end of the statement block using unified line contexts
                        for current_line_num in range(
                            start_line_number - 1, total_lines
                        ):  # 0-based iteration
                            current_line_context = line_contexts.get(
                                current_line_num + 1
                            )  # +1 for 1-based lookup
                            if not current_line_context:
                                break

                            # Stop at guard tags
                            if current_line_context.has_guard_tag:
                                break

                            # Use tree-sitter info to check if we hit a scope-breaking node type
                            if current_line_context.is_scope_breaking:
                                # Hit program/module/class/function scope, stop here
                                break

                            # Include this line in the block
                            end_line_number = current_line_num + 1  # Convert to 1-based

                        guard_tag.scopeStart = start_line_number
                        guard_tag.scopeEnd = max(end_line_number, line_number)
                    else:
                        # For other scopes (class, func, function, signature), use semantic scope resolution
                        if guard_tag.scope in ["class", "func", "function", "signature"]:
                            try:
                                # Use direct synchronous scope resolution to avoid async complexity
                                scope_boundary = resolve_semantic_scope_sync(
                                    document,
                                    line_number - 1,
                                    guard_tag.scope,  # Convert to 0-based for tree-sitter
                                )

                                if scope_boundary:
                                    guard_tag.scopeStart = scope_boundary.startLine
                                    guard_tag.scopeEnd = scope_boundary.endLine
                                else:
                                    # Fallback to single line if semantic resolution fails
                                    guard_tag.scopeStart = line_number
                                    guard_tag.scopeEnd = line_number

                            except Exception as e:
                                handle_scope_resolution_error(
                                    f"Error in semantic scope resolution for {guard_tag.scope} at line {line_number}",
                                    scope_type=guard_tag.scope,
                                    line_number=line_number,
                                    cause=e,
                                )
                                # Fallback to single line if semantic resolution fails
                                guard_tag.scopeStart = line_number
                                guard_tag.scopeEnd = line_number
                        else:
                            # For unrecognized scopes, fallback to single line
                            guard_tag.scopeStart = line_number
                            guard_tag.scopeEnd = line_number

                    guard_tags.append(guard_tag)

        except Exception as e:
            logger.debug(f"Error parsing guard tag at line {line_number}: {e}")

    return guard_tags


def get_permission_ranges_core(
    document: IDocument,
    guard_tags: List[GuardTag],
    config: ICoreConfiguration,
) -> List[PermissionRange]:
    """
    Get permission ranges for a document - optimized version using range-based processing
    """

    ranges: List[PermissionRange] = []
    guard_stack: List[GuardStackEntry] = []
    total_lines = document.lineCount

    # Initialize with default permissions
    default_perms = get_default_permissions()

    # Process each line to build ranges
    current_range = None

    for line_number in range(1, total_lines + 1):
        # Check if any guards end at this line
        while guard_stack and guard_stack[-1].endLine < line_number:
            pop_guard_with_context_cleanup(guard_stack)

        # Check if any guards start at this line
        guards_at_line = [tag for tag in guard_tags if tag.lineNumber == line_number]

        for guard in guards_at_line:
            if guard.scopeStart is not None and guard.scopeEnd is not None:
                # Create permissions object
                permissions: Dict[str, str] = {}
                is_context: Dict[str, bool] = {}

                # Set AI permissions
                if guard.aiPermission:
                    permissions["ai"] = guard.aiPermission
                    is_context["ai"] = guard.aiPermission == "contextWrite" or bool(
                        guard.aiIsContext
                    )
                elif guard.aiIsContext:
                    permissions["ai"] = "r"
                    is_context["ai"] = True

                # Set human permissions
                if guard.humanPermission:
                    permissions["human"] = guard.humanPermission
                    is_context["human"] = guard.humanPermission == "contextWrite" or bool(
                        guard.humanIsContext
                    )
                elif guard.humanIsContext:
                    permissions["human"] = "r"
                    is_context["human"] = True

                # Create range directly instead of processing line by line
                new_range = PermissionRange(
                    start_line=guard.scopeStart,
                    end_line=guard.scopeEnd,
                    permissions=permissions,
                    isContext=is_context,
                    identifier=guard.identifier,
                )

                # Check if we can extend existing range or need new one
                if ranges and ranges[-1].can_extend(
                    guard.scopeStart, permissions, is_context, guard.identifier
                ):
                    ranges[-1].extend_to(guard.scopeEnd)
                else:
                    ranges.append(new_range)

    return ranges


async def process_document(
    content: str,
    language_id: str,
    parse_result,
    config: CoreConfiguration = None,
    extension_context: Any = None,
) -> Tuple[List[GuardTag], List[PermissionRange]]:
    """
    Process a complete document and return guard tags and permission ranges.
    """
    if config is None:
        config = CoreConfiguration()

    lines = content.split("\n")
    document = Document(lines=lines, languageId=language_id, lineCount=len(lines), text=content)

    # Parse guard tags
    guard_tags = await parse_guard_tags_core(parse_result, config, extension_context)

    # Get permission ranges using optimized range-based system
    permission_ranges = get_permission_ranges_core(document, guard_tags, config)

    return guard_tags, permission_ranges


def detect_language(file_path: str) -> str:
    """
    Detect programming language from file extension.
    """
    language = get_language_for_file_path(file_path)
    return language if language != "unknown" else "plaintext"


def clean_node_type_for_display(node_type: str) -> str:
    """
    Clean up node type names for display.
    Port of the VSCode plugin's node type cleaning logic.
    """
    # Clean up node type names for display
    if node_type.endswith("_declaration"):
        node_type = node_type.replace("_declaration", "")
    if node_type.endswith("_definition"):
        node_type = node_type.replace("_definition", "")
    if node_type.endswith("_expression"):
        node_type = node_type.replace("_expression", "")
    if node_type.endswith("_operator"):
        node_type = node_type.replace("_operator", "")
    if node_type.endswith("_statement"):
        node_type = node_type.replace("_statement", "")
    if node_type == "statement_block":
        node_type = "statement"
    if node_type == "class_body":
        node_type = "body"
    if node_type.startswith("import_"):
        node_type = "import"

    return node_type


def get_node_type_for_line_display(content: str, language_id: str, line_number: int) -> str:
    """
    Get the semantic node type for a specific line for display purposes only.
    """
    from ..parsing.tree_sitter_parser import get_node_type_for_line, is_tree_sitter_available

    if not is_tree_sitter_available():
        return "unknown"

    try:
        node_type = get_node_type_for_line(content, language_id, line_number)
        return clean_node_type_for_display(node_type)
    except Exception:
        return "error"


def find_guard_tags_in_line(line: str, language_id: str = "plaintext") -> list:
    """
    Find valid guard tags in a line that are properly comment-anchored.

    Args:
        line: Text content of the line
        language_id: Programming language identifier

    Returns:
        List of guard tag matches that are properly anchored to comments
    """
    # Get all potential guard tag matches
    guard_matches = extract_guard_tag_matches(line)

    if not guard_matches:
        return []

    # Check if this line is a comment using existing comment detector
    if not is_line_a_comment(line, language_id):
        return []  # Not a comment line, no valid guards

    # Get comment prefixes for this language
    comment_prefixes = get_comment_prefixes(language_id)

    # Find where the comment syntax ends so we can validate guard positioning
    stripped_line = line.lstrip()  # Remove leading whitespace
    comment_end_pos = 0

    for prefix in comment_prefixes:
        if stripped_line.startswith(prefix):
            # Found the comment prefix, calculate where it ends in the original line
            leading_whitespace = len(line) - len(stripped_line)
            comment_end_pos = leading_whitespace + len(prefix)
            break

    valid_guards = []

    for start_pos, end_pos in guard_matches:
        # Check if this guard starts right after the comment syntax (allowing whitespace)
        text_between_comment_and_guard = line[comment_end_pos:start_pos].strip()

        if not text_between_comment_and_guard:
            # Guard comes right after comment syntax (possibly with whitespace) - this is valid
            valid_guards.append((start_pos, end_pos))
        elif valid_guards:
            # If we already have valid guards, subsequent guards can follow them
            # Check if there's only whitespace between the last valid guard and this one
            last_guard_end = valid_guards[-1][1]
            text_between_guards = line[last_guard_end:start_pos].strip()

            if not text_between_guards:
                valid_guards.append((start_pos, end_pos))
            # If there's other text between guards, this guard is invalid (per spec)

    return valid_guards


# Async functionality for streaming operations


async def process_document_generator(content: str, language_id: str = "text"):
    """
    Async version of process_document for streaming operations.

    Args:
        content: Document content to process
        language_id: Language identifier

    Returns:
        Tuple of (guard_tags, line_permissions) - same as sync version
    """
    # For now, just call the sync version since document processing is CPU-bound
    # In a full implementation, you might want to use asyncio.to_thread for CPU-intensive work
    return process_document(content, language_id)
