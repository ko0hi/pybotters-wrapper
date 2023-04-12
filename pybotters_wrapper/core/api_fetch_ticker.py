from typing import Any, Awaitable, Callable, NamedTuple, TypedDict

from aiohttp.client import ClientResponse

from pybotters_wrapper._typedefs import TEndpoint, TRequsetMethod, TSymbol

from .api_client import APIClient
from .api_fetch import FetchAPI
from .normalized_store_ticker import TickerItem


class TickerFetchAPIResponse(NamedTuple):
    ticker: TickerItem
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class TickerFetchAPIGenerateEndpointParameters(TypedDict):
    symbol: TSymbol
    extra_params: dict


class TickerFetchAPITranslateParametersParameters(TypedDict):
    endpoint: TEndpoint
    symbol: TSymbol
    extra_params: dict


class TickerFetchAPIWrapResponseParameters(TypedDict):
    item: TickerItem
    resp: ClientResponse
    resp_data: dict


class TickerFetchAPI(
    FetchAPI[
        TickerFetchAPIResponse,
        TickerFetchAPIGenerateEndpointParameters,
        TickerFetchAPITranslateParametersParameters,
        TickerFetchAPIWrapResponseParameters,
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
        response_itemizer: Callable[[ClientResponse, any], TickerItem] | None = None,
    ):
        super(TickerFetchAPI, self).__init__(
            api_client,
            method,
            endpoint_generator=endpoint_generator,
            parameter_translater=parameter_translater,
            response_wrapper_cls=TickerFetchAPIResponse,
            response_decoder=response_decoder,
        )
        self._response_itemizer = response_itemizer

    def _itemize_response(
        self, resp: ClientResponse, resp_data: Any | None = None
    ) -> TickerItem:
        assert self._response_itemizer is not None
        return self._response_itemizer(resp, resp_data)

    async def fetch_ticker(
        self, symbol: TSymbol, *, extra_params: dict = None, request_params: dict = None
    ) -> TickerFetchAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(
            TickerFetchAPIGenerateEndpointParameters(
                symbol=symbol, extra_params=extra_params
            )
        )
        parameters = self._translate_parameters(
            TickerFetchAPITranslateParametersParameters(
                endpoint=endpoint, symbol=symbol, extra_params=extra_params
            )
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        item = self._itemize_response(resp, resp_data)
        return self._wrap_response(
            TickerFetchAPIWrapResponseParameters(
                item=item, resp=resp, resp_data=resp_data
            )
        )
