from typing import NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .api_fetch import FetchAPI
from .normalized_store_position import PositionItem
from .._typedefs import TEndpoint, TSymbol


class PositionsFetchAPIResponse(NamedTuple):
    positions: list[PositionItem]
    resp: ClientResponse | None = None
    data: dict | None = None


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
    data: dict


class PositionsFetchAPI(
    FetchAPI[
        PositionsFetchAPIResponse,
        PositionsFetchAPIGenerateEndpointParameters,
        PositionsFetchAPITranslateParametersParameters,
        PositionsFetchAPIWrapResponseParameters,
    ]
):
    async def fetch_positions(
        self, symbol: TSymbol, *, extra_params: dict = None, request_params: dict = None
    ) -> PositionsFetchAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            PositionsFetchAPIGenerateEndpointParameters(
                symbol=symbol, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            PositionsFetchAPITranslateParametersParameters(
                endpoint=endpoint, symbol=symbol, extra_params=extra_params
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        data = await self._decode_response(resp)
        item = self._itemize_response(resp, data)
        return self._wrap_response(
            PositionsFetchAPIWrapResponseParameters(
                positions=item, resp=resp, data=data
            )
        )
