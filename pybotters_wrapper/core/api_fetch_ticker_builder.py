from .api_fetch_builder import FetchAPIBuilder
from .api_fetch_ticker import (
    TickerFetchAPI,
    TickerFetchAPIResponse,
    TickerFetchAPIGenerateEndpointParameters,
    TickerFetchAPITranslateParametersParameters,
    TickerFetchAPIWrapResponseParameters,
)


class TickerFetchAPIBuilder(
    FetchAPIBuilder[
        TickerFetchAPI,
        TickerFetchAPIGenerateEndpointParameters,
        TickerFetchAPITranslateParametersParameters,
        TickerFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(TickerFetchAPIBuilder, self).__init__(
            TickerFetchAPI, TickerFetchAPIResponse
        )
