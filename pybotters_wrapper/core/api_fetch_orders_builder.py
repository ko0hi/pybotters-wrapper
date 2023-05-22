from .api_fetch_builder import FetchAPIBuilder
from .api_fetch_orders import (
    OrdersFetchAPI,
    OrdersFetchAPIResponse,
    OrdersFetchAPIGenerateEndpointParameters,
    OrdersFetchAPITranslateParametersParameters,
    OrdersFetchAPIWrapResponseParameters,
)


class OrdersFetchAPIBuilder(
    FetchAPIBuilder[
        OrdersFetchAPI,
        OrdersFetchAPIGenerateEndpointParameters,
        OrdersFetchAPITranslateParametersParameters,
        OrdersFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(OrdersFetchAPIBuilder, self).__init__(
            OrdersFetchAPI, OrdersFetchAPIResponse
        )
