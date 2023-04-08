from . import OrderAPIBuilder

from .api_order_cancel import (
    CancelOrderAPI,
    CancelOrderAPIResponse,
    CancelOrderAPIGenerateEndpointParameters,
    CancelOrderAPITranslateParametersParameters,
    CancelOrderAPIWrapResponseParameters,
)


class CancelOrderAPIBuilder(
    OrderAPIBuilder[
        CancelOrderAPI,
        CancelOrderAPIGenerateEndpointParameters,
        CancelOrderAPITranslateParametersParameters,
        CancelOrderAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(CancelOrderAPIBuilder, self).__init__(
            CancelOrderAPI, CancelOrderAPIResponse
        )
