from typing import Any, NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from ...typedefs import TEndpoint, TickerItem, TSymbol
from .fetch_api import FetchAPI
from .fetch_api_builder import FetchAPIBuilder


class TickerFetchAPIResponse(NamedTuple):
    ticker: TickerItem
    resp: ClientResponse
    data: Any | None = None


class TickerFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class TickerFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class TickerFetchAPIWrapResponseParameters(TypedDict):
    ticker: TickerItem
    resp: ClientResponse
    data: Any


class TickerFetchAPI(
    FetchAPI[
        TickerFetchAPIResponse,
        TickerFetchAPIGenerateEndpointParameters,
        TickerFetchAPITranslateParametersParameters,
        TickerFetchAPIWrapResponseParameters,
    ]
):
    async def fetch_ticker(
        self,
        symbol: TSymbol,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None
    ) -> TickerFetchAPIResponse:
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
        return self._wrap_response({"ticker": item, "resp": resp, "data": data})


class TickerFetchAPIBuilder(
    FetchAPIBuilder[
        TickerFetchAPI,
        TickerFetchAPIGenerateEndpointParameters,
        TickerFetchAPITranslateParametersParameters,
        TickerFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(TickerFetchAPIBuilder, self).__init__(
            TickerFetchAPI, TickerFetchAPIResponse
        )
