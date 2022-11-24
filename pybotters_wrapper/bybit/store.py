from __future__ import annotations

import pandas as pd
from pybotters.models.bybit import BybitUSDTDataStore, BybitInverseDataStore

from pybotters_wrapper.bybit import BybitUSDTWebsocketChannels, \
    BybitInverseWebsocketChannels
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.common.store import TickerStore, TradesStore, OrderbookStore


class BybitTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {"symbol": d["symbol"], "price": d["last_price"]}


class BybitTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "id": d["trade_id"],
            "symbol": d["symbol"],
            "side": d["side"].upper(),
            "price": float(d["price"]),
            "size": d["size"],
            "timestamp": pd.to_datetime(d["timestamp"]),
        }


class BybitOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "symbol": d["symbol"],
            "side": d["side"].upper(),
            "price": float(d["price"]),
            "size": float(d["size"]),
        }


class BybitDataStoreMixin:
    _TICKER_STORE = (BybitTickerStore, "instrument")
    _TRADES_STORE = (BybitTradesStore, "trade")
    _ORDERBOOK_STORE = (BybitOrderbookStore, "orderbook")


class BybitUSDTDataStoreWrapper(
    BybitDataStoreMixin,
    DataStoreWrapper[BybitUSDTDataStore]
):
    _NAME = "bybitusdt"
    _WRAP_STORE = BybitUSDTDataStore
    _WEBSOCKET_CHANNELS = BybitUSDTWebsocketChannels


class BybitInverseDataStoreWrapper(
    BybitDataStoreMixin,
    DataStoreWrapper[BybitInverseDataStore]
):
    _NAME = "bybitinverse"
    _WRAP_STORE = BybitInverseDataStore
    _WEBSOCKET_CHANNELS = BybitInverseWebsocketChannels
