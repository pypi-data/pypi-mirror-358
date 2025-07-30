"""
Core language-specific comment detection utilities - platform agnostic
EXACT port of VSCode src/core/commentDetector.ts
No dependencies allowed in this module
"""

from typing import Dict, List, Tuple


class LanguageCommentConfig:
    """Language configuration for comment patterns."""

    def __init__(
        self,
        line_comments: List[str],
        block_comment_start: List[str] = None,
        block_comment_continue: List[str] = None,
    ):
        self.line_comments = line_comments
        self.block_comment_start = block_comment_start or []
        self.block_comment_continue = block_comment_continue or []


# Map of language IDs to their comment configurations - EXACT port from VSCode
LANGUAGE_COMMENTS: Dict[str, LanguageCommentConfig] = {
    # C-style languages
    "javascript": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "typescript": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "javascriptreact": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "typescriptreact": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "java": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "c": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "cpp": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "csharp": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "go": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "rust": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "swift": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "kotlin": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "scala": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "php": LanguageCommentConfig(["//", "#"], ["/*"], ["*"]),
    # Shell-style languages
    "python": LanguageCommentConfig(["#"]),
    "ruby": LanguageCommentConfig(["#"]),
    "perl": LanguageCommentConfig(["#"]),
    "shellscript": LanguageCommentConfig(["#"]),
    "yaml": LanguageCommentConfig(["#"]),
    "r": LanguageCommentConfig(["#"]),
    "elixir": LanguageCommentConfig(["#"]),
    # XML-style languages
    "html": LanguageCommentConfig([], ["<!--"]),
    "xml": LanguageCommentConfig([], ["<!--"]),
    "svg": LanguageCommentConfig([], ["<!--"]),
    # CSS-style languages
    "css": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "scss": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    "less": LanguageCommentConfig(["//"], ["/*"], ["*"]),
    # SQL
    "sql": LanguageCommentConfig(["--"], ["/*"], ["*"]),
    # Lua
    "lua": LanguageCommentConfig(["--"]),
    # Haskell
    "haskell": LanguageCommentConfig(["--"], ["{-"]),
    # PowerShell
    "powershell": LanguageCommentConfig(["#"], ["<#"]),
    # Visual Basic
    "vb": LanguageCommentConfig(["'", "rem "]),
    "vbscript": LanguageCommentConfig(["'", "rem "]),
    # Lisp-style languages
    "clojure": LanguageCommentConfig([";"]),
    "lisp": LanguageCommentConfig([";"]),
    "scheme": LanguageCommentConfig([";"]),
    # Erlang
    "erlang": LanguageCommentConfig(["%"]),
    # Fortran
    "fortran": LanguageCommentConfig(["c", "C", "!"]),
    # Pascal/Delphi
    "pascal": LanguageCommentConfig(["//"], ["{", "(*"]),
    "delphi": LanguageCommentConfig(["//"], ["{", "(*"]),
    # Markdown (supports HTML comments)
    "markdown": LanguageCommentConfig([], ["<!--"]),
}


def is_line_a_comment(line: str, language_id: str) -> bool:
    """
    Check if a line is a comment based on language - EXACT port from VSCode

    Args:
        line: The line text to check
        language_id: The language identifier

    Returns:
        True if the line is a comment
    """
    trimmed = line.strip()
    if not trimmed:
        return False

    # Get language config or use defaults
    config = LANGUAGE_COMMENTS.get(language_id)
    if not config:
        config = LanguageCommentConfig(["#", "//"], ["/*"], ["*"])

    # Check line comments
    for prefix in config.line_comments:
        if trimmed.startswith(prefix):
            return True

    # Check block comment starts
    for prefix in config.block_comment_start:
        if trimmed.startswith(prefix):
            return True

    # Check block comment continuation
    for prefix in config.block_comment_continue:
        if trimmed.startswith(prefix):
            return True

    # Special case for case-insensitive matches
    if language_id in ["vb", "vbscript"]:
        import re

        return bool(re.match(r"^rem\s", trimmed, re.IGNORECASE))

    return False


def get_comment_prefixes(language_id: str) -> List[str]:
    """
    Get comment prefixes for a language

    Args:
        language_id: The language identifier

    Returns:
        Array of comment prefixes
    """
    config = LANGUAGE_COMMENTS.get(language_id)
    if not config:
        return ["#", "//", "/*"]

    prefixes = list(config.line_comments)
    prefixes.extend(config.block_comment_start)
    return prefixes


def supports_line_comments(language_id: str) -> bool:
    """
    Check if a language supports line comments

    Args:
        language_id: The language identifier

    Returns:
        True if the language supports line comments
    """
    config = LANGUAGE_COMMENTS.get(language_id)
    return len(config.line_comments) > 0 if config else True


def supports_block_comments(language_id: str) -> bool:
    """
    Check if a language supports block comments

    Args:
        language_id: The language identifier

    Returns:
        True if the language supports block comments
    """
    config = LANGUAGE_COMMENTS.get(language_id)
    return len(config.block_comment_start) > 0 if config else True


def is_line_only_comment_markers(line: str, language_id: str) -> bool:
    """
    Check if a line contains only comment markers (no other meaningful content).

    Args:
        line: The line to check
        language_id: The programming language

    Returns:
        True if the line is empty or contains only comment markers
    """
    stripped = line.strip()

    if not stripped:
        return True

    # Check if the remaining content is just comment prefixes
    comment_prefixes = get_comment_prefixes(language_id)

    for prefix in comment_prefixes:
        prefix_stripped = prefix.strip()
        if stripped == prefix_stripped:
            return True
        # Also check for common comment-only patterns
        if stripped in [prefix_stripped + " ", prefix_stripped + "\t"]:
            return True

    return False


def remove_guard_tags_from_line(line: str) -> str:
    """
    Remove all guard tag patterns from a line of code.

    Args:
        line: The line to clean

    Returns:
        The line with guard tags removed
    """
    import re

    # Import patterns here to avoid circular dependencies
    from ..patterns import GUARD_TAG_PATTERNS

    cleaned_line = line

    # Remove guard tags using the comprehensive pattern
    cleaned_line = re.sub(GUARD_TAG_PATTERNS.GUARD_TAG, "", cleaned_line)
    cleaned_line = re.sub(GUARD_TAG_PATTERNS.MARKDOWN_GUARD_TAG, "", cleaned_line)

    return cleaned_line


def should_include_guard_line_in_context(guard_line: str, language_id: str) -> Tuple[bool, str]:
    """
    Determine if a guard tag line should be included in context content.

    Args:
        guard_line: The original line containing the guard tag
        language_id: The programming language

    Returns:
        Tuple of (should_include, cleaned_content)
    """
    # Remove guard tags from the line
    cleaned_line = remove_guard_tags_from_line(guard_line)

    # Check if only comment markers remain
    if is_line_only_comment_markers(cleaned_line, language_id):
        return False, ""

    # Return the cleaned line if it has meaningful content
    return True, cleaned_line.strip()
