from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from ...typedefs import TEndpoint, TOrderbook, TSymbol
from .fetch_api import FetchAPI
from .fetch_api_builder import FetchAPIBuilder


class OrderbookFetchAPIResponse(NamedTuple):
    orderbook: TOrderbook
    resp: ClientResponse | None = None
    data: dict | None = None


class OrderbookFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class OrderbookFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class OrderbookFetchAPIWrapResponseParameters(TypedDict):
    orderbook: TOrderbook
    resp: ClientResponse
    data: dict


class OrderbookFetchAPI(
    FetchAPI[
        OrderbookFetchAPIResponse,
        OrderbookFetchAPIGenerateEndpointParameters,
        OrderbookFetchAPITranslateParametersParameters,
        OrderbookFetchAPIWrapResponseParameters,
    ]
):
    async def fetch_orderbook(
        self,
        symbol: TSymbol,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None
    ) -> OrderbookFetchAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            {"symbol": symbol, "extra_params": extra_params}
        )
        parameters = self._translate_parameters(
            {"endpoint": endpoint, "symbol": symbol, "extra_params": extra_params}
        )

        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        item = self._itemize_response(resp, data)
        assert isinstance(data, dict)
        return self._wrap_response({"orderbook": item, "resp": resp, "data": data})


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
