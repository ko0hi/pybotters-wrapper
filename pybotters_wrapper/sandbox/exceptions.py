from ..exceptions import PybottersWrapperError


class SandboxError(PybottersWrapperError):
    """Base class for exceptions in this module."""


class OrderNotFoundError(SandboxError):
    """Raised when order is not found."""
