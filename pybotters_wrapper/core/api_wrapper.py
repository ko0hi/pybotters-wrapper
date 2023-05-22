import pybotters
from aiohttp.client import ClientResponse
from requests import Response

from .api_client import APIClient
from .api_fetch_orderbook import OrderbookFetchAPI, OrderbookFetchAPIResponse
from .api_fetch_orders import OrdersFetchAPI, OrdersFetchAPIResponse
from .api_fetch_positions import PositionsFetchAPI, PositionsFetchAPIResponse
from .api_fetch_ticker import TickerFetchAPI, TickerFetchAPIResponse
from .api_order_cancel import CancelOrderAPI, CancelOrderAPIResponse
from .api_order_limit import LimitOrderAPI, LimitOrderAPIResponse
from .api_order_market import MarketOrderAPI, MarketOrderAPIResponse
from .api_order_stop_limit import StopLimitOrderAPI, StopLimitOrderAPIResponse
from .api_order_stop_market import StopMarketOrderAPI, StopMarketOrderAPIResponse
from .exchange_property import ExchangeProperty
from .formatter_precision import PriceSizeFormatter
from .._typedefs import (
    TRequestMethod,
    TSymbol,
    TSide,
    TPrice,
    TSize,
    TTrigger,
    TOrderId,
)


class APIWrapper:
    def __init__(
        self,
        api_client: APIClient,
        *,
        limit_order_api: LimitOrderAPI,
        market_order_api: MarketOrderAPI,
        stop_limit_order_api: StopLimitOrderAPI,
        stop_market_order_api: StopMarketOrderAPI,
        cancel_order_api: CancelOrderAPI,
        ticker_fetch_api: TickerFetchAPI,
        orderbook_fetch_api: OrderbookFetchAPI,
        orders_fetch_api: OrdersFetchAPI,
        positions_fetch_api: PositionsFetchAPI,
    ):
        self._api_client = api_client
        self._limit_order_api = limit_order_api
        self._market_order_api = market_order_api
        self._stop_limit_order_api = stop_limit_order_api
        self._stop_market_order_api = stop_market_order_api
        self._cancel_order_api = cancel_order_api
        self._ticker_fetch_api = ticker_fetch_api
        self._orderbook_fetch_api = orderbook_fetch_api
        self._orders_fetch_api = orders_fetch_api
        self._positions_fetch_api = positions_fetch_api

    async def request(
        self,
        method: TRequestMethod,
        url: str,
        *,
        params_or_data: dict | None = None,
        **kwargs,
    ) -> ClientResponse:
        return await self._api_client.request(
            method, url, params_or_data=params_or_data, **kwargs
        )

    async def get(
        self, url: str, *, params: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._api_client.get(url, params=params, **kwargs)

    async def post(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._api_client.post(url, data=data, **kwargs)

    async def put(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._api_client.put(url, data=data, **kwargs)

    async def delete(
        self, url: str, *, data: dict | None = None, **kwargs
    ) -> ClientResponse:
        return await self._api_client.delete(url, data=data, **kwargs)

    def srequest(
        self,
        method: TRequestMethod,
        url: str,
        *,
        params_or_data: dict | None = None,
        **kwargs,
    ) -> Response:
        return self._api_client.srequest(
            method, url, params_or_data=params_or_data, **kwargs
        )

    def sget(self, url: str, *, params: dict | None = None, **kwargs) -> Response:
        return self._api_client.sget(url, params=params, **kwargs)

    def spost(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self._api_client.spost(url, data=data, **kwargs)

    def sput(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self._api_client.sput(url, data=data, **kwargs)

    def sdelete(self, url: str, *, data: dict | None = None, **kwargs) -> Response:
        return self._api_client.sdelete(url, data=data, **kwargs)

    async def limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> LimitOrderAPIResponse:
        if self._limit_order_api is None:
            raise RuntimeError("limit_order is not supported.")
        return await self._limit_order_api.limit_order(
            symbol,
            side,
            price,
            size,
            extra_params=extra_params,
            request_params=request_params,
        )

    async def market_order(
        self,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> MarketOrderAPIResponse:
        if self._market_order_api is None:
            raise RuntimeError("market_order is not supported.")
        return await self._market_order_api.market_order(
            symbol, side, size, extra_params=extra_params, request_params=request_params
        )

    async def stop_limit_order(
        self,
        symbol: TSymbol,
        side: TSide,
        price: TPrice,
        size: TSize,
        trigger: TTrigger,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> StopLimitOrderAPIResponse:
        if self._stop_limit_order_api is None:
            raise RuntimeError("stop_limit_order is not supported.")
        return await self._stop_limit_order_api.stop_limit_order(
            symbol,
            side,
            price,
            size,
            trigger,
            extra_params=extra_params,
            request_params=request_params,
        )

    async def stop_market_order(
        self,
        symbol: TSymbol,
        side: TSide,
        size: TSize,
        trigger: TTrigger,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> StopMarketOrderAPIResponse:
        if self._stop_market_order_api is None:
            raise RuntimeError("stop_market_order is not supported.")
        return await self._stop_market_order_api.stop_market_order(
            symbol,
            side,
            size,
            trigger,
            extra_params=extra_params,
            request_params=request_params,
        )

    async def cancel_order(
        self,
        symbol: TSymbol,
        order_id: TOrderId,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> CancelOrderAPIResponse:
        if self._cancel_order_api is None:
            raise RuntimeError("cancel_order is not supported.")
        return await self._cancel_order_api.cancel_order(
            symbol,
            order_id,
            extra_params=extra_params,
            request_params=request_params,
        )

    async def fetch_ticker(self, symbol: TSymbol) -> TickerFetchAPIResponse:
        if self._ticker_fetch_api is None:
            raise RuntimeError("fetch_ticker is not supported.")
        return await self._ticker_fetch_api.fetch_ticker(symbol)

    async def fetch_orderbook(self, symbol: TSymbol) -> OrderbookFetchAPIResponse:
        if self._orderbook_fetch_api is None:
            raise RuntimeError("fetch_orderbook is not supported.")
        return await self._orderbook_fetch_api.fetch_orderbook(symbol)

    async def fetch_orders(
        self,
        symbol: TSymbol,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> OrdersFetchAPIResponse:
        if self._orders_fetch_api is None:
            raise RuntimeError("fetch_orders is not supported.")
        return await self._orders_fetch_api.fetch_orders(
            symbol, extra_params=extra_params, request_params=request_params
        )

    async def fetch_positions(
        self,
        symbol: TSymbol,
        *,
        extra_params: dict = None,
        request_params: dict = None,
    ) -> PositionsFetchAPIResponse:
        if self._positions_fetch_api is None:
            raise RuntimeError("fetch_positions is not supported.")
        return await self._positions_fetch_api.fetch_positions(
            symbol, extra_params=extra_params, request_params=request_params
        )

    @property
    def client(self) -> pybotters.Client:
        return self._api_client._client

    @property
    def price_size_formatter(self) -> PriceSizeFormatter:
        return self._limit_order_api._price_size_formatter  # noqa

    @property
    def exchange_property(self) -> ExchangeProperty:
        return self._limit_order_api._api_client._eprop  # noqa
