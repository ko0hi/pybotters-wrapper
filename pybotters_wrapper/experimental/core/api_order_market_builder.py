from . import OrderAPIBuilder

from .api_order_market import (
    MarketOrderAPI,
    MarketOrderAPIResponse,
    MarketOrderAPIGenerateEndpointParameters,
    MarketOrderAPITranslateParametersParameters,
    MarketOrderAPIWrapResponseParameters,
)


class MarketOrderAPIBuilder(
    OrderAPIBuilder[
        MarketOrderAPIGenerateEndpointParameters,
        MarketOrderAPITranslateParametersParameters,
        MarketOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(MarketOrderAPIBuilder, self).__init__(
            MarketOrderAPI, MarketOrderAPIResponse
        )
