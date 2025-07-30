#!/usr/bin/env python3
"""
Exception hierarchy for LLM Proxy Test Framework

Provides structured exceptions with proper error context and categorization
for better error handling and debugging.
"""

from typing import Any, Dict, Optional


class ProxyFrameworkError(Exception):
    """
    Base exception for all proxy framework errors.

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


class ConfigurationError(ProxyFrameworkError):
    """
    Raised when there are configuration validation or setup errors.

    Examples:
    - Invalid port ranges
    - Missing SSL certificates
    - Invalid environment settings
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)


class ProxyStartupError(ProxyFrameworkError):
    """
    Raised when proxy process fails to start properly.

    Examples:
    - Process dies during startup
    - Port binding failures
    - SSL context creation errors
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="STARTUP_ERROR", **kwargs)


class ProxyTimeoutError(ProxyFrameworkError):
    """
    Raised when operations timeout.

    Examples:
    - Proxy startup timeout
    - Command execution timeout
    - Shutdown timeout
    """

    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        context = kwargs.get("context", {})
        if timeout_duration is not None:
            context["timeout_duration"] = timeout_duration
        kwargs["context"] = context
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)


class ProxyCleanupError(ProxyFrameworkError):
    """
    Raised when resource cleanup fails.

    Examples:
    - Process termination failures
    - Port release failures
    - File cleanup errors
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CLEANUP_ERROR", **kwargs)


class ProxyConnectionError(ProxyFrameworkError):
    """
    Raised when proxy connection or communication fails.

    Examples:
    - Failed to connect to proxy
    - HTTPS tunnel establishment failed
    - SSL handshake errors
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CONNECTION_ERROR", **kwargs)


class CertificateError(ProxyFrameworkError):
    """
    Raised when SSL certificate operations fail.

    Examples:
    - Certificate generation failures
    - Invalid certificate format
    - Certificate validation errors
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CERTIFICATE_ERROR", **kwargs)


class PluginError(ProxyFrameworkError):
    """
    Raised when proxy plugins encounter errors.

    Examples:
    - Plugin loading failures
    - Plugin execution errors
    - Plugin configuration errors
    """

    def __init__(self, message: str, plugin_name: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if plugin_name:
            context["plugin_name"] = plugin_name
        kwargs["context"] = context
        super().__init__(message, error_code="PLUGIN_ERROR", **kwargs)


class TestExecutionError(ProxyFrameworkError):
    """
    Raised when test execution fails.

    Examples:
    - Test command failures
    - Assertion failures
    - Test environment setup errors
    """

    def __init__(self, message: str, test_name: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if test_name:
            context["test_name"] = test_name
        kwargs["context"] = context
        super().__init__(message, error_code="TEST_ERROR", **kwargs)


class InterceptionError(ProxyFrameworkError):
    """
    Raised when traffic interception fails.

    Examples:
    - Failed to intercept LLM traffic
    - Request/response parsing errors
    - Traffic modification failures
    """

    def __init__(self, message: str, domain: Optional[str] = None, **kwargs):
        context = kwargs.get("context", {})
        if domain:
            context["domain"] = domain
        kwargs["context"] = context
        super().__init__(message, error_code="INTERCEPTION_ERROR", **kwargs)


# Convenience functions for creating exceptions with context


def create_startup_error(
    message: str,
    process_id: Optional[int] = None,
    exit_code: Optional[int] = None,
    output: Optional[str] = None,
) -> ProxyStartupError:
    """Create a ProxyStartupError with process context."""
    context = {}
    if process_id is not None:
        context["process_id"] = process_id
    if exit_code is not None:
        context["exit_code"] = exit_code
    if output:
        context["output"] = output[:500]  # Truncate long output

    return ProxyStartupError(message, context=context)


def create_timeout_error(
    message: str, operation: str, duration: float, expected_duration: Optional[float] = None
) -> ProxyTimeoutError:
    """Create a ProxyTimeoutError with timing context."""
    context = {"operation": operation, "actual_duration": duration}
    if expected_duration is not None:
        context["expected_duration"] = expected_duration

    return ProxyTimeoutError(message, timeout_duration=duration, context=context)


def create_plugin_error(
    message: str,
    plugin_name: str,
    method_name: Optional[str] = None,
    original_error: Optional[Exception] = None,
) -> PluginError:
    """Create a PluginError with plugin context."""
    context = {"plugin_name": plugin_name}
    if method_name:
        context["method_name"] = method_name

    return PluginError(message, plugin_name=plugin_name, context=context, cause=original_error)


def create_interception_error(
    message: str, domain: str, request_path: Optional[str] = None, error_phase: Optional[str] = None
) -> InterceptionError:
    """Create an InterceptionError with request context."""
    context = {"domain": domain}
    if request_path:
        context["request_path"] = request_path
    if error_phase:
        context["error_phase"] = error_phase

    return InterceptionError(message, domain=domain, context=context)


# Exception handling utilities


def handle_subprocess_error(
    error: Exception, operation: str, command: Optional[list] = None
) -> ProxyFrameworkError:
    """
    Convert subprocess errors to appropriate framework exceptions.

    Args:
        error: Original subprocess error
        operation: Description of the operation that failed
        command: Command that was executed (optional)

    Returns:
        Appropriate ProxyFrameworkError subclass
    """
    import subprocess

    context = {"operation": operation}
    if command:
        context["command"] = " ".join(str(c) for c in command)

    if isinstance(error, subprocess.TimeoutExpired):
        return ProxyTimeoutError(
            f"Operation '{operation}' timed out",
            timeout_duration=error.timeout,
            context=context,
            cause=error,
        )
    elif isinstance(error, subprocess.CalledProcessError):
        context["exit_code"] = error.returncode
        if error.output:
            context["output"] = error.output[:500]
        return ProxyStartupError(
            f"Operation '{operation}' failed with exit code {error.returncode}",
            context=context,
            cause=error,
        )
    elif isinstance(error, (OSError, IOError)):
        return ProxyConnectionError(
            f"System error during '{operation}': {error}", context=context, cause=error
        )
    else:
        return ProxyFrameworkError(
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
    if isinstance(error, ProxyTimeoutError):
        return True

    # Connection errors might be recoverable
    if isinstance(error, ProxyConnectionError):
        return True

    # Some startup errors might be recoverable (port conflicts, etc.)
    if isinstance(error, ProxyStartupError):
        # Check if it's a port binding issue
        if "port" in str(error).lower() or "bind" in str(error).lower():
            return True

    # Configuration and certificate errors are usually not recoverable
    if isinstance(error, (ConfigurationError, CertificateError)):
        return False

    return False
