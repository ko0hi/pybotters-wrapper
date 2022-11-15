from typing import Generic, TypeVar

import copy
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
            "id": str(d["a"]),
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
            "id": str(d["i"]),
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
            "id": str(d["i"]),
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

    def _subscribe_one(self, channel: str, **kwargs):
        if channel in (
            "order",
            "execution",
            "position",
        ):
            self._ws_channels.add(channel, listen_key=self.store.listenkey)
        else:
            self._ws_channels.add(channel, **kwargs)

    def _parse_send(
        self, endpoint: str, send: any, client: pybotters.Client
    ) -> dict[str, list[any]]:
        subscribe_list = super()._parse_send(endpoint, send, client)

        # エンドポイントごとにparamsを一つにまとめる（バラバラだと量によっては接続できない場合がある）
        compressed = {}
        for endpoint, sends in subscribe_list.items():
            compressed[endpoint] = {
                "method": "SUBSCRIBE",
                "params": [s["params"][0] for s in sends],
                "id": sends[0]["id"],
            }

        rtn = copy.deepcopy(compressed)
        for endpoint, send in compressed.items():
            rtn[endpoint]["params"] = []
            for p in send["params"]:
                if p == "LISTEN_KEY":
                    if self.store.listenkey is None:
                        raise RuntimeError(
                            f"`listenkey` has not been initialized. "
                            f"HINT: "
                            f"`store.initialize(..., 'token_private', client=client)`"
                        )
                    rtn[endpoint]["params"].append(self.store.listenkey)
                else:
                    rtn[endpoint]["params"].append(p)
        return rtn


class BinanceSpotDataStoreWrapper(_BinanceDataStoreWrapper[BinanceSpotDataStore]):
    _WEBSOCKET_CHANNELS = BinanceSpotWebsocketChannels
    _INITIALIZE_ENDPOINTS = {
        "token": ("POST", "/api/v3/userDataStream"),
        "token_private": ("POST", "/api/v3/userDataStream"),
        "orderbook": ("GET", "/api/v3/depth"),
        "order": ("GET", "/api/v3/openOrders"),
    }
    _WRAP_STORE = BinanceSpotDataStore


class BinanceUSDSMDataStoreWrapper(_BinanceDataStoreWrapper[BinanceUSDSMDataStore]):
    _WEBSOCKET_CHANNELS = BinanceUSDSMWebsocketChannels
    _INITIALIZE_ENDPOINTS = {
        "token": ("POST", "/fapi/v1/listenKey"),
        "token_private": ("POST", "/fapi/v1/listenKey"),
        "orderbook": ("GET", "/fapi/v1/depth"),
        "order": ("GET", "/fapi/v1/openOrders"),
    }
    _WRAP_STORE = BinanceUSDSMDataStore


class BinanceCOINMDataStoreWrapper(_BinanceDataStoreWrapper[BinanceCOINMDataStore]):
    _WEBSOCKET_CHANNELS = BinanceCOINMWebsocketChannels
    _INITIALIZE_ENDPOINTS = {
        "token": ("POST", "/dapi/v1/listenKey"),
        "token_private": ("POST", "/dapi/v1/listenKey"),
        "orderbook": ("GET", "/dapi/v1/depth"),
        "order": ("GET", "/dapi/v1/openOrders"),
    }
    _WRAP_STORE = BinanceCOINMDataStore
