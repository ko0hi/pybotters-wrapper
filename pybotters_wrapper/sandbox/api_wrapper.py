from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from aiohttp import ClientResponse
from requests import Response

from .exceptions import OrderNotFoundError

if TYPE_CHECKING:
    from pybotters_wrapper.sandbox import SandboxEngine

from ..core import (
    APIWrapper,
    CancelOrderAPIResponse,
    LimitOrderAPIResponse,
    MarketOrderAPIResponse,
    OrderbookFetchAPIResponse,
    OrdersFetchAPIResponse,
    PositionsFetchAPIResponse,
    StopLimitOrderAPIResponse,
    StopMarketOrderAPIResponse,
    TickerFetchAPIResponse,
    TOrderId,
    TPrice,
    TRequestMethod,
    TSide,
    TSize,
    TSymbol,
    TTrigger,
)


class SandboxResponse(NamedTuple):
    status: int

    @property
    def status_code(self) -> int:
        return self.status


class SandboxAPIWrapper:
    def __init__(self, simulate_api: APIWrapper, **kwargs):
        self._simulate_api = simulate_api
        self._engine: SandboxEngine

    async def limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> LimitOrderAPIResponse:
        self._check_is_api_available("limit_order")
        order_id = self._engine.insert_order(symbol, side, price, size, "LIMIT")
        return LimitOrderAPIResponse(
            order_id=order_id,
            resp=SandboxResponse(status=200),  # type: ignore
            data={},
        )

    async def market_order(
        self,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> MarketOrderAPIResponse:
        self._check_is_api_available("market_order")
        order_id = self._engine.insert_order(symbol, side, None, size, "MARKET")
        return MarketOrderAPIResponse(
            order_id=order_id, resp=SandboxResponse(status=200), data={}  # type: ignore
        )

    async def stop_limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        trigger: TTrigger,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> StopLimitOrderAPIResponse:
        self._check_is_api_available("stop_limit_order")
        order_id = self._engine.insert_order(
            symbol, side, price, size, "STOP_LIMIT", trigger=trigger
        )
        return StopLimitOrderAPIResponse(
            order_id=order_id, resp=SandboxResponse(status=200), data={}  # type: ignore
        )

    async def stop_market_order(
        self,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        trigger: TTrigger,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> StopMarketOrderAPIResponse:
        self._check_is_api_available("stop_market_order")
        order_id = self._engine.insert_order(
            symbol, side, None, size, "STOP_MARKET", trigger=trigger
        )
        return StopMarketOrderAPIResponse(
            order_id=order_id, resp=SandboxResponse(status=200), data={}  # type: ignore
        )

    async def cancel_order(
        self,
        symbol: TSymbol,
        order_id: TOrderId,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> CancelOrderAPIResponse:
        self._check_is_api_available("cancel_order")
        try:
            self._engine.delete_order(symbol, order_id)
        except OrderNotFoundError:
            status = 500
        else:
            status = 200
        return CancelOrderAPIResponse(
            order_id=order_id,
            resp=SandboxResponse(status=status),  # type: ignore
            data={},
        )

    async def fetch_ticker(self, symbol: TSymbol) -> TickerFetchAPIResponse:
        self._check_is_api_available("fetch_ticker")
        return await self._simulate_api.fetch_ticker(symbol)

    async def fetch_orderbook(self, symbol: TSymbol) -> OrderbookFetchAPIResponse:
        self._check_is_api_available("fetch_orderbook")
        return await self._simulate_api.fetch_orderbook(symbol)

    async def fetch_orders(
        self,
        symbol: TSymbol,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> OrdersFetchAPIResponse:
        self._check_is_api_available("fetch_orders")
        return await self._simulate_api.fetch_orders(
            symbol, extra_params=extra_params, request_params=request_params
        )

    async def fetch_positions(
        self,
        symbol: TSymbol,
        *,
        extra_params: dict | None = None,
        request_params: dict | None = None,
    ) -> PositionsFetchAPIResponse:
        self._check_is_api_available("fetch_positions")
        return await self._simulate_api.fetch_positions(
            symbol, extra_params=extra_params, request_params=request_params
        )

    async def request(
        self,
        method: TRequestMethod,
        url: str,
        *,
        params_or_data: dict | None = None,
        **kwargs,
    ) -> ClientResponse:
        return await self._simulate_api.request(
            method, url, params_or_data=params_or_data, **kwargs
        )

    async def get(
        self, url: str, *, params: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._simulate_api.get(url, params=params, **kwargs)

    async def post(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._simulate_api.post(url, data=data, **kwargs)

    async def put(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._simulate_api.put(url, data=data, **kwargs)

    async def delete(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._simulate_api.delete(url, data=data, **kwargs)

    def srequest(
        self,
        method: TRequestMethod,
        url: str,
        *,
        params_or_data: dict | None = None,
        **kwargs,
    ) -> Response:
        return self._simulate_api.srequest(
            method, url, params_or_data=params_or_data, **kwargs
        )

    def sget(self, url: str, *, params: dict | None = None, **kwargs) -> Response:
        return self._simulate_api.sget(url, params=params, **kwargs)

    def spost(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self._simulate_api.spost(url, data=data, **kwargs)

    def sput(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self._simulate_api.sput(url, data=data, **kwargs)

    def sdelete(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self._simulate_api.sdelete(url, data=data, **kwargs)

    def _check_is_api_available(
        self,
        api_name: str,
    ) -> None:
        if not self._simulate_api.is_available(api_name):  # type: ignore
            raise RuntimeError(
                f"{api_name} is not supported for: "
                f"{self._simulate_api.exchange_property.exchange}."
            )

    def _link_to_engine(self, engine: "SandboxEngine"):
        self._engine = engine
