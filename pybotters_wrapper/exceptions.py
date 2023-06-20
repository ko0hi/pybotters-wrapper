class PybottersWrapperError(Exception):
    ...


class FetchPrecisionsError(PybottersWrapperError):
    """Raised when an error occurred while fetching precisions."""
