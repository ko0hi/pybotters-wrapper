from typing import NamedTuple, Callable, Awaitable

from aiohttp.client import ClientResponse

from . import OrderItem, FetchAPI, APIClient
from .._typedefs import TEndpoint, TSymbol, TRequsetMethod


class FetchOrderResponse(NamedTuple):
    orders: list[OrderItem]
    resp: ClientResponse | None = None
    resp_data: dict | None = None


class OrdersFetchAPI(FetchAPI):
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        endpoint: TEndpoint | Callable[[TSymbol, dict], str] | None = None,
        parameter_translater: Callable[[TEndpoint, TSymbol, dict], dict] | None = None,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
        response_converter: Callable[[ClientResponse, any], OrderItem] | None = None,
    ):
        super(OrdersFetchAPI, self).__init__(
            api_client, method, response_decoder=response_decoder
        )
        self._endpoint = endpoint
        self._parameter_translater = parameter_translater
        self._response_converter = response_converter

    def _generate_endpoint(self, symbol: TSymbol, extra_params: dict) -> TEndpoint:
        assert self._endpoint is not None
        if isinstance(self._endpoint, str):
            return self._endpoint
        elif callable(self._endpoint):
            return self._endpoint(symbol)

    def _translate_parameters(
        self, endpoint: TEndpoint, symbol: TSymbol, extra_params: dict
    ) -> dict:
        assert self._parameter_translater is not None
        return self._parameter_translater(endpoint, symbol, extra_params)

    def _convert_response(
        self, resp: ClientResponse, resp_data: any | None = None
    ) -> OrderItem:
        assert self._response_converter is not None
        return self._response_converter(resp, resp_data)

    def fetch_order(
        self, symbol: TSymbol, *, extra_params: dict = None, request_params: dict = None
    ) -> FetchOrderResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(symbol, extra_params)
        parameters = self._translate_parameters(endpoint, symbol, extra_params)
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        item = self._convert_response(resp, resp_data)
        return FetchOrderResponse(item, resp, resp_data)
