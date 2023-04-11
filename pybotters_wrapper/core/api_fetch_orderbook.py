from typing import NamedTuple, Callable, Awaitable, TypedDict, Any

from aiohttp.client import ClientResponse

from . import FetchAPI, APIClient
from .normalized_store_orderbook import OrderbookItem
from .._typedefs import TEndpoint, TSymbol, TSide, TRequsetMethod


class OrderbookFetchAPIResponse(NamedTuple):
    orderbook: dict[TSide, list[OrderbookItem]]
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class OrderbookFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class OrderbookFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class OrderbookFetchAPIWrapResponseParameters(TypedDict):
    item: dict[TSide, list[OrderbookItem]]
    resp: ClientResponse
    resp_data: dict


class OrderbookFetchAPI(
    FetchAPI[
        OrderbookFetchAPIResponse,
        OrderbookFetchAPIGenerateEndpointParameters,
        OrderbookFetchAPITranslateParametersParameters,
        OrderbookFetchAPIWrapResponseParameters,
    ]
):
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        endpoint_generator: TEndpoint | Callable[[TSymbol, dict], str] | None = None,
        parameter_translater: Callable[[TEndpoint, TSymbol, dict], dict] | None = None,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
        response_itemizer: Callable[
            [ClientResponse, any], dict[TSide, list[OrderbookItem]]
        ]
        | None = None,
    ):
        super(OrderbookFetchAPI, self).__init__(
            api_client,
            method,
            endpoint_generator=endpoint_generator,
            parameters_translater=parameter_translater,
            response_wrapper_cls=OrderbookFetchAPIResponse,
            response_decoder=response_decoder,
        )
        self._response_itemizer = response_itemizer

    def _itemize_response(
        self, resp: ClientResponse, resp_data: Any | None = None
    ) -> dict[TSide, list[OrderbookItem]]:
        assert self._response_itemizer is not None
        return self._response_itemizer(resp, resp_data)

    async def fetch_orderbook(
        self, symbol: TSymbol, *, extra_params: dict = None, request_params: dict = None
    ) -> OrderbookFetchAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            OrderbookFetchAPIGenerateEndpointParameters(
                symbol=symbol, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            OrderbookFetchAPITranslateParametersParameters(
                endpoint=endpoint, symbol=symbol, extra_params=extra_params
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        item = self._itemize_response(resp, resp_data)
        return self._wrap_response(
            OrderbookFetchAPIWrapResponseParameters(
                item=item, resp=resp, resp_data=resp_data
            )
        )
