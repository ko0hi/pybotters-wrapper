from typing import NamedTuple, Callable, Awaitable, TypedDict

from aiohttp.client import ClientResponse

from . import PositionItem, FetchAPI, APIClient
from .._typedefs import TEndpoint, TSymbol, TRequsetMethod


class PositionFetchAPIResponse(NamedTuple):
    positions: list[PositionItem]
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class PositionFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class PositionFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class PositionFetchAPIWrapResponseParameters(TypedDict):
    item: list[PositionItem]
    resp: ClientResponse
    resp_data: dict


class PositionFetchAPI(
    FetchAPI[
        PositionFetchAPIResponse,
        PositionFetchAPIGenerateEndpointParameters,
        PositionFetchAPITranslateParametersParameters,
        PositionFetchAPIWrapResponseParameters,
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
        super(PositionFetchAPI, self).__init__(
            api_client,
            method,
            endpoint_generator=endpoint_generator,
            parameters_translater=parameter_translater,
            response_wrapper_cls=PositionFetchAPIResponse,
            response_decoder=response_decoder,
        )
        self._response_itemizer = response_itemizer

    def _itemize_response(
        self, resp: ClientResponse, resp_data: any | None = None
    ) -> list[PositionItem]:
        assert self._response_itemizer is not None
        return self._response_itemizer(resp, resp_data)

    def fetch_positions(
        self, symbol: TSymbol, *, extra_params: dict = None, request_params: dict = None
    ) -> PositionFetchAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            PositionFetchAPIGenerateEndpointParameters(
                symbol=symbol, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            PositionFetchAPITranslateParametersParameters(
                endpoint=endpoint, symbol=symbol, extra_params=extra_params
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        item = self._itemize_response(resp, resp_data)
        return self._wrap_response(
            PositionFetchAPIWrapResponseParameters(
                item=item, resp=resp, resp_data=resp_data
            )
        )
