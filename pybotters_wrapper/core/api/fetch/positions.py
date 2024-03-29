from typing import Any, NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from ...typedefs import PositionItem, TEndpoint, TSymbol
from .fetch_api import FetchAPI
from .fetch_api_builder import FetchAPIBuilder


class PositionsFetchAPIResponse(NamedTuple):
    positions: list[PositionItem]
    resp: ClientResponse
    data: Any = None


class PositionsFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class PositionsFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class PositionsFetchAPIWrapResponseParameters(TypedDict):
    positions: list[PositionItem]
    resp: ClientResponse
    data: Any


class PositionsFetchAPI(
    FetchAPI[
        PositionsFetchAPIResponse,
        PositionsFetchAPIGenerateEndpointParameters,
        PositionsFetchAPITranslateParametersParameters,
        PositionsFetchAPIWrapResponseParameters,
    ]
):
    async def fetch_positions(
        self,
        symbol: TSymbol,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None
    ) -> PositionsFetchAPIResponse:
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
        return self._wrap_response({"positions": item, "resp": resp, "data": data})


class PositionsFetchAPIBuilder(
    FetchAPIBuilder[
        PositionsFetchAPI,
        PositionsFetchAPIGenerateEndpointParameters,
        PositionsFetchAPITranslateParametersParameters,
        PositionsFetchAPIWrapResponseParameters,
    ]
):
    def __init__(self):
        super(PositionsFetchAPIBuilder, self).__init__(
            PositionsFetchAPI, PositionsFetchAPIResponse
        )
