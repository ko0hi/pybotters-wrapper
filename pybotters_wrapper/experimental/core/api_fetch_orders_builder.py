from .api_fetch_orders import (
    OrdersFetchAPI,
    OrdersFetchAPIResponse,
    OrdersFetchAPIGenerateEndpointParameters,
    OrdersFetchAPITranslateParametersParameters,
    OrdersFetchAPIWrapResponseParameters,
)


from .api_fetch_builder import FetchAPIBuilder


class OrdersFetchAPIBuilder(
    FetchAPIBuilder[
        OrdersFetchAPIResponse,
        OrdersFetchAPIGenerateEndpointParameters,
        OrdersFetchAPITranslateParametersParameters,
        OrdersFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(OrdersFetchAPIBuilder, self).__init__(
            OrdersFetchAPI, OrdersFetchAPIResponse
        )
