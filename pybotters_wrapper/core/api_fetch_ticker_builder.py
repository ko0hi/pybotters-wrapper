from .api_fetch_ticker import (
    TickerFetchAPI,
    TickerFetchAPIResponse,
    TickerFetchAPIGenerateEndpointParameters,
    TickerFetchAPITranslateParametersParameters,
    TickerFetchAPIWrapResponseParameters,
)

from .api_fetch_builder import FetchAPIBuilder


class TickerFetchAPIBuilder(
    FetchAPIBuilder[
        TickerFetchAPIResponse,
        TickerFetchAPIGenerateEndpointParameters,
        TickerFetchAPITranslateParametersParameters,
        TickerFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(TickerFetchAPIBuilder, self).__init__(
            TickerFetchAPI, TickerFetchAPIResponse
        )
