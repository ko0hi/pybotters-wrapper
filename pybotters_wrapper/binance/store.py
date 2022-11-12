from typing import Generic, TypeVar

import pandas as pd

from pybotters.models.binance import (
    BinanceDataStoreBase,
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
    BinanceCOINMDataStore,
)
from pybotters_wrapper.common import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
    OrderStore,
    ExecutionStore,
    PositionStore,
)
from pybotters_wrapper.binance.socket import (
    BinanceSpotWebsocketChannels,
    BinanceUSDSMWebsocketChannels,
    BinanceCOINMWebsocketChannels,
)

import pybotters


T = TypeVar("T", bound=BinanceDataStoreBase)


class BinanceTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {"symbol": d["s"], "price": float(d["c"])}


class BinanceTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return {
            "id": d["a"],
            "symbol": d["s"],
            "side": "SELL" if d["m"] else "BUY",
            "price": float(d["p"]),
            "size": float(d["q"]),
            "timestamp": pd.to_datetime(d["T"], unit="ms"),
        }


class BinanceOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "symbol": d["s"],
            "side": d["S"],
            "price": float(d["p"]),
            "size": float(d["q"]),
        }


class BinanceOrderStore(OrderStore):
    def _normalize(self, d: dict, op: str) -> "OrderItem":
        return {
            "id": d["i"],
            "symbol": d["s"],
            "side": d["S"],
            "price": float(d["p"]),
            "size": float(d["q"]) - float(d["z"]),
            "type": d["f"],
        }


class BinanceExecutionStore(ExecutionStore):
    def _get_operation(self, change: "StoreChange") -> "Callable":
        if change.data["X"] in ("FILLED", "PARTIALLY_FILLED"):
            return self._insert

    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        return {
            "id": d["i"],
            "symbol": d["s"],
            "side": d["S"],
            "price": float(d["p"]),
            "size": float(d["l"]),
            "timestamp": pd.to_datetime(d["T"], unit="ms"),
        }


class BinancePositionStore(PositionStore):
    _AVAILABLE_OPERATIONS = ("_update",)

    def _normalize(self, d: dict, op: str) -> "PositionItem":
        return {
            "symbol": d["s"],
            "side": "BUY" if d["ps"] == "LONG" else "SELL",
            "price": float(d["ep"]),
            "size": float(d["pa"]),
        }


class _BinanceDataStoreWrapper(DataStoreWrapper[T]):
    _TICKER_STORE = (BinanceTickerStore, "ticker")
    _TRADES_STORE = (BinanceTradesStore, "trade")
    _ORDERBOOK_STORE = (BinanceOrderbookStore, "orderbook")
    _ORDER_STORE = (BinanceOrderStore, "order")
    _EXECUTION_STORE = (BinanceExecutionStore, "order")
    _POSITION_STORE = (BinancePositionStore, "position")

    _WRAP_CLS = None

    def __init__(self, store: BinanceDataStoreBase = None):
        super(_BinanceDataStoreWrapper, self).__init__(store or self._WRAP_CLS())

    def _subscribe_one(self, channel: str, **kwargs):
        if channel in (
            "order",
            "execution",
            "position",
        ):
            self._ws_channels.add(channel, listen_key=self.store.listenkey)
        else:
            self._ws_channels.add(channel, **kwargs)


class BinanceSpotDataStoreWrapper(_BinanceDataStoreWrapper[BinanceSpotDataStore]):
    _SOCKET_CHANNELS_CLS = BinanceSpotWebsocketChannels
    _WRAP_CLS = BinanceSpotDataStore


class BinanceUSDSMDataStoreWrapper(_BinanceDataStoreWrapper[BinanceUSDSMDataStore]):
    _SOCKET_CHANNELS_CLS = BinanceUSDSMWebsocketChannels
    _WRAP_CLS = BinanceUSDSMDataStore


class BinanceCOINMDataStoreWrapper(_BinanceDataStoreWrapper[BinanceCOINMDataStore]):
    _SOCKET_CHANNELS_CLS = BinanceCOINMWebsocketChannels
    _WRAP_CLS = BinanceCOINMDataStore
