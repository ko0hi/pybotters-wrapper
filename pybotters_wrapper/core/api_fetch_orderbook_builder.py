from .api_fetch_builder import FetchAPIBuilder
from .api_fetch_orderbook import (
    OrderbookFetchAPI,
    OrderbookFetchAPIResponse,
    OrderbookFetchAPIGenerateEndpointParameters,
    OrderbookFetchAPITranslateParametersParameters,
    OrderbookFetchAPIWrapResponseParameters,
)


class OrderbookFetchAPIBuilder(
    FetchAPIBuilder[
        OrderbookFetchAPI,
        OrderbookFetchAPIGenerateEndpointParameters,
        OrderbookFetchAPITranslateParametersParameters,
        OrderbookFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(OrderbookFetchAPIBuilder, self).__init__(
            OrderbookFetchAPI, OrderbookFetchAPIResponse
        )
