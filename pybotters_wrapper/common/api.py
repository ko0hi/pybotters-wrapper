from typing import NamedTuple

import aiohttp
import pybotters


class OrderResponse(NamedTuple):
    id: str
    resp: aiohttp.ClientResponse
    info: any = None

    @property
    def status(self):
        return self.resp.status


class CancelResponse(NamedTuple):
    id: str
    is_success: bool
    resp: aiohttp.ClientResponse
    info: any = None

    @property
    def status(self):
        return self.resp.status


class API:
    BASE_URL = None

    def __init__(self, client: pybotters.Client, **kwargs):
        self._client = client

    async def request(self, method, url, *, params=None, data=None, **kwargs):
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

    async def market_order(
        self, symbol: str, side: str, size: float, *, params: dict = None, **kwargs
    ) -> "OrderResponse":
        raise NotImplementedError

    async def limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        *,
        params: dict = None,
        **kwargs,
    ) -> "OrderResponse":
        raise NotImplementedError

    async def cancel_order(
        self, symbol: str, order_id: str, *, params: dict = None, **kwargs
    ) -> "CancelResponse":
        raise NotImplementedError

    def _attach_base_url(self, url):
        return url if self._client._base_url else self.BASE_URL + url

    async def _create_order_impl(
        self, endpoint: str, data: dict, id_key: str, params: dict | None, **kwargs
    ):
        resp = await self.post(endpoint, data=self._make_data(data, params), **kwargs)
        return await self._make_market_order_response(resp, id_key)

    async def _make_market_order_response(
        self, resp: aiohttp.ClientResponse, id_key: str
    ) -> "OrderResponse":
        resp_data = await self._to_response_data_new(resp)
        order_id = self._get_order_id_new(resp, resp_data, id_key)
        return self._to_order_response(order_id, resp, resp_data)

    async def _cancel_order_impl(
        self,
        endpoint: str,
        data: dict,
        order_id: str,
        params: dict | None,
        method: str = "DELETE",
        **kwargs,
    ):
        resp = await self.request(
            method, endpoint, data=self._make_data(data, params), **kwargs
        )
        return await self._make_cancel_order_response(resp, order_id)

    async def _make_cancel_order_response(
        self,
        resp: aiohttp.ClientResponse,
        order_id: str,
    ) -> CancelResponse:
        resp_data = await self._to_response_data_cancel(resp)
        is_success = self._to_is_success(resp)
        return self._to_cancel_response(order_id, is_success, resp, resp_data)

    def _make_data(self, data: dict | None, params: dict | None):
        data = data or {}
        params = params or {}
        return {**data, **params}

    async def _to_response_data_new(self, resp: "aiohttp.ClientResponse") -> dict:
        return await resp.json()

    async def _to_response_data_cancel(self, resp: "aiohttp.ClientResponse") -> dict:
        return await resp.json()

    def _get_order_id_new(
        self, resp: "aiohttp.ClientResponse", resp_data: dict, id_key: str
    ) -> str | None:
        if resp.status == 200:
            order_id = resp_data
            for k in id_key.split("."):
                order_id = order_id[k]
            return str(order_id)
        else:
            return None

    def _to_order_response(
        self, order_id: str, resp: "aiohttp.ClientResponse", resp_data: dict
    ) -> "OrderResponse":
        return OrderResponse(order_id, resp, resp_data)

    def _to_is_success(self, resp: "aiohttp.ClientResponse") -> bool:
        return resp.status == 200

    def _to_cancel_response(
        self,
        order_id: str,
        is_success: bool,
        resp: "aiohttp.ClientResponse",
        resp_data: dict,
    ) -> "CancelResponse":
        return CancelResponse(order_id, is_success, resp, resp_data)
