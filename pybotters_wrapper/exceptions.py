class PybottersWrapperError(Exception):
    ...


class FetchPrecisionsError(PybottersWrapperError):
    """Raised when an error occurred while fetching precisions."""


class RequestError(PybottersWrapperError):
    """Raised when an error occurred while requesting."""


class UnsupportedStoreError(PybottersWrapperError):
    """Raised when an unsupported operation is attempted."""
