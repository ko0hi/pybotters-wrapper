from __future__ import annotations

from typing import TypeVar

from .api import (
    APIClient,
    CancelOrderAPI,
    LimitOrderAPI,
    MarketOrderAPI,
    OrderbookFetchAPI,
    OrdersFetchAPI,
    PositionsFetchAPI,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
    TickerFetchAPI,
)
from .api_wrapper import APIWrapper

TAPIWrapperBuilder = TypeVar("TAPIWrapperBuilder", bound="APIWrapperBuilder")


class APIWrapperBuilder:
    def __init__(self):
        self._api_client: APIClient | None = None
        self._limit_order_api: LimitOrderAPI | None = None
        self._market_order_api: MarketOrderAPI | None = None
        self._stop_limit_order_api: StopLimitOrderAPI | None = None
        self._stop_market_order_api: StopMarketOrderAPI | None = None
        self._cancel_order_api: CancelOrderAPI | None = None
        self._ticker_fetch_api: TickerFetchAPI | None = None
        self._orderbook_fetch_api: OrderbookFetchAPI | None = None
        self._orders_fetch_api: OrdersFetchAPI | None = None
        self._positions_fetch_api: PositionsFetchAPI | None = None

    def set_api_client(
        self: TAPIWrapperBuilder, api_client: APIClient
    ) -> TAPIWrapperBuilder:
        self._api_client = api_client
        return self

    def set_limit_order_api(
        self: TAPIWrapperBuilder, limit_order_api: LimitOrderAPI
    ) -> TAPIWrapperBuilder:
        self._limit_order_api = limit_order_api
        return self

    def set_market_order_api(
        self: TAPIWrapperBuilder, market_order_api: MarketOrderAPI
    ) -> TAPIWrapperBuilder:
        self._market_order_api = market_order_api
        return self

    def set_stop_limit_order_api(
        self: TAPIWrapperBuilder, stop_limit_order_api: StopLimitOrderAPI
    ) -> TAPIWrapperBuilder:
        self._stop_limit_order_api = stop_limit_order_api
        return self

    def set_stop_market_order_api(
        self: TAPIWrapperBuilder, stop_market_order_api: StopMarketOrderAPI
    ) -> TAPIWrapperBuilder:
        self._stop_market_order_api = stop_market_order_api
        return self

    def set_cancel_order_api(
        self, cancel_order_api: CancelOrderAPI
    ) -> APIWrapperBuilder:
        self._cancel_order_api = cancel_order_api
        return self

    def set_ticker_fetch_api(
        self: TAPIWrapperBuilder, ticker_fetch_api: TickerFetchAPI
    ) -> TAPIWrapperBuilder:
        self._ticker_fetch_api = ticker_fetch_api
        return self

    def set_orderbook_fetch_api(
        self: TAPIWrapperBuilder, orderbook_fetch_api: OrderbookFetchAPI
    ) -> TAPIWrapperBuilder:
        self._orderbook_fetch_api = orderbook_fetch_api
        return self

    def set_orders_fetch_api(
        self: TAPIWrapperBuilder, orders_fetch_api: OrdersFetchAPI
    ) -> TAPIWrapperBuilder:
        self._orders_fetch_api = orders_fetch_api
        return self

    def set_positions_fetch_api(
        self: TAPIWrapperBuilder, positions_fetch_api: PositionsFetchAPI
    ) -> TAPIWrapperBuilder:
        self._positions_fetch_api = positions_fetch_api
        return self

    def get(self) -> APIWrapper:
        if self._api_client is None:
            raise ValueError("Missing required field: api_client")
        return APIWrapper(
            self._api_client,
            limit_order_api=self._limit_order_api,
            market_order_api=self._market_order_api,
            stop_limit_order_api=self._stop_limit_order_api,
            stop_market_order_api=self._stop_market_order_api,
            cancel_order_api=self._cancel_order_api,
            ticker_fetch_api=self._ticker_fetch_api,
            orderbook_fetch_api=self._orderbook_fetch_api,
            orders_fetch_api=self._orders_fetch_api,
            positions_fetch_api=self._positions_fetch_api,
        )
