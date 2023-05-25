from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .fetch_api import FetchAPI
from .fetch_api_builder import FetchAPIBuilder
from ...typedefs import OrderItem, TEndpoint


class OrdersFetchAPIResponse(NamedTuple):
    orders: list[OrderItem]
    resp: ClientResponse | None = None
    data: dict | None = None


class OrdersFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: str
    extra_params: dict


class OrdersFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: str
    extra_params: dict


class OrdersFetchAPIWrapResponseParameters(TypedDict):
    orders: list[OrderItem]
    resp: ClientResponse
    data: dict


class OrdersFetchAPI(
    FetchAPI[
        OrdersFetchAPIResponse,
        OrdersFetchAPIGenerateEndpointParameters,
        OrdersFetchAPITranslateParametersParameters,
        OrdersFetchAPIWrapResponseParameters,
    ]
):
    async def fetch_orders(
        self, symbol: str, *, extra_params: dict = None, request_params: dict = None
    ) -> OrdersFetchAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            OrdersFetchAPIGenerateEndpointParameters(symbol=symbol)
        )
        parameters = self._translate_parameters(
            OrdersFetchAPITranslateParametersParameters(
                endpoint=endpoint, symbol=symbol, extra_params=extra_params
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        item = self._itemize_response(resp, data)
        return self._wrap_response(
            OrdersFetchAPIWrapResponseParameters(orders=item, resp=resp, data=data)
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
