"""
Centralized exit codes for CodeGuard CLI

Follows CLI conventions while maintaining granularity:
- 0: Success (universal)
- 1: General validation failure (like git, grep)
- 2: Usage/syntax error (like bash, find)
- 5: Access denied (Windows standard)
- Others: Specific granular error codes

Each error type has a unique exit code for debugging and automation.
"""

# Universal success
SUCCESS = 0

# Standard CLI patterns
GENERAL_ERROR = 1  # General failure (git, grep, most CLI tools)
USAGE_ERROR = 2  # Invalid arguments (bash, find, grep usage errors)

# Windows/Linux standard access errors
SECURITY_VIOLATION = 5  # Windows "Access Denied" standard code
PERMISSION_DENIED = 13  # Unix permission denied (EACCES)

# Validation errors
VALIDATION_FAILED = 1  # Use standard general error for validation
INPUT_VALIDATION_FAILED = 2  # Use standard usage error
CONFIG_VALIDATION_FAILED = 10  # Unique config validation error

# File/Directory access (maintain granularity)
FILE_NOT_FOUND = 8  # Unique code for file not found
DIRECTORY_NOT_FOUND = 9  # Unique code for directory not found
DOCUMENT_READ_FAILED = 11  # Unique code for document read failure
DOCUMENT_ACCESS_DENIED = 12  # Unique code for document access issues
DOCUMENT_FORMAT_INVALID = 14  # Unique code for format errors

# Tree-sitter related errors (maintain all granularity)
TREE_SITTER_NOT_INSTALLED = 20
TREE_SITTER_LANGUAGE_NOT_SUPPORTED = 21
TREE_SITTER_LANGUAGE_LOAD_FAILED = 22
TREE_SITTER_NOT_INITIALIZED = 23

# Parser errors (maintain granularity)
PARSER_INITIALIZATION_FAILED = 30
PARSER_DOCUMENT_FAILED = 31
PARSER_NODE_LOOKUP_FAILED = 32

# Scope resolution errors (maintain granularity)
SCOPE_RESOLUTION_FAILED = 40
SCOPE_TYPE_INVALID = 41
REGEX_FALLBACK_FAILED = 42

# Guard processing errors (maintain granularity)
GUARD_TAG_PARSE_FAILED = 50
GUARD_SYNTAX_INVALID = 51
GUARD_PERMISSION_CONFLICT = 52

# System resource errors (maintain granularity)
INSUFFICIENT_MEMORY = 60
DISK_FULL = 61
THEME_LOAD_FAILED = 62

# Application errors (maintain granularity)
UNEXPECTED_ERROR = 70
DEPENDENCY_MISSING = 71
CONFIGURATION_ERROR = 72
WATCHDOG_MISSING = 73
WORKER_MANAGER_UNAVAILABLE = 74

# Network/external errors (maintain granularity)
NETWORK_ERROR = 80
EXTERNAL_TOOL_FAILED = 81
API_ERROR = 82
TIMEOUT_ERROR = 124  # Standard Unix timeout exit code

# Signal-based (Unix/Linux standard)
INTERRUPTED = 130  # Ctrl+C (128 + SIGINT=2)


def get_exit_code_description(code: int) -> str:
    """Get human-readable description for an exit code"""
    descriptions = {
        # Core success and standard errors
        SUCCESS: "Success",
        GENERAL_ERROR: "General error",
        USAGE_ERROR: "Invalid command arguments or usage",
        # Access and permission errors
        SECURITY_VIOLATION: "Security violation - access denied",
        PERMISSION_DENIED: "Permission denied",
        # Validation errors
        VALIDATION_FAILED: "Validation failed",
        INPUT_VALIDATION_FAILED: "Invalid input arguments",
        CONFIG_VALIDATION_FAILED: "Configuration validation failed",
        # File/Directory access errors
        FILE_NOT_FOUND: "File not found",
        DIRECTORY_NOT_FOUND: "Directory not found",
        DOCUMENT_READ_FAILED: "Failed to read document",
        DOCUMENT_ACCESS_DENIED: "Document access denied",
        DOCUMENT_FORMAT_INVALID: "Invalid document format",
        # Tree-sitter errors
        TREE_SITTER_NOT_INSTALLED: "Tree-sitter library not installed",
        TREE_SITTER_LANGUAGE_NOT_SUPPORTED: "Programming language not supported by tree-sitter",
        TREE_SITTER_LANGUAGE_LOAD_FAILED: "Failed to load tree-sitter language parser",
        TREE_SITTER_NOT_INITIALIZED: "Tree-sitter parser not initialized",
        # Parser errors
        PARSER_INITIALIZATION_FAILED: "Parser initialization failed",
        PARSER_DOCUMENT_FAILED: "Failed to parse document",
        PARSER_NODE_LOOKUP_FAILED: "Failed to lookup AST node",
        # Scope resolution errors
        SCOPE_RESOLUTION_FAILED: "Scope resolution failed",
        SCOPE_TYPE_INVALID: "Invalid scope type specified",
        REGEX_FALLBACK_FAILED: "Regex fallback parsing failed",
        # Guard processing errors
        GUARD_TAG_PARSE_FAILED: "Guard tag parsing failed",
        GUARD_SYNTAX_INVALID: "Invalid guard tag syntax",
        GUARD_PERMISSION_CONFLICT: "Guard permission conflict detected",
        # System resource errors
        INSUFFICIENT_MEMORY: "Insufficient memory",
        DISK_FULL: "Disk full",
        THEME_LOAD_FAILED: "Theme loading failed",
        # Application errors
        UNEXPECTED_ERROR: "Unexpected error occurred",
        DEPENDENCY_MISSING: "Required dependency missing",
        CONFIGURATION_ERROR: "Configuration error",
        WATCHDOG_MISSING: "Watchdog library required for file watching",
        WORKER_MANAGER_UNAVAILABLE: "Worker manager not available for remote execution",
        # Network/external errors
        NETWORK_ERROR: "Network error",
        EXTERNAL_TOOL_FAILED: "External tool failed",
        API_ERROR: "API error",
        TIMEOUT_ERROR: "Operation timed out",
        # Signal-based errors
        INTERRUPTED: "Interrupted by user (Ctrl+C)",
    }

    return descriptions.get(code, f"Unknown exit code: {code}")
