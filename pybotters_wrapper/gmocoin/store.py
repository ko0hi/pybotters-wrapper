from __future__ import annotations

import asyncio

import pandas as pd
import pybotters
from pybotters.models.gmocoin import GMOCoinDataStore
from pybotters_wrapper.core.store import (
    DataStoreWrapper,
    ExecutionItem,
    ExecutionStore,
    OrderbookItem,
    OrderbookStore,
    OrderItem,
    OrderStore,
    PositionItem,
    PositionStore,
    TickerItem,
    TickerStore,
    TradesItem,
    TradesStore,
)
from pybotters_wrapper.gmocoin import GMOWebsocketChannels
from pybotters_wrapper.utils.mixins import GMOCoinMixin


class GMOCoinTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["symbol"].name, float(d["last"]))


class GMOCoinTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            hash(tuple(d)),
            d["symbol"].name,
            d["side"].name,
            float(d["price"]),
            float(d["size"]),
            pd.to_datetime(d["timestamp"], utc=True),
        )


class GMOCoinOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            d["symbol"].name, d["side"].name, float(d["price"]), float(d["size"])
        )


class GMOCoinOrderStore(OrderStore):
    def _normalize(self, d: dict, op: str) -> "OrderItem":
        return self._itemize(
            str(d["order_id"]),
            d["symbol"].name,
            d["side"].name,
            float(d["price"]),
            float(d["size"]),
            d["execution_type"],
        )


class GMOCoinExecutionStore(ExecutionStore):
    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        return self._itemize(
            str(d["order_id"]),
            d["symbol"].name,
            d["side"].name,
            float(d["price"]),
            float(d["size"]),
            pd.to_datetime(d["timestamp"], utc=True),
        )


class GMOCoinPositionStore(PositionStore):
    def _normalize(self, d: dict, op: str) -> "PositionItem":
        return self._itemize(
            d["symbol"].name, d["side"].name, float(d["price"]), float(d["size"])
        )


class GMOCoinDataStoreWrapper(GMOCoinMixin, DataStoreWrapper[GMOCoinDataStore]):
    _WRAP_STORE = GMOCoinDataStore
    _WEBSOCKET_CHANNELS = GMOWebsocketChannels
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/private/v1/ws-auth", None),
        "token_private": ("POST", "/private/v1/ws-auth", None),
        "order": ("GET", "/private/v1/activeOrders", ["symbol"]),
        "position": ("GET", "/private/v1/openPositions", ["symbol"]),
    }
    _TICKER_STORE = (GMOCoinTickerStore, "ticker")
    _TRADES_STORE = (GMOCoinTradesStore, "trades")
    _ORDERBOOK_STORE = (GMOCoinOrderbookStore, "orderbooks")
    _ORDER_STORE = (GMOCoinOrderStore, "orders")
    _EXECUTION_STORE = (GMOCoinExecutionStore, "executions")
    _POSITION_STORE = (GMOCoinPositionStore, "positions")

    def _parse_connect_send(
        self, endpoint: str, send: any, client: pybotters.Client
    ) -> dict[str, list[any]]:
        subscribe_list = super()._parse_connect_send(endpoint, send, client)
        rtn = {}
        for endpoint, send_items in subscribe_list.items():
            if "private" in endpoint:
                if self.store.token is None:
                    import pybotters_wrapper as pbw

                    api = pbw.create_api(self.exchange, client)
                    _, url, _ = self._INITIALIZE_CONFIG["token"]
                    resp = api.spost(url)
                    data = resp.json()
                    key = data["data"]
                    self.store.token = key
                    asyncio.create_task(self.store._token(client._session))
                    self.log("`token` got automatically initialized. ", "warning")
                rtn[endpoint + f"/{self.store.token}"] = send_items

            else:
                rtn[endpoint] = send_items

        return rtn
