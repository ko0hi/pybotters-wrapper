from __future__ import annotations

import pandas as pd
from pybotters.models.gmocoin import GMOCoinDataStore
from pybotters_wrapper.common.store import (
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
            pd.to_datetime(d["timestamp"]),
        )


class GMOCoinOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            d["symbol"].name, d["side"].name, float(d["price"]), float(d["size"])
        )


class GMOCoinOrderStore(OrderStore):
    def _normalize(self, d: dict, op: str) -> "OrderItem":
        return self._itemize(
            str(d["orderId"]),
            d["symbol"].name,
            d["side"].name,
            float(d["orderPrice"]),
            float(d["orderSize"]),
            d["executionType"],
        )


class GMOCoinExecutionStore(ExecutionStore):
    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        return self._itemize(
            str(d["orderId"]),
            d["symbol"].name,
            d["side"].name,
            float(d["executionPrice"]),
            float(d["executionSize"]),
            pd.to_datetime(d["executionTimestamp"]),
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
        "position": ("GET", "/private/v1/activeOrders", ["symbol"]),
    }
    _TICKER_STORE = (GMOCoinTickerStore, "ticker")
    _TRADES_STORE = (GMOCoinTradesStore, "trades")
    _ORDERBOOK_STORE = (GMOCoinOrderbookStore, "orderbooks")
    _ORDER_STORE = (GMOCoinOrderStore, "orders")
    _EXECUTION_STORE = (GMOCoinExecutionStore, "executions")
    _POSITION_STORE = (GMOCoinPositionStore, "positions")
