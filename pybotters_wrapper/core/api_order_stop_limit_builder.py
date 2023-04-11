from . import OrderAPIBuilder

from .api_order_stop_limit import (
    StopLimitOrderAPI,
    StopLimitOrderAPIResponse,
    StopLimitOrderAPIGenerateEndpointParameters,
    StopLimitOrderAPITranslateParametersParameters,
    StopLimitOrderAPIWrapResponseParameters,
)


class StopLimitOrderAPIBuilder(
    OrderAPIBuilder[
        StopLimitOrderAPI,
        StopLimitOrderAPIGenerateEndpointParameters,
        StopLimitOrderAPITranslateParametersParameters,
        StopLimitOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(StopLimitOrderAPIBuilder, self).__init__(
            StopLimitOrderAPI, StopLimitOrderAPIResponse
        )
