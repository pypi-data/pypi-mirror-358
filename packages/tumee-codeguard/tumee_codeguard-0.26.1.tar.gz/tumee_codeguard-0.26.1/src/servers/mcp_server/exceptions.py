#!/usr/bin/env python3
"""
Exception hierarchy for MCP Server Test Framework

Provides structured exceptions with proper error context and categorization
for better error handling and debugging.
"""

from typing import Any, Dict, Optional


class MCPFrameworkError(Exception):
    """
    Base exception for all MCP framework errors.

    Provides structured error context and logging integration.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause

    def __str__(self) -> str:
        """Return a formatted error message."""
        parts = [self.message]

        if self.error_code:
            parts.append(f"(Code: {self.error_code})")

        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"[{context_str}]")

        if self.cause:
            parts.append(f"Caused by: {self.cause}")

        return " ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class MCPConfigurationError(MCPFrameworkError):
    """
    Raised when there are configuration validation or setup errors.

    Examples:
    - Invalid port ranges
    - Missing SSL certificates
    - Invalid environment settings
    - MCP transport configuration errors
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="MCP_CONFIG_ERROR", **kwargs)


class MCPStartupError(MCPFrameworkError):
    """
    Raised when MCP server fails to start properly.

    Examples:
    - Server process dies during startup
    - Port binding failures
    - SSL context creation errors
    - Transport initialization failures
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="MCP_STARTUP_ERROR", **kwargs)


class MCPTimeoutError(MCPFrameworkError):
    """
    Raised when operations timeout.

    Examples:
    - Server startup timeout
    - Client connection timeout
    - Request processing timeout
    - Shutdown timeout
    """

    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        context = kwargs.get("context", {})
        if timeout_duration is not None:
            context["timeout_duration"] = timeout_duration
        kwargs["context"] = context
        super().__init__(message, error_code="MCP_TIMEOUT_ERROR", **kwargs)


class MCPCleanupError(MCPFrameworkError):
    """
    Raised when resource cleanup fails.

    Examples:
    - Server process termination failures
    - Port release failures
    - SSL certificate cleanup errors
    - Transport cleanup failures
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="MCP_CLEANUP_ERROR", **kwargs)


class MCPConnectionError(MCPFrameworkError):
    """
    Raised when MCP connection or communication fails.

    Examples:
    - Failed to connect to MCP server
    - Client authentication failures
    - Transport-level errors
    - Network connectivity issues
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="MCP_CONNECTION_ERROR", **kwargs)


class MCPCertificateError(MCPFrameworkError):
    """
    Raised when SSL certificate operations fail.

    Examples:
    - Certificate generation failures
    - Invalid certificate format
    - Certificate validation errors
    - SSL context creation failures
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="MCP_CERTIFICATE_ERROR", **kwargs)


class MCPTransportError(MCPFrameworkError):
    """
    Raised when MCP transport layer encounters errors.

    Examples:
    - Network transport failures
    - STDIO transport errors
    - Message serialization failures
    - Protocol errors
    """

    def __init__(self, message: str, transport_type: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if transport_type:
            context["transport_type"] = transport_type
        kwargs["context"] = context
        super().__init__(message, error_code="MCP_TRANSPORT_ERROR", **kwargs)


class MCPToolError(MCPFrameworkError):
    """
    Raised when MCP tools encounter errors.

    Examples:
    - Tool registration failures
    - Tool execution errors
    - Tool parameter validation errors
    - Tool permission errors
    """

    def __init__(self, message: str, tool_name: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if tool_name:
            context["tool_name"] = tool_name
        kwargs["context"] = context
        super().__init__(message, error_code="MCP_TOOL_ERROR", **kwargs)


class MCPResourceError(MCPFrameworkError):
    """
    Raised when MCP resources encounter errors.

    Examples:
    - Resource loading failures
    - Resource access permission errors
    - Resource not found errors
    - Resource validation failures
    """

    def __init__(self, message: str, resource_uri: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if resource_uri:
            context["resource_uri"] = resource_uri
        kwargs["context"] = context
        super().__init__(message, error_code="MCP_RESOURCE_ERROR", **kwargs)


class MCPPromptError(MCPFrameworkError):
    """
    Raised when MCP prompts encounter errors.

    Examples:
    - Prompt template loading failures
    - Prompt parameter validation errors
    - Prompt execution errors
    - Prompt permission errors
    """

    def __init__(self, message: str, prompt_name: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if prompt_name:
            context["prompt_name"] = prompt_name
        kwargs["context"] = context
        super().__init__(message, error_code="MCP_PROMPT_ERROR", **kwargs)


class MCPTestExecutionError(MCPFrameworkError):
    """
    Raised when MCP test execution fails.

    Examples:
    - Test server startup failures
    - Test client connection failures
    - Test assertion failures
    - Test environment setup errors
    """

    def __init__(self, message: str, test_name: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if test_name:
            context["test_name"] = test_name
        kwargs["context"] = context
        super().__init__(message, error_code="MCP_TEST_ERROR", **kwargs)


# Convenience functions for creating exceptions with context


def create_startup_error(
    message: str,
    process_id: Optional[int] = None,
    exit_code: Optional[int] = None,
    output: Optional[str] = None,
    transport: Optional[str] = None,
) -> MCPStartupError:
    """Create an MCPStartupError with process context."""
    context = {}
    if process_id is not None:
        context["process_id"] = process_id
    if exit_code is not None:
        context["exit_code"] = exit_code
    if output:
        context["output"] = output[:500]  # Truncate long output
    if transport:
        context["transport"] = transport

    return MCPStartupError(message, context=context)


def create_timeout_error(
    message: str,
    operation: str,
    duration: float,
    expected_duration: Optional[float] = None,
    transport: Optional[str] = None,
) -> MCPTimeoutError:
    """Create an MCPTimeoutError with timing context."""
    context = {"operation": operation, "actual_duration": duration}
    if expected_duration is not None:
        context["expected_duration"] = expected_duration
    if transport:
        context["transport"] = transport

    return MCPTimeoutError(message, timeout_duration=duration, context=context)


def create_connection_error(
    message: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    transport: Optional[str] = None,
    original_error: Optional[Exception] = None,
) -> MCPConnectionError:
    """Create an MCPConnectionError with connection context."""
    context = {}
    if host:
        context["host"] = host
    if port is not None:
        context["port"] = port
    if transport:
        context["transport"] = transport

    return MCPConnectionError(message, context=context, cause=original_error)


def create_tool_error(
    message: str,
    tool_name: str,
    operation: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    original_error: Optional[Exception] = None,
) -> MCPToolError:
    """Create an MCPToolError with tool context."""
    context = {"tool_name": tool_name}
    if operation:
        context["operation"] = operation
    if parameters:
        # Sanitize parameters to avoid logging sensitive data
        safe_params = {
            k: v
            for k, v in parameters.items()
            if not any(
                sensitive in k.lower() for sensitive in ["password", "token", "key", "secret"]
            )
        }
        context["parameters"] = safe_params

    return MCPToolError(message, tool_name=tool_name, context=context, cause=original_error)


def create_transport_error(
    message: str,
    transport_type: str,
    operation: Optional[str] = None,
    message_data: Optional[Dict[str, Any]] = None,
    original_error: Optional[Exception] = None,
) -> MCPTransportError:
    """Create an MCPTransportError with transport context."""
    context = {"operation": operation} if operation else {}
    if message_data:
        # Sanitize message data
        context["message_type"] = message_data.get("method") or message_data.get("type")
        context["message_id"] = message_data.get("id")

    return MCPTransportError(
        message, transport_type=transport_type, context=context, cause=original_error
    )


# Exception handling utilities


def handle_subprocess_error(
    error: Exception,
    operation: str,
    command: Optional[list] = None,
    transport: Optional[str] = None,
) -> MCPFrameworkError:
    """
    Convert subprocess errors to appropriate MCP framework exceptions.

    Args:
        error: Original subprocess error
        operation: Description of the operation that failed
        command: Command that was executed (optional)
        transport: Transport type (optional)

    Returns:
        Appropriate MCPFrameworkError subclass
    """
    import subprocess

    context = {"operation": operation}
    if command:
        context["command"] = " ".join(str(c) for c in command)
    if transport:
        context["transport"] = transport

    if isinstance(error, subprocess.TimeoutExpired):
        return MCPTimeoutError(
            f"Operation '{operation}' timed out",
            timeout_duration=error.timeout,
            context=context,
            cause=error,
        )
    elif isinstance(error, subprocess.CalledProcessError):
        context["exit_code"] = error.returncode
        if error.output:
            context["output"] = error.output[:500]
        return MCPStartupError(
            f"Operation '{operation}' failed with exit code {error.returncode}",
            context=context,
            cause=error,
        )
    elif isinstance(error, (OSError, IOError)):
        return MCPConnectionError(
            f"System error during '{operation}': {error}", context=context, cause=error
        )
    else:
        return MCPFrameworkError(
            f"Unexpected error during '{operation}': {error}", context=context, cause=error
        )


def is_recoverable_error(error: Exception) -> bool:
    """
    Determine if an error is potentially recoverable.

    Args:
        error: Exception to check

    Returns:
        True if the error might be recoverable with retry
    """
    # Timeout errors might be recoverable
    if isinstance(error, MCPTimeoutError):
        return True

    # Connection errors might be recoverable
    if isinstance(error, MCPConnectionError):
        return True

    # Some startup errors might be recoverable (port conflicts, etc.)
    if isinstance(error, MCPStartupError):
        # Check if it's a port binding issue
        if "port" in str(error).lower() or "bind" in str(error).lower():
            return True

    # Transport errors might be recoverable
    if isinstance(error, MCPTransportError):
        return True

    # Configuration and certificate errors are usually not recoverable
    if isinstance(error, (MCPConfigurationError, MCPCertificateError)):
        return False

    return False


def categorize_mcp_error(error: Exception) -> str:
    """
    Categorize an MCP error for monitoring and alerting.

    Args:
        error: Exception to categorize

    Returns:
        Error category string
    """
    if isinstance(error, MCPConfigurationError):
        return "configuration"
    elif isinstance(error, MCPStartupError):
        return "startup"
    elif isinstance(error, MCPTimeoutError):
        return "timeout"
    elif isinstance(error, MCPConnectionError):
        return "connection"
    elif isinstance(error, MCPTransportError):
        return "transport"
    elif isinstance(error, (MCPToolError, MCPResourceError, MCPPromptError)):
        return "functionality"
    elif isinstance(error, MCPTestExecutionError):
        return "testing"
    else:
        return "unknown"
