from . import OrderAPIBuilder

from .api_order_limit import (
    LimitOrderAPI,
    LimitOrderAPIResponse,
    LimitOrderAPIGenerateEndpointParameters,
    LimitOrderAPITranslateParametersParameters,
    LimitOrderAPIWrapResponseParameters,
)


class LimitOrderAPIBuilder(
    OrderAPIBuilder[
        LimitOrderAPIGenerateEndpointParameters,
        LimitOrderAPITranslateParametersParameters,
        LimitOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(LimitOrderAPIBuilder, self).__init__(LimitOrderAPI, LimitOrderAPIResponse)
