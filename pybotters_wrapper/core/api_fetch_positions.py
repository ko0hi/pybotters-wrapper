from typing import Any, Awaitable, Callable, NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from .._typedefs import TEndpoint, TRequsetMethod, TSymbol
from .api_client import APIClient
from .api_fetch import FetchAPI
from .normalized_store_position import PositionItem


class PositionsFetchAPIResponse(NamedTuple):
    positions: list[PositionItem]
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class PositionsFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class PositionsFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class PositionsFetchAPIWrapResponseParameters(TypedDict):
    item: list[PositionItem]
    resp: ClientResponse
    resp_data: dict


class PositionsFetchAPI(
    FetchAPI[
        PositionsFetchAPIResponse,
        PositionsFetchAPIGenerateEndpointParameters,
        PositionsFetchAPITranslateParametersParameters,
        PositionsFetchAPIWrapResponseParameters,
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
        response_itemizer: Callable[[ClientResponse, any], list[PositionItem]]
        | None = None,
    ):
        super(PositionsFetchAPI, self).__init__(
            api_client,
            method,
            endpoint_generator=endpoint_generator,
            parameter_translater=parameter_translater,
            response_wrapper_cls=PositionsFetchAPIResponse,
            response_decoder=response_decoder,
        )
        self._response_itemizer = response_itemizer

    def _itemize_response(
        self, resp: ClientResponse, resp_data: Any | None = None
    ) -> list[PositionItem]:
        assert self._response_itemizer is not None
        return self._response_itemizer(resp, resp_data)

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
        resp_data = await self._decode_response(resp)
        item = self._itemize_response(resp, resp_data)
        return self._wrap_response(
            PositionsFetchAPIWrapResponseParameters(
                item=item, resp=resp, resp_data=resp_data
            )
        )
