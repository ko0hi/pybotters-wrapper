from . import OrderAPIBuilder

from .api_order_stop_market import (
    StopMarketOrderAPI,
    StopMarketOrderAPIResponse,
    StopMarketOrderAPIGenerateEndpointParameters,
    StopMarketOrderAPITranslateParametersParameters,
    StopMarketOrderAPIWrapResponseParameters,
)


class StopMarketOrderAPIBuilder(
    OrderAPIBuilder[
        StopMarketOrderAPIGenerateEndpointParameters,
        StopMarketOrderAPITranslateParametersParameters,
        StopMarketOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(StopMarketOrderAPIBuilder, self).__init__(
            StopMarketOrderAPI, StopMarketOrderAPIResponse
        )
