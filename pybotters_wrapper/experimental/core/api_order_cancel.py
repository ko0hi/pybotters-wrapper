import asyncio
from typing import Callable, Awaitable

from aiohttp.client import ClientResponse

from .api_client import APIClient
from .api_order import OrderAPI, OrderAPIResponse
from .._typedefs import TEndpoint, TOrderId, TSymbol, TRequsetMethod


class CancelOrderAPI(OrderAPI):
    def __init__(
        self,
        api_client: APIClient,
        method: TRequsetMethod,
        order_id_key: str,
        endpoint: TEndpoint | Callable[[TSymbol, TOrderId, dict], str] | None = None,
        parameter_translater: Callable[[TEndpoint, TSymbol, TOrderId, dict], dict]
                              | None = None,
        order_id_extractor: Callable[[ClientResponse, dict, str], str | None]
        | None = None,
        response_decoder: Callable[
            [ClientResponse], dict | list | Awaitable[dict | list]
        ]
        | None = None,
    ):
        super(CancelOrderAPI, self).__init__(
            api_client,
            method,
            order_id_key=order_id_key,
            order_id_extractor=order_id_extractor,
            response_decoder=response_decoder
        )
        self._endpoint = endpoint
        self._parameter_translater = parameter_translater

    def _generate_endpoint(
        self,
        symbol: TSymbol,
        order_id: TOrderId,
        extra_params: dict,
    ) -> TEndpoint:
        assert self._endpoint is not None
        if isinstance(self._endpoint, str):
            return self._endpoint
        elif callable(self._endpoint):
            return self._endpoint(symbol, order_id, extra_params)

    def _translate_parameters(
        self,
        endpoint: TEndpoint,
        symbol: TSymbol,
        order_id: TOrderId,
        extra_params: dict,
    ) -> dict:
        assert self._parameter_translater is not None
        return self._parameter_translater(endpoint, symbol, order_id, extra_params)

    async def cancel_order(
        self,
        symbol: TSymbol,
        order_id: TOrderId,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> OrderAPIResponse:
        extra_params = extra_params or {}
        request_params = request_params or {}
        endpoint = self._generate_endpoint(symbol, order_id, extra_params)
        parameters = self._translate_parameters(
            endpoint, symbol, order_id, extra_params
        )
        parameters = {**parameters, **extra_params}
        resp = await self.request(endpoint, parameters, **request_params)
        resp_data = await self._decode_response(resp)
        order_id = self._extract_order_id(resp, resp_data)
        return self._wrap_response(order_id, resp, resp_data)
