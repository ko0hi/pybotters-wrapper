from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from . import FetchAPI
from .normalized_store_orderbook import OrderbookItem
from .._typedefs import TEndpoint, TSide, TSymbol


class OrderbookFetchAPIResponse(NamedTuple):
    orderbook: dict[TSide, list[OrderbookItem]]
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
    orderbook: dict[TSide, list[OrderbookItem]]
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
            self, symbol: TSymbol, *, extra_params: dict = None,
            request_params: dict = None
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
        data = await self._decode_response(resp)
        item = self._itemize_response(resp, data)
        return self._wrap_response(
            OrderbookFetchAPIWrapResponseParameters(
                orderbook=item, resp=resp, data=data
            )
        )
