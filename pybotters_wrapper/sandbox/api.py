from __future__ import annotations

from typing import TYPE_CHECKING
from collections import namedtuple

if TYPE_CHECKING:
    import requests
    from pybotters_wrapper.sandbox import SandboxEngine

from pybotters_wrapper.core import API
from pybotters_wrapper.core.api import OrderResponse


SandboxResponse = namedtuple("SandboxResponse", ("status", "reason"))



class SandboxAPI(API):
    def __init__(self, simulate_api: API, **kwargs):
        super(SandboxAPI, self).__init__(
            simulate_api._client, simulate_api._verbose, **kwargs
        )
        self._simulate_api = simulate_api
        self._engine: SandboxEngine = None

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
        order_id = self._engine.insert_order(symbol, side, price, size, "LIMIT")
        return OrderResponse(order_id, SandboxResponse(200, "ok"), {})

    async def market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        order_id = self._engine.insert_order(symbol, side, None, size, "MARKET")
        return OrderResponse(order_id, SandboxResponse(200, "ok"), {})

    async def cancel_order(
        self,
        symbol: str,
        order_id: str,
        request_params: dict = None,
        **kwargs,
    ) -> "OrderResponse":
        try:
            self._engine.delete_order(symbol, order_id)
            return OrderResponse(order_id, SandboxResponse(200, "ok"), {})
        except RuntimeError:
            return OrderResponse(order_id, SandboxResponse(500, "cancel failed"))


    async def stop_market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        trigger: float,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        raise NotImplementedError("Unsupported: stop_limit_order")

    async def stop_limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        trigger: float,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        raise NotImplementedError("Unsupported: stop_limit_order")

    async def request(self, method, url, *, params=None, data=None, **kwargs):
        return await self._simulate_api.request(
            method, url, params=params, data=data, **kwargs
        )

    def srequest(
        self, method, url, *, params=None, data=None, **kwargs
    ) -> requests.Response:
        return self._simulate_api.srequest(
            method, url, params=params, data=data, **kwargs
        )

    def _link_to_engine(self, engine: "SandboxEngine"):
        self._engine = engine
