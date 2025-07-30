"""
Centralized language configuration for CodeGuard CLI.

This module provides a single source of truth for all programming language
configurations, file extension mappings, and project detection patterns.
Based on the comprehensive approach from workspace_analyzer.py.
"""

from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set

# Comprehensive language configuration combining all patterns from the codebase
# Based on workspace_analyzer.py but enhanced with all languages found across modules
LANGUAGE_FILES = {
    # Web languages
    "javascript": ["package.json", "*.js", "*.mjs", "*.cjs"],
    "javascriptreact": ["*.jsx"],
    "typescript": ["tsconfig.json", "*.ts"],
    "typescriptreact": ["*.tsx"],
    # Backend languages
    "python": ["requirements.txt", "setup.py", "pyproject.toml", "*.py"],
    "java": ["pom.xml", "build.gradle", "*.java"],
    "csharp": ["*.csproj", "*.sln", "*.cs"],
    "go": ["go.mod", "go.sum", "*.go"],
    "rust": ["Cargo.toml", "Cargo.lock", "*.rs"],
    "php": ["composer.json", "*.php"],
    "ruby": ["Gemfile", "*.rb"],
    # Systems languages
    "cpp": ["CMakeLists.txt", "Makefile", "*.cpp", "*.hpp", "*.c", "*.h"],
    "c": ["*.c", "*.h"],
    # Mobile/Cross-platform
    "swift": ["Package.swift", "*.swift"],
    "kotlin": ["*.kt", "*.kts"],
    "dart": ["pubspec.yaml", "*.dart"],
    # JVM languages
    "scala": ["build.sbt", "*.scala"],
    # Functional languages
    "clojure": ["project.clj", "deps.edn", "*.clj"],
    "elixir": ["mix.exs", "*.ex", "*.exs"],
    "haskell": ["*.hs"],
    "ocaml": ["*.ml", "*.mli"],
    # Scripting/Other
    "r": ["DESCRIPTION", "*.R"],
    "julia": ["Project.toml", "*.jl"],
    "lua": ["*.lua"],
    "shell": ["*.sh", "*.bash", "*.zsh"],
    # Markup/Config
    "markdown": ["*.md"],
    "html": ["*.html", "*.htm"],
    "css": ["*.css"],
    "yaml": ["*.yml", "*.yaml"],
    "json": ["*.json"],
    "toml": ["*.toml"],
    "xml": ["*.xml"],
    # Database
    "sql": ["*.sql"],
    # Other
    "bash": ["*.sh", "*.bash"],
}

# Tree-sitter language mappings (from tree_sitter_parser.py)
TREE_SITTER_LANGUAGES = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "typescriptreact": "tsx",
    "javascriptreact": "javascript",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "csharp": "c_sharp",
    "go": "go",
    "rust": "rust",
    "php": "php",
    "ruby": "ruby",
    "html": "html",
    "css": "css",
    "bash": "bash",
    "sql": "sql",
    "json": "json",
    "yaml": "yaml",
    "toml": "toml",
    "lua": "lua",
    "scala": "scala",
    "haskell": "haskell",
    "ocaml": "ocaml",
    "markdown": "markdown",
}

# Language aliases for compatibility
LANGUAGE_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "tsx": "typescriptreact",
    "jsx": "javascriptreact",
    "py": "python",
    "rb": "ruby",
    "rs": "rust",
    "sh": "shell",
    "md": "markdown",
    "yml": "yaml",
}

# File type detection patterns with clear categorization
FILE_TYPE_PATTERNS = {
    "config": {
        "extensions": {".yml", ".yaml", ".toml", ".ini", ".conf", ".json", ".xml"},
        "exact_names": {"dockerfile", "makefile", ".env", ".gitignore", ".editorconfig"},
        "name_contains": ["config", "settings"],
    },
    "test": {
        "extensions": {
            ".test.js",
            ".test.ts",
            ".test.jsx",
            ".test.tsx",
            ".spec.js",
            ".spec.ts",
            ".spec.jsx",
            ".spec.tsx",
        },
        "exact_names": {
            "jest.config.js",
            "vitest.config.js",
            "karma.conf.js",
            "pytest.ini",
            "tox.ini",
        },
        "name_contains": ["test"],
        "name_starts_with": ["test_"],
        "name_ends_with": ["_test.py", "_test.js", "_test.ts", "_spec.py", "_spec.js", "_spec.ts"],
        "directories": {"test", "tests", "__tests__", "spec", "specs"},
    },
    "doc": {
        "extensions": {".md", ".rst", ".txt"},
        "exact_names": {
            "readme.md",
            "readme.rst",
            "readme.txt",
            "changelog.md",
            "contributing.md",
            "license",
            "license.txt",
        },
        "name_contains": ["readme", "changelog", "contributing", "license"],
        "directories": {"docs", "doc", "documentation"},
    },
    "context": {
        "extensions": {".md", ".txt"},
        "exact_names": {
            "claude.md",
            "claude.txt",
            "module_context.md",
            "module_info.md",
            "module_info.txt",
            "context.md",
            "context.txt",
        },
        "name_wildcard": ["*_context.md", "*_context.txt", "*_overview.md", "*_overview.txt"],
        "description": "AI and LLM context files",
    },
    "ai_ownership": {
        "exact_names": {
            ".ai-owner",
            "ai-owner",
        },
        "description": "AI ownership and delegation files",
    },
    "system_exclude": {
        "directories": {
            ".codeguard",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".tox",
            ".coverage",
            ".mypy_cache",
            ".venv",
            "venv",
            ".env",
            "build",
            "dist",
            ".DS_Store",
            ".nyc_output",
            ".next",
            ".nuxt",
            "target",
            "bin",
            "obj",
        },
        "description": "System directories that should never be analyzed as source code",
    },
}

# Reverse mapping: extension -> language (auto-generated)
_EXTENSION_TO_LANGUAGE: Optional[Dict[str, str]] = None


def _build_extension_mapping() -> Dict[str, str]:
    """Build reverse mapping from file extensions to languages."""
    extension_map = {}

    for language, patterns in LANGUAGE_FILES.items():
        for pattern in patterns:
            if pattern.startswith("*."):
                ext = pattern[1:]  # Remove the *
                if ext not in extension_map:
                    extension_map[ext] = language
                # If extension exists, keep first mapping (preference order)

    return extension_map


def get_extension_to_language_mapping() -> Dict[str, str]:
    """Get the extension to language mapping (cached)."""
    global _EXTENSION_TO_LANGUAGE
    if _EXTENSION_TO_LANGUAGE is None:
        _EXTENSION_TO_LANGUAGE = _build_extension_mapping()
    return _EXTENSION_TO_LANGUAGE


def get_language_for_extension(ext: str) -> str:
    """
    Get programming language for a file extension.

    Args:
        ext: File extension (with or without leading dot)

    Returns:
        Language name or "unknown" if not found
    """
    if not ext:
        return "unknown"

    # Normalize extension
    if not ext.startswith("."):
        ext = "." + ext

    mapping = get_extension_to_language_mapping()
    language = mapping.get(ext, "unknown")

    # Check aliases
    if language == "unknown" and ext[1:] in LANGUAGE_ALIASES:
        language = LANGUAGE_ALIASES[ext[1:]]

    return language


def get_language_for_file_path(file_path: str) -> str:
    """
    Get programming language for a file path.

    Args:
        file_path: Path to the file

    Returns:
        Language name or "unknown" if not found
    """
    path = Path(file_path)
    return get_language_for_extension(path.suffix)


def get_extensions_for_language(language: str) -> List[str]:
    """
    Get file extensions for a programming language.

    Args:
        language: Programming language name

    Returns:
        List of file extensions (with dots)
    """
    patterns = LANGUAGE_FILES.get(language, [])
    extensions = []

    for pattern in patterns:
        if pattern.startswith("*."):
            extensions.append(pattern[1:])  # Remove the *

    return extensions


def get_project_files_for_language(language: str) -> List[str]:
    """
    Get project files (non-extension patterns) for a programming language.

    Args:
        language: Programming language name

    Returns:
        List of project files (package.json, Cargo.toml, etc.)
    """
    patterns = LANGUAGE_FILES.get(language, [])
    project_files = []

    for pattern in patterns:
        if not pattern.startswith("*."):
            project_files.append(pattern)

    return project_files


def get_analyzable_extensions() -> Set[str]:
    """
    Get set of all file extensions that can be analyzed.

    Returns:
        Set of file extensions (with dots)
    """
    extensions = set()

    for patterns in LANGUAGE_FILES.values():
        for pattern in patterns:
            if pattern.startswith("*."):
                extensions.add(pattern[1:])  # Remove the *

    return extensions


def get_code_extensions() -> Set[str]:
    """
    Get set of programming language file extensions (excludes markup/config).

    Returns:
        Set of code file extensions (with dots)
    """
    # Exclude markup and config languages
    exclude_languages = {"markdown", "html", "css", "yaml", "json", "toml", "xml"}

    extensions = set()
    for language, patterns in LANGUAGE_FILES.items():
        if language not in exclude_languages:
            for pattern in patterns:
                if pattern.startswith("*."):
                    extensions.add(pattern[1:])  # Remove the *

    return extensions


def is_supported_language(language: str) -> bool:
    """
    Check if a language is supported.

    Args:
        language: Programming language name

    Returns:
        True if language is supported
    """
    return language in LANGUAGE_FILES or language in LANGUAGE_ALIASES


def is_tree_sitter_supported(language: str) -> bool:
    """
    Check if a language is supported by tree-sitter.

    Args:
        language: Programming language name

    Returns:
        True if tree-sitter support is available
    """
    return language in TREE_SITTER_LANGUAGES


def get_tree_sitter_language(language: str) -> Optional[str]:
    """
    Get tree-sitter language identifier for a language.

    Args:
        language: Programming language name

    Returns:
        Tree-sitter language identifier or None if not supported
    """
    return TREE_SITTER_LANGUAGES.get(language)


def get_supported_languages() -> List[str]:
    """
    Get list of all supported programming languages.

    Returns:
        Sorted list of language names
    """
    return sorted(LANGUAGE_FILES.keys())


def get_tree_sitter_supported_languages() -> List[str]:
    """
    Get list of languages supported by tree-sitter.

    Returns:
        Sorted list of tree-sitter supported language names
    """
    return sorted(TREE_SITTER_LANGUAGES.keys())


def is_code_file(file_path: str) -> bool:
    """
    Check if a file is a programming language file (not markup/config).

    Args:
        file_path: Path to the file

    Returns:
        True if it's a code file
    """
    language = get_language_for_file_path(file_path)
    exclude_languages = {"markdown", "html", "css", "yaml", "json", "toml", "xml", "unknown"}
    return language not in exclude_languages


def is_code_file_by_extension(file_path) -> bool:
    """
    Check if a file is a code file based on extension match.
    Fast extension-based check using code extensions set.

    Args:
        file_path: Path to the file (string or Path object)

    Returns:
        True if the file extension is in the code extensions set
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    code_extensions = get_code_extensions()
    return file_path.suffix.lower() in code_extensions


def is_config_file(file_path) -> bool:
    """
    Check if a file is a configuration file.

    Args:
        file_path: Path to the file (string or Path object)

    Returns:
        True if the file is a configuration file
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    patterns = FILE_TYPE_PATTERNS["config"]
    filename = file_path.name.lower()

    # Check exact extension match
    if file_path.suffix.lower() in patterns["extensions"]:
        return True

    # Check exact filename match
    if filename in patterns["exact_names"]:
        return True

    # Check if filename contains config-related words
    return any(word in filename for word in patterns["name_contains"])


def is_test_file(file_path) -> bool:
    """
    Check if a file is a test file.

    Args:
        file_path: Path to the file (string or Path object)

    Returns:
        True if the file is a test file
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    patterns = FILE_TYPE_PATTERNS["test"]
    filename = file_path.name.lower()

    # Check specific test extensions (like .test.js)
    for ext in patterns["extensions"]:
        if filename.endswith(ext):
            return True

    # Check exact names
    if filename in patterns["exact_names"]:
        return True

    # Check name patterns
    if any(word in filename for word in patterns["name_contains"]):
        return True

    if any(filename.startswith(prefix) for prefix in patterns["name_starts_with"]):
        return True

    if any(filename.endswith(suffix) for suffix in patterns["name_ends_with"]):
        return True

    return False


def is_doc_file(file_path) -> bool:
    """
    Check if a file is a documentation file.

    Args:
        file_path: Path to the file (string or Path object)

    Returns:
        True if the file is a documentation file
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    patterns = FILE_TYPE_PATTERNS["doc"]
    filename = file_path.name.lower()

    # Check exact extension match
    if file_path.suffix.lower() in patterns["extensions"]:
        return True

    # Check exact filename match
    if filename in patterns["exact_names"]:
        return True

    # Check if filename contains doc-related words
    return any(word in filename for word in patterns["name_contains"])


def has_tests_in_directory(directory_path) -> bool:
    """
    Check if a directory contains test files or test directories.

    Args:
        directory_path: Path to the directory (string or Path object)

    Returns:
        True if the directory contains tests
    """
    if isinstance(directory_path, str):
        directory_path = Path(directory_path)

    if not directory_path.exists() or not directory_path.is_dir():
        return False

    patterns = FILE_TYPE_PATTERNS["test"]

    try:
        # Check for test directories
        for item in directory_path.iterdir():
            if item.is_dir() and item.name.lower() in patterns["directories"]:
                return True

        # Check for test files
        for item in directory_path.iterdir():
            if item.is_file() and is_test_file(item):
                return True

    except (PermissionError, OSError):
        pass

    return False


def has_docs_in_directory(directory_path) -> bool:
    """
    Check if a directory contains documentation files or doc directories.

    Args:
        directory_path: Path to the directory (string or Path object)

    Returns:
        True if the directory contains documentation
    """
    if isinstance(directory_path, str):
        directory_path = Path(directory_path)

    if not directory_path.exists() or not directory_path.is_dir():
        return False

    patterns = FILE_TYPE_PATTERNS["doc"]

    try:
        # Check for doc directories
        for item in directory_path.iterdir():
            if item.is_dir() and item.name.lower() in patterns["directories"]:
                return True

        # Check for doc files
        for item in directory_path.iterdir():
            if item.is_file() and is_doc_file(item):
                return True

    except (PermissionError, OSError):
        pass

    return False


def has_config_in_directory(directory_path) -> bool:
    """
    Check if a directory contains configuration files.

    Args:
        directory_path: Path to the directory (string or Path object)

    Returns:
        True if the directory contains configuration files
    """
    if isinstance(directory_path, str):
        directory_path = Path(directory_path)

    if not directory_path.exists() or not directory_path.is_dir():
        return False

    try:
        # Check for config files
        for item in directory_path.iterdir():
            if item.is_file() and is_config_file(item):
                return True

    except (PermissionError, OSError):
        pass

    return False


def is_project_file(file_path: str) -> bool:
    """
    Check if a file is a project configuration file.

    Args:
        file_path: Path to the file

    Returns:
        True if it's a project file
    """
    filename = Path(file_path).name

    for patterns in LANGUAGE_FILES.values():
        for pattern in patterns:
            if not pattern.startswith("*.") and pattern == filename:
                return True

    return False


def detect_language_from_content(content: str, file_path: str) -> str:
    """
    Detect language from file content and path.

    Args:
        content: File content
        file_path: Path to the file

    Returns:
        Detected language name
    """
    # First try extension-based detection
    language = get_language_for_file_path(file_path)
    if language != "unknown":
        return language

    # Content-based detection for files without extensions
    filename = Path(file_path).name.lower()

    # Common executable names
    if filename in ["makefile", "dockerfile"]:
        return "shell"

    # Shebang detection
    lines = content.split("\n", 2)
    if lines and lines[0].startswith("#!"):
        shebang = lines[0].lower()
        if "python" in shebang:
            return "python"
        elif any(shell in shebang for shell in ["bash", "sh", "zsh"]):
            return "shell"
        elif "node" in shebang:
            return "javascript"

    return "unknown"


# Compatibility functions for existing code
def create_extension_map() -> Dict[str, str]:
    """Create extension mapping for backward compatibility."""
    return get_extension_to_language_mapping()


def get_language_extensions() -> Set[str]:
    """Get all language extensions for backward compatibility."""
    return get_analyzable_extensions()


def get_language_display_name(language: str) -> str:
    """
    Get a human-readable display name for a programming language.

    Args:
        language: Internal language identifier

    Returns:
        Formatted display name for the language
    """
    if not language:
        return "Unknown"

    # Check aliases first and resolve to actual language
    actual_language = LANGUAGE_ALIASES.get(language, language)

    # Start with the base language from our configuration
    if actual_language in LANGUAGE_FILES:
        base_name = actual_language.title()
    else:
        base_name = actual_language.title()

    # Apply special formatting cases only where needed
    special_formatting = {
        "Javascriptreact": "React (JS)",
        "Typescriptreact": "React (TS)",
        "Csharp": "C#",
        "Cpp": "C++",
        "Php": "PHP",
        "Sql": "SQL",
        "Html": "HTML",
        "Css": "CSS",
        "Yaml": "YAML",
        "Json": "JSON",
        "Toml": "TOML",
        "Xml": "XML",
    }

    return special_formatting.get(base_name, base_name)


def is_other_context_file(file_path) -> bool:
    """Check if file is a 3rd party context file based on FILE_TYPE_PATTERNS."""
    if isinstance(file_path, str):
        file_path = Path(file_path)

    patterns = FILE_TYPE_PATTERNS["context"]
    filename = file_path.name.lower()

    # Check exact extension match
    if file_path.suffix.lower() in patterns["extensions"]:
        # Check exact filename match
        if filename in patterns["exact_names"]:
            return True

        # Check wildcard patterns
        if "name_wildcard" in patterns:
            for wildcard_pattern in patterns["name_wildcard"]:
                if fnmatch(filename, wildcard_pattern.lower()):
                    return True

    return False


def is_ai_ownership_file(file_path) -> Path | None:
    """Check if the passed path contains an AI ownership file.

    Returns the Path to the AI ownership file if found, otherwise None.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # If it's a file, check if it's an AI ownership file
    if file_path.is_file():
        name = file_path.name.lower()
        if name in {"ai-owner", ".ai-owner"}:
            return file_path
        return None

    # If it's a directory, check if it contains an AI ownership file
    if file_path.is_dir():
        # Check for ai-owner first (non-hidden version typically takes precedence)
        ai_owner_path = file_path / "ai-owner"
        if ai_owner_path.exists():
            return ai_owner_path

        # Then check for .ai-owner
        hidden_ai_owner_path = file_path / ".ai-owner"
        if hidden_ai_owner_path.exists():
            return hidden_ai_owner_path

    return None


def is_repository_directory(directory_path) -> tuple[bool, str]:
    """
    Check if directory contains any type of version control repository.

    Args:
        directory_path: Path to the directory (string or Path object)

    Returns:
        Tuple of (is_repo, repo_type) where repo_type is 'main', 'worktree', or 'other'
    """
    if isinstance(directory_path, str):
        directory_path = Path(directory_path)

    if not directory_path.is_dir():
        return False, ""

    # Check for git specifically first
    git_path = directory_path / ".git"
    if git_path.exists():
        if git_path.is_file():
            # This is a worktree - .git is a file with gitdir reference
            return True, "worktree"
        elif git_path.is_dir():
            # This is a main repository - .git is a directory
            return True, "main"

    # Support other VCS types (existing logic)
    vcs_markers = {".hg", ".svn", ".bzr", "_FOSSIL_", ".fslckout"}

    try:
        for item in directory_path.iterdir():
            if item.name in vcs_markers:
                return True, "other"
    except (PermissionError, OSError):
        pass

    return False, ""


def is_system_exclude_directory(directory_path) -> bool:
    """
    Check if a directory should be excluded from analysis as a system directory.

    Args:
        directory_path: Path to the directory (string or Path object)

    Returns:
        True if the directory should be excluded from analysis
    """
    if isinstance(directory_path, str):
        directory_path = Path(directory_path)

    patterns = FILE_TYPE_PATTERNS["system_exclude"]
    directory_name = directory_path.name.lower()

    # Check if directory name is in the exclude list
    return directory_name in patterns["directories"]


def is_ai_owned_module(module_path) -> Path | None:
    """
    Check if a module is AI-owned by detecting AI-OWNER files.

    Args:
        module_path: Path to the module directory

    Returns:
        True if module contains an AI-OWNER file
    """
    try:
        if isinstance(module_path, str):
            module_path = Path(module_path)

        if not module_path.is_dir():
            return None

        # Check for AI-OWNER files using existing detection logic
        return is_ai_ownership_file(module_path)

    except (PermissionError, OSError):
        # Silently return None on filesystem-related errors only
        return None
