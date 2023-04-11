from .api_fetch_orderbook import (
    OrderbookFetchAPI,
    OrderbookFetchAPIResponse,
    OrderbookFetchAPIGenerateEndpointParameters,
    OrderbookFetchAPITranslateParametersParameters,
    OrderbookFetchAPIWrapResponseParameters,
)

from .api_fetch_builder import FetchAPIBuilder


class OrderbookFetchAPIBuilder(
    FetchAPIBuilder[
        OrderbookFetchAPIResponse,
        OrderbookFetchAPIGenerateEndpointParameters,
        OrderbookFetchAPITranslateParametersParameters,
        OrderbookFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(OrderbookFetchAPIBuilder, self).__init__(
            OrderbookFetchAPI, OrderbookFetchAPIResponse
        )
