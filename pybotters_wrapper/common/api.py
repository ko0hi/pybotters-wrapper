from typing import NamedTuple

import aiohttp
from loguru import logger

import pybotters
from pybotters_wrapper.utils import LoggingMixin


class OrderResponse(NamedTuple):
    id: str
    resp: aiohttp.ClientResponse
    resp_data: any = None

    @property
    def status(self):
        return self.resp.status


class API(LoggingMixin):
    BASE_URL = None
    _ORDER_ENDPOINT = None
    _MARKET_ENDPOINT = None
    _LIMIT_ENDPOINT = None
    _CANCEL_ENDPOINT = None
    _ORDER_ID_KEY = None
    _MARKET_REQUEST_METHOD = "POST"
    _LIMIT_REQUEST_METHOD = "POST"
    _CANCEL_REQUEST_METHOD = "DELETE"

    def __init__(self, client: pybotters.Client, verbose: bool = False, **kwargs):
        self._client = client
        self._verbose = verbose

    async def request(self, method, url, *, params=None, data=None, **kwargs):
        if url is None:
            raise RuntimeError(f"null endpoint")

        url = self._attach_base_url(url)
        return await self._client.request(
            method, url, params=params, data=data, **kwargs
        )

    async def get(self, url, *, params=None, **kwargs):
        return await self.request("GET", url, params=params, data=None, **kwargs)

    async def post(self, url, *, data=None, **kwargs):
        return await self.request("POST", url, params=None, data=data, **kwargs)

    async def put(self, url, *, data=None, **kwargs):
        return await self._client.request("PUT", url, params=None, data=data, **kwargs)

    async def delete(self, url, *, data=None, **kwargs):
        return await self._client.request(
            "DELETE", url, params=None, data=data, **kwargs
        )

    @logger.catch
    async def market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        request_params = request_params or {}
        endpoint = self._make_market_endpoint(symbol, side, size, **kwargs)
        p = self._make_market_order_parameter(endpoint, symbol, side, size)
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"market order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_market_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(f"market order response: {resp} {resp_data}", verbose=self._verbose)
        order_id = self._make_market_order_id(resp, resp_data, p, order_id_key)
        wrapped_resp = self._make_market_order_response(resp, resp_data, order_id)
        return wrapped_resp

    @logger.catch
    async def limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        request_params = request_params or {}
        endpoint = self._make_limit_endpoint(symbol, side, price, size, **kwargs)
        p = self._make_limit_order_parameter(endpoint, symbol, side, price, size)
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"limit order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_limit_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(f"limit order response: {resp} {resp_data}", verbose=self._verbose)
        order_id = self._make_limit_order_id(resp, resp_data, p, order_id_key)
        wrapped_resp = self._make_limit_order_response(resp, resp_data, order_id)
        return wrapped_resp

    @logger.catch
    async def cancel_order(
        self,
        symbol: str,
        order_id: str,
        request_params: dict = None,
        **kwargs,
    ) -> "CancelResponse":
        request_params = request_params or {}
        endpoint = self._make_cancel_endpoint(symbol, order_id, **kwargs)
        p = self._make_cancel_order_parameter(endpoint, symbol, order_id)
        p_w_kwargs = self._add_kwargs_to_data(p, **kwargs)
        self.log(f"cancel order request: {p_w_kwargs}", verbose=self._verbose)
        resp, resp_data = await self._make_cancel_request(
            endpoint, p_w_kwargs, **request_params
        )
        self.log(f"cancel order response: {resp} {resp_data}", verbose=self._verbose)
        wrapped_resp = self._make_cancel_order_response(resp, resp_data, order_id)
        return wrapped_resp

    def _attach_base_url(self, url) -> str:
        return url if self._client._base_url else self.BASE_URL + url

    def _make_market_endpoint(
        self, symbol: str, side: str, size: float, **kwargs
    ) -> str:
        return self._MARKET_ENDPOINT or self._ORDER_ENDPOINT

    def _make_limit_endpoint(
        self, symbol: str, side: str, price: float, size: float, **kwargs
    ) -> str:
        return self._LIMIT_ENDPOINT or self._ORDER_ENDPOINT

    def _make_cancel_endpoint(self, symbol: str, order_id: str, **kwargs) -> str:
        return self._CANCEL_ENDPOINT or self._ORDER_ENDPOINT

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: str, size: float
    ) -> dict | None:
        raise NotImplementedError

    def _make_limit_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
    ) -> dict | None:
        raise NotImplementedError

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict | None:
        raise NotImplementedError

    def _make_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        order_id_key: str,
    ) -> str | None:
        if resp.status == 200:
            order_id = resp_data
            order_id_key = order_id_key or self._ORDER_ID_KEY
            assert order_id_key is not None
            for k in order_id_key.split("."):
                order_id = order_id[k]
            return str(order_id)
        else:
            self.log(f"order failed: {resp} {resp_data}", "error")
            return None

    def _make_market_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        order_id_key: str,
    ) -> str:
        return self._make_order_id(resp, resp_data, data, order_id_key)

    def _make_limit_order_id(
        self,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
        data: dict,
        order_id_key: str,
    ) -> str:
        return self._make_order_id(resp, resp_data, data, order_id_key)

    async def _make_request(
        self, method: str, endpoint: str, params_or_data: dict | None, **kwargs
    ):
        params = {"method": method, "url": endpoint}
        if method == "GET":
            params["params"] = params_or_data
        else:
            params["data"] = params_or_data

        params.update(kwargs)

        resp = await self.request(**params)
        resp_data = await resp.json()
        return resp, resp_data

    async def _make_market_request(
        self, endpoint: str, params_or_data=dict | None, **kwargs
    ):
        return await self._make_request(
            self._MARKET_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    async def _make_limit_request(
        self, endpoint: str, params_or_data=dict | None, **kwargs
    ):
        return await self._make_request(
            self._LIMIT_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    async def _make_cancel_request(
        self, endpoint: str, params_or_data=dict | None, **kwargs
    ):
        return await self._make_request(
            self._CANCEL_REQUEST_METHOD, endpoint, params_or_data, **kwargs
        )

    def _make_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return OrderResponse(order_id, resp, resp_data)

    def _make_market_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    def _make_limit_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict, order_id: str
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    def _make_cancel_order_response(
        self,
        resp: aiohttp.ClientResponse,
        resp_data: dict,
        order_id: str,
    ) -> "OrderResponse":
        return self._make_order_response(resp, resp_data, order_id)

    def _add_kwargs_to_data(self, data: dict | None, **kwargs):
        data = data or {}
        return {**data, **kwargs}
