"""
Component-specific exceptions.
"""


class ComponentError(Exception):
    """Base exception for component-related errors."""

    pass


class ComponentNotFoundError(ComponentError):
    """Raised when a requested component is not found."""

    pass


class ComponentParameterError(ComponentError):
    """Raised when component parameters are invalid."""

    pass


class ComponentRegistrationError(ComponentError):
    """Raised when component registration fails."""

    pass
