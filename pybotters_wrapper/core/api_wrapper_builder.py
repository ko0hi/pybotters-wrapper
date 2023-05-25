from __future__ import annotations

from .api import (
    APIClient,
    OrderbookFetchAPI,
    OrdersFetchAPI,
    PositionsFetchAPI,
    TickerFetchAPI,
    CancelOrderAPI,
    LimitOrderAPI,
    MarketOrderAPI,
    StopLimitOrderAPI,
    StopMarketOrderAPI,
)

from .api_wrapper import APIWrapper


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

    def set_api_client(self, api_client: APIClient) -> APIWrapperBuilder:
        self._api_client = api_client
        return self

    def set_limit_order_api(self, limit_order_api: LimitOrderAPI) -> APIWrapperBuilder:
        self._limit_order_api = limit_order_api
        return self

    def set_market_order_api(
        self, market_order_api: MarketOrderAPI
    ) -> APIWrapperBuilder:
        self._market_order_api = market_order_api
        return self

    def set_stop_limit_order_api(
        self, stop_limit_order_api: StopLimitOrderAPI
    ) -> APIWrapperBuilder:
        self._stop_limit_order_api = stop_limit_order_api
        return self

    def set_stop_market_order_api(
        self, stop_market_order_api: StopMarketOrderAPI
    ) -> APIWrapperBuilder:
        self._stop_market_order_api = stop_market_order_api
        return self

    def set_cancel_order_api(
        self, cancel_order_api: CancelOrderAPI
    ) -> APIWrapperBuilder:
        self._cancel_order_api = cancel_order_api
        return self

    def set_ticker_fetch_api(
        self, ticker_fetch_api: TickerFetchAPI
    ) -> APIWrapperBuilder:
        self._ticker_fetch_api = ticker_fetch_api
        return self

    def set_orderbook_fetch_api(
        self, orderbook_fetch_api: OrderbookFetchAPI
    ) -> APIWrapperBuilder:
        self._orderbook_fetch_api = orderbook_fetch_api
        return self

    def set_orders_fetch_api(
        self, orders_fetch_api: OrdersFetchAPI
    ) -> APIWrapperBuilder:
        self._orders_fetch_api = orders_fetch_api
        return self

    def set_positions_fetch_api(
        self, positions_fetch_api: PositionsFetchAPI
    ) -> APIWrapperBuilder:
        self._positions_fetch_api = positions_fetch_api
        return self

    def get(self) -> APIWrapper:
        self.validate()
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

    def validate(self) -> None:
        required_fields = ["api_client"]
        missing_fields = [
            field for field in required_fields if getattr(self, f"_{field}") is None
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
