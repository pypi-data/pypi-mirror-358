"""
Tree-sitter based parser for CodeGuard CLI.
Port of the VSCode plugin's core/parser.ts functionality.
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..error_handling import get_logger
from ..exit_codes import (
    TREE_SITTER_LANGUAGE_LOAD_FAILED,
    TREE_SITTER_LANGUAGE_NOT_SUPPORTED,
    TREE_SITTER_NOT_INITIALIZED,
    TREE_SITTER_NOT_INSTALLED,
)
from ..language.config import TREE_SITTER_LANGUAGES
from .comment_detector import get_comment_prefixes

try:
    import tree_sitter as ts
    from tree_sitter import Language, Node, Tree

    TREE_SITTER_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.critical(f"tree-sitter is required but not available: {e}")
    logger.critical("Install tree-sitter with: pip install tree-sitter")
    sys.exit(TREE_SITTER_NOT_INSTALLED)


@dataclass
class NodePosition:
    """Position information for a tree-sitter node."""

    line: int
    column: int


@dataclass
class NodeBoundaries:
    """Boundary information for a tree-sitter node."""

    start: NodePosition
    end: NodePosition


@dataclass
class ParseResult:
    """Result of parsing a document with tree-sitter."""

    tree: Optional["Tree"]
    root_node: Optional["Node"]
    language: str
    success: bool
    error_message: Optional[str] = None


class TreeSitterParser:
    """Tree-sitter parser for various programming languages."""

    def __init__(self) -> None:
        self._languages: Dict[str, Language] = {}
        self._supported_languages = TREE_SITTER_LANGUAGES
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize tree-sitter - parsers are loaded lazily per language."""
        if self._initialized:
            return True

        # Just mark as initialized - parsers are loaded on-demand
        self._initialized = True
        return self._initialized

    def _load_language_parser(self, language_id: str) -> bool:
        """Load a specific language parser on-demand. Exit if it fails to load."""
        if language_id in self._languages:
            return True  # Already loaded

        # Map of language IDs to their tree-sitter package imports
        language_imports = {
            "python": "tree_sitter_python",
            "javascript": "tree_sitter_javascript",
            "typescript": "tree_sitter_typescript",
            "typescriptreact": "tree_sitter_typescript",
            "javascriptreact": "tree_sitter_javascript",
            "java": "tree_sitter_java",
            "c": "tree_sitter_cpp",  # Use cpp parser for C
            "cpp": "tree_sitter_cpp",
            "csharp": "tree_sitter_c_sharp",
            "go": "tree_sitter_go",
            "rust": "tree_sitter_rust",
            "php": "tree_sitter_php",
            "ruby": "tree_sitter_ruby",
            "html": "tree_sitter_html",
            "css": "tree_sitter_css",
            "bash": "tree_sitter_bash",
            "sql": "tree_sitter_sql",
            "json": "tree_sitter_json",
            "yaml": "tree_sitter_yaml",
            "toml": "tree_sitter_toml",
            "lua": "tree_sitter_lua",
            "scala": "tree_sitter_scala",
            "haskell": "tree_sitter_haskell",
            "ocaml": "tree_sitter_ocaml",
            "markdown": "tree_sitter_markdown",
        }

        if language_id not in language_imports:
            logger = get_logger(__name__)
            logger.debug(
                f"Language {language_id} not supported by tree-sitter, will fall back to regex parsing"
            )
            logger.debug(f"Supported languages: {list(language_imports.keys())}")
            return False

        module_name = language_imports[language_id]
        try:
            # Import the language package and get language object
            import importlib

            module = importlib.import_module(module_name)

            # Handle special cases for typescript (has multiple functions)
            if language_id == "typescript":
                language_obj = module.language_typescript()
            elif language_id == "typescriptreact":
                language_obj = module.language_tsx()
            else:
                # Standard case
                language_obj = module.language()

            # Create Language wrapper - this is the working pattern from the existing code
            language = Language(language_obj)
            self._languages[language_id] = language
            return True

        except ImportError as e:
            logger = get_logger(__name__)
            logger.critical(f"Required tree-sitter package not installed: {module_name}")
            logger.critical(f"Install with: pip install {module_name.replace('_', '-')}")
            sys.exit(TREE_SITTER_LANGUAGE_LOAD_FAILED)
        except Exception as e:
            logger = get_logger(__name__)
            logger.critical(f"Failed to load tree-sitter parser for {language_id}: {e}")
            sys.exit(TREE_SITTER_LANGUAGE_LOAD_FAILED)

    def _find_wasm_directory(self) -> Optional[Path]:
        """Find the tree-sitter WASM parsers directory."""
        # Check multiple possible locations
        possible_paths = [
            # Relative to this module
            Path(__file__).parent.parent.parent / "resources" / "tree-sitter-wasm",
            # From VSCode plugin (if available)
            Path(__file__).parent.parent.parent.parent
            / "CodeGuard-vscode-plugin"
            / "resources"
            / "tree-sitter-wasm",
            # Current working directory
            Path.cwd() / "resources" / "tree-sitter-wasm",
            # Check environment variable
            (
                Path(os.environ.get("TREE_SITTER_WASM_DIR", ""))
                if os.environ.get("TREE_SITTER_WASM_DIR")
                else None
            ),
        ]

        for path in possible_paths:
            if path and path.exists() and path.is_dir():
                return path

        return None

    def is_language_supported(self, language_id: str) -> bool:
        """Check if a language is supported."""
        return language_id in self._supported_languages

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language IDs."""
        return list(self._supported_languages.keys())

    def parse_document(self, content: str, language_id: str) -> ParseResult:
        """Parse a document using tree-sitter."""
        if not self._initialized:
            logger = get_logger(__name__)
            logger.critical("Tree-sitter not initialized")
            sys.exit(TREE_SITTER_NOT_INITIALIZED)

        # Load the language parser on-demand (returns False if not supported)
        if not self._load_language_parser(language_id):
            # Language not supported, return failed result for graceful fallback
            return ParseResult(
                None,
                None,
                language_id,
                False,
                f"Language {language_id} not supported by tree-sitter",
            )

        try:
            language = self._languages[language_id]
            parser = ts.Parser(language)

            tree = parser.parse(content.encode("utf8"))
            return ParseResult(tree, tree.root_node, language_id, True)

        except Exception as e:
            # Don't exit on parsing errors - return failed result for recovery
            return ParseResult(None, None, language_id, False, str(e))

    def find_node_at_position(self, root_node: Node, line: int, column: int) -> Optional[Node]:
        """Find the smallest node containing the given position."""
        if not root_node:
            return None

        point = (line - 1, column)  # Convert to 0-based indexing
        return root_node.descendant_for_point_range(point, point)

    def find_parent_of_type(self, node: Node, node_type: str) -> Optional[Node]:
        """Find the first parent node of the specified type."""
        current = node.parent
        while current:
            if current.type == node_type:
                return current
            current = current.parent
        return None

    def get_node_boundaries(self, node: Node) -> NodeBoundaries:
        """Get the boundaries of a node."""
        start = NodePosition(node.start_point[0] + 1, node.start_point[1])  # Convert to 1-based
        end = NodePosition(node.end_point[0] + 1, node.end_point[1])
        return NodeBoundaries(start, end)

    def get_node_type_for_line(self, content: str, language_id: str, line_number: int) -> str:
        """Get the semantic node type for a specific line."""
        parse_result = self.parse_document(content, language_id)
        if not parse_result.success or not parse_result.root_node:
            return "comment"  # Fallback to "comment" when parsing fails

        # Find the most specific node for this line
        lines = content.split("\n")
        if line_number <= 0 or line_number > len(lines):
            return "unknown"

        line_content = lines[line_number - 1]

        # For empty lines, find node at position 0 to get containing scope
        if not line_content.strip():
            node = self.find_node_at_position(parse_result.root_node, line_number, 0)
        else:
            # Find node at the start of the line's content
            first_char_col = len(line_content) - len(line_content.lstrip())
            node = self.find_node_at_position(parse_result.root_node, line_number, first_char_col)

        if not node:
            return "unknown"

        # Return the most specific node type that covers this line
        node_type = node.type

        # Map some common node types to more readable names
        type_mappings = {
            "module": "program",
            "source_file": "program",
            "program": "program",
            "function_declaration": "function",
            "function_definition": "function",
            "method_definition": "method",
            "method_declaration": "method",
            "class_definition": "class",
            "class_declaration": "class",
            "interface_declaration": "interface",
            "type_declaration": "interface",
            "block": "body",
            "compound_statement": "body",
            "statement_block": "body",
            "expression_statement": "statement",
            "assignment_statement": "statement",
            "if_statement": "statement",
            "for_statement": "statement",
            "for_in_statement": "statement",
            "while_statement": "statement",
            "return_statement": "statement",
            "try_statement": "statement",
            "for": "statement",
            "try": "statement",
            "return": "statement",
            "if": "statement",
            "await": "statement",
            "await_expression": "statement",
            "comment": "comment",
            "string_literal": "string_fragment",
            "template_string": "template_str",
            "formal_parameters": "formal_param",
            "parameter_list": "formal_param",
            "import_statement": "import",
            "import_declaration": "import",
            "export_statement": "export",
            "export_declaration": "export",
            "variable_declaration": "lexical",
            "lexical_declaration": "lexical",
            "variable_declarator": "lexical",
            "const": "lexical",
            "let": "lexical",
            "var": "lexical",
            "object_expression": "object",
            "object_literal": "object",
            "object": "object",
            "pair": "pair",
            "property_identifier": "object",
            "shorthand_property_identifier": "shorthand_property_identifier",
            "dictionary": "object",
            "}": "object",
            "interface_body": "interface_body",
            "call_expression": "identifier",
            "member_expression": "identifier",
            "assignment_expression": "identifier",
            "binary_expression": "identifier",
            "identifier": "identifier",
            "this": "identifier",
            "static": "static",
            "async": "async",
        }

        return type_mappings.get(node_type, node_type)


# Global parser instance
_parser_instance: Optional[TreeSitterParser] = None


def get_parser() -> TreeSitterParser:
    """Get the global parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = TreeSitterParser()
        _parser_instance.initialize()
    return _parser_instance


def is_tree_sitter_available() -> bool:
    """Check if tree-sitter is available and initialized."""
    # Tree-sitter is always required, so this should always return True
    # If tree-sitter is not available, the module would have exited during import
    return get_parser()._initialized


def parse_document(content: str, language_id: str) -> ParseResult:
    """Parse a document using tree-sitter."""
    return get_parser().parse_document(content, language_id)


def get_node_type_for_line(content: str, language_id: str, line_number: int) -> str:
    """Get the semantic node type for a specific line."""
    return get_parser().get_node_type_for_line(content, language_id, line_number)


def find_node_at_position(root_node: Node, line: int, column: int) -> Optional[Node]:
    """Find the smallest node containing the given position."""
    return get_parser().find_node_at_position(root_node, line, column)


def find_parent_of_type(node: Node, node_type: str) -> Optional[Node]:
    """Find the first parent node of the specified type."""
    return get_parser().find_parent_of_type(node, node_type)


def get_node_boundaries(node: Node) -> NodeBoundaries:
    """Get the boundaries of a node."""
    return get_parser().get_node_boundaries(node)


def get_supported_languages() -> List[str]:
    """Get list of supported language IDs."""
    return get_parser().get_supported_languages()


def is_language_supported(language_id: str) -> bool:
    """Check if a language is supported."""
    return get_parser().is_language_supported(language_id)


async def calculate_document_metrics(content: str, language_id: str) -> Dict[str, Any]:
    """
    Calculate comprehensive document metrics including enhanced complexity analysis.

    This provides complete parsing and structural analysis using tree-sitter
    with advanced complexity metrics automatically included.

    Args:
        content: Source code content
        language_id: Programming language identifier

    Returns:
        Dictionary with comprehensive document metrics
    """
    if not TREE_SITTER_AVAILABLE:
        return {
            "parse_success": False,
            "error": "tree-sitter not available",
            "line_count": len(content.split("\n")),
            "language_id": language_id,
        }

    parse_result = parse_document(content, language_id)
    lines = content.split("\n")

    metrics = {
        "parse_success": parse_result.success,
        "language_id": language_id,
        "line_count": len(lines),
        "byte_count": len(content.encode("utf-8")),
    }

    if not parse_result.success or not parse_result.root_node:
        metrics["error"] = parse_result.error_message or "parse failed"
        return metrics

    root_node = parse_result.root_node

    # Calculate basic tree metrics
    metrics.update(
        {
            "total_nodes": root_node.descendant_count,
            "named_nodes": root_node.named_child_count,
            "has_errors": root_node.has_error,
            "max_depth": _calculate_tree_depth(root_node),
        }
    )

    # Calculate all metrics in single optimized pass
    all_metrics = await calculate_metrics(root_node, content, language_id)
    metrics.update(all_metrics)

    return metrics


def _calculate_tree_depth(node: Node) -> int:
    """Calculate maximum depth of the parse tree using iterative approach."""
    if not node:
        return 0

    max_depth = 0
    stack = [(node, 1)]

    while stack:
        current, depth = stack.pop()
        max_depth = max(max_depth, depth)

        for child in current.children:
            stack.append((child, depth + 1))

    return max_depth


def _count_comment_lines(content: str, language_id: str) -> int:
    lines = content.split("\n")
    comment_prefixes = tuple(get_comment_prefixes(language_id))
    return sum(
        1
        for line in lines
        if line.strip() and any(line.strip().startswith(prefix) for prefix in comment_prefixes)
    )


def _count_nodes_by_type(node: Node, target_types: List[str]) -> int:
    target_set = frozenset(target_types)
    count = 0
    stack = [node]

    while stack:
        current = stack.pop()
        if current.type in target_set:
            count += 1
        stack.extend(reversed(current.children))

    return count


# Pre-compiled regex patterns for maximum performance
_CONTROL_FLOW_REGEX = re.compile(
    r"\b(if|for|while|switch|try|catch|except|match|select|with)\b", re.IGNORECASE
)
_DECISION_REGEX = re.compile(
    r"\b(if|elif|for|while|case|try|catch|except|match|boolean_operator|binary_expression|conditional_expression|logical)\b",
    re.IGNORECASE,
)
_EXCLUDE_REGEX = re.compile(
    r"\b(clause|body|block|expression_statement|identifier|comment)\b", re.IGNORECASE
)


async def calculate_metrics(node: Node, content: str, language_id: str) -> Dict[str, Any]:
    comment_prefixes = tuple(get_comment_prefixes(language_id))

    # Using pre-compiled regex patterns for maximum performance

    FUNCTION_TYPES = frozenset(
        {
            "python": ["function_definition", "async_function_definition"],
            "javascript": [
                "function_declaration",
                "function_expression",
                "arrow_function",
                "method_definition",
            ],
            "typescript": [
                "function_declaration",
                "function_expression",
                "arrow_function",
                "method_definition",
            ],
            "java": ["method_declaration", "constructor_declaration"],
            "c": ["function_definition"],
            "cpp": ["function_definition", "function_declarator"],
            "csharp": ["method_declaration", "constructor_declaration"],
            "go": ["function_declaration", "method_declaration"],
            "rust": ["function_item", "impl_item"],
        }.get(language_id, ["function", "method"])
    )

    CLASS_TYPES = frozenset(
        {
            "python": ["class_definition"],
            "javascript": ["class_declaration"],
            "typescript": ["class_declaration", "interface_declaration"],
            "java": ["class_declaration", "interface_declaration", "enum_declaration"],
            "c": ["struct_specifier"],
            "cpp": ["class_specifier", "struct_specifier"],
            "csharp": ["class_declaration", "interface_declaration", "struct_declaration"],
            "go": ["type_declaration"],
            "rust": ["struct_item", "enum_item", "trait_item"],
        }.get(language_id, ["class"])
    )

    IMPORT_TYPES = frozenset(
        {
            "python": ["import_statement", "import_from_statement"],
            "javascript": ["import_statement"],
            "typescript": ["import_statement"],
            "java": ["import_declaration"],
            "go": ["import_declaration"],
            "rust": ["use_declaration"],
            "c": ["preproc_include"],
            "cpp": ["preproc_include"],
        }.get(language_id, ["import"])
    )

    EXPORT_TYPES = frozenset(
        {"javascript": ["export_statement"], "typescript": ["export_statement"]}.get(
            language_id, []
        )
    )

    lines = content.split("\n")
    line_count = len(lines)

    class MetricsAccumulator:
        __slots__ = (
            "comment_lines",
            "blank_lines",
            "code_lines",
            "control_flow_complexity",
            "cyclomatic_complexity",
            "complexity_score_raw",
            "total_nodes",
            "max_depth",
            "function_count",
            "class_count",
            "import_count",
            "export_count",
            "functions",
            "classes",
            "imports",
            "exports",
        )

        def __init__(self):
            self.comment_lines = 0
            self.blank_lines = 0
            self.code_lines = 0
            self.control_flow_complexity = 0
            self.cyclomatic_complexity = 1
            self.complexity_score_raw = 0.0
            self.total_nodes = 0
            self.max_depth = 0
            self.function_count = 0
            self.class_count = 0
            self.import_count = 0
            self.export_count = 0
            self.functions = []
            self.classes = []
            self.imports = []
            self.exports = []

    metrics = MetricsAccumulator()

    stack = [(node, 0)]
    last_yield_time = time.time()

    while stack:
        # Time-based yielding every 50ms
        current_time = time.time()
        if (current_time - last_yield_time) >= 0.05:  # 50ms
            await asyncio.sleep(0)
            last_yield_time = current_time

        current_node, depth = stack.pop()
        node_type = current_node.type

        metrics.total_nodes += 1
        if depth > metrics.max_depth:
            metrics.max_depth = depth

        node_type_lower = node_type.lower()

        has_exclude = _EXCLUDE_REGEX.search(node_type_lower) is not None

        if not has_exclude:
            if _CONTROL_FLOW_REGEX.search(node_type_lower):
                metrics.control_flow_complexity += 1
                metrics.complexity_score_raw += 1.0 + (depth * 0.5)

            if _DECISION_REGEX.search(node_type_lower):
                metrics.cyclomatic_complexity += 1

        if depth > 3:
            metrics.complexity_score_raw += 0.1

        if node_type in FUNCTION_TYPES:
            metrics.function_count += 1
            try:
                for child in current_node.children:
                    if child.type in ("identifier", "function_name"):
                        name = content[child.start_byte : child.end_byte]
                        line_num = current_node.start_point[0] + 1
                        if line_num <= line_count:
                            definition = lines[current_node.start_point[0]].strip()
                            metrics.functions.append(
                                {"name": name, "line_number": line_num, "definition": definition}
                            )
                        break
            except (IndexError, AttributeError):
                pass

        elif node_type in CLASS_TYPES:
            metrics.class_count += 1
            try:
                for child in current_node.children:
                    if child.type in ("identifier", "type_identifier"):
                        name = content[child.start_byte : child.end_byte]
                        line_num = current_node.start_point[0] + 1
                        if line_num <= line_count:
                            definition = lines[current_node.start_point[0]].strip()
                            metrics.classes.append(
                                {"name": name, "line_number": line_num, "definition": definition}
                            )
                        break
            except (IndexError, AttributeError):
                pass

        elif node_type in IMPORT_TYPES:
            metrics.import_count += 1
            try:
                line_num = current_node.start_point[0] + 1
                if line_num <= line_count:
                    statement = lines[current_node.start_point[0]].strip()
                    metrics.imports.append(
                        {"type": "import", "statement": statement, "line_number": line_num}
                    )
            except (IndexError, AttributeError):
                pass

        elif node_type in EXPORT_TYPES:
            metrics.export_count += 1
            try:
                line_num = current_node.start_point[0] + 1
                if line_num <= line_count:
                    statement = lines[current_node.start_point[0]].strip()
                    metrics.exports.append(
                        {"type": "export", "statement": statement, "line_number": line_num}
                    )
            except (IndexError, AttributeError):
                pass

        stack.extend((child, depth + 1) for child in reversed(current_node.children))

    # Optimized batch line processing
    stripped_lines = [line.strip() for line in lines]
    comment_prefixes_set = frozenset(comment_prefixes)

    for stripped in stripped_lines:
        if not stripped:
            metrics.blank_lines += 1
        elif any(stripped.startswith(prefix) for prefix in comment_prefixes_set):
            metrics.comment_lines += 1
        else:
            metrics.code_lines += 1

    complexity_score = (
        round(metrics.complexity_score_raw / max(metrics.total_nodes / 100, 1), 2)
        if metrics.total_nodes > 0
        else 0.0
    )

    if metrics.max_depth <= 3:
        nested_complexity = 0.0
    elif metrics.max_depth <= 6:
        nested_complexity = (metrics.max_depth - 3) * 1.5
    else:
        nested_complexity = 4.5 + ((metrics.max_depth - 6) ** 1.5)

    return {
        "comment_lines": metrics.comment_lines,
        "blank_lines": metrics.blank_lines,
        "code_lines": metrics.code_lines,
        "complexity_score": complexity_score,
        "control_flow_complexity": metrics.control_flow_complexity,
        "cyclomatic_complexity": metrics.cyclomatic_complexity,
        "nested_complexity": nested_complexity,
        "function_count": metrics.function_count,
        "class_count": metrics.class_count,
        "import_count": metrics.import_count,
        "export_count": metrics.export_count,
        "functions": metrics.functions,
        "classes": metrics.classes,
        "imports": metrics.imports,
        "exports": metrics.exports,
        "total_nodes": metrics.total_nodes,
        "max_depth": metrics.max_depth,
    }
