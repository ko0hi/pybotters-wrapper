from typing import NamedTuple

import aiohttp
import pybotters


class OrderResponse(NamedTuple):
    order_id: str
    resp: aiohttp.ClientResponse
    info: any = None

    @property
    def status(self):
        return self.resp.status


class CancelResponse(NamedTuple):
    order_id: str
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
        self, symbol: str, side: str, size: float, params: dict = None, **kwargs
    ) -> "OrderResponse":
        raise NotImplementedError

    async def limit_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        params: dict = None,
        **kwargs
    ) -> "OrderResponse":
        raise NotImplementedError

    async def cancel_order(
        self, order_id: str, params: dict = None, **kwargs
    ) -> "CancelResponse":
        raise NotImplementedError

    def _attach_base_url(self, url):
        return url if self._client._base_url else self.BASE_URL + url

    async def _post_order(self, endpoint: str, data: dict, id_key: str, **kwargs):
        resp = await self.post(endpoint, data=data, **kwargs)
        resp_data = await resp.json()

        if resp.status == 200:
            order_id = resp_data
            for k in id_key.split("."):
                order_id = order_id[k]
            order_id = str(order_id)
        else:
            order_id = None

        return self._make_market_order_response(resp, resp_data, order_id)

    async def _delete_order(self, endpoint: str, data: dict, order_id: str, **kwargs):
        resp = await self.delete(endpoint, data=data, **kwargs)
        resp_data = await resp.json()
        return self._make_cancel_order_response(resp, resp_data, order_id)

    def _make_market_order_response(
        self, resp: aiohttp.ClientResponse, resp_data: any, order_id: str
    ) -> OrderResponse:
        return OrderResponse(order_id, resp, resp_data)

    def _make_cancel_order_response(
        self,
        resp: aiohttp.ClientResponse,
        resp_data: any,
        order_id: str,
        is_success: bool = None,
    ):
        if is_success is None:
            is_success = resp.status == 200
        return CancelResponse(order_id, is_success, resp, resp_data)
