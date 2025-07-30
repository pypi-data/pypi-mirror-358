"""
P2P-specific exceptions for the network manager.
"""

from ...core.error_handling import CodeGuardException


class P2PError(CodeGuardException):
    """Base exception for P2P network operations."""

    pass


class NetworkError(P2PError):
    """Network communication errors."""

    pass


class PathConflictError(P2PError):
    """Path ownership conflicts between nodes."""

    def __init__(self, path: str, existing_node: str, existing_address: str):
        self.path = path
        self.existing_node = existing_node
        self.existing_address = existing_address
        super().__init__(
            f"Path '{path}' is already managed by node '{existing_node}' at {existing_address}"
        )


class RegistrationError(P2PError):
    """Errors during node registration."""

    pass


class DiscoveryError(P2PError):
    """Errors during network discovery."""

    pass


class ConfigurationError(P2PError):
    """P2P configuration errors."""

    pass
