class PybottersWrapperError(Exception):
    ...


class FetchPrecisionsError(PybottersWrapperError):
    """Raised when an error occurred while fetching precisions."""


class RequestError(PybottersWrapperError):
    """Raised when an error occurred while requesting."""
