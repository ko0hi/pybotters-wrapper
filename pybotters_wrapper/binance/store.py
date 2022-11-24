from typing import Generic, TypeVar

import copy
import pandas as pd
from yarl import URL

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
            "timestamp": pd.to_datetime(d["T"], unit="ms", utc=True),
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
            "type": d["o"],
        }


class BinanceExecutionStore(ExecutionStore):
    """ 対応ストアなし

    """
    def _onmessage(self, msg: "Item", ws: "ClientWebSocketResponse"):
        if "e" in msg:
            item = None
            if msg["e"] == "ORDER_TRADE_UPDATE":
                # futures
                item = msg["o"]
            elif msg["e"] == "executionReport":
                item = msg
            if item and item["X"] in ("TRADE", "PARTIALLY_FILLED", "FILLED"):
                item = self._itemize(
                    str(item["i"]),
                    item["s"],
                    item["S"],
                    float(item["L"]),
                    float(item["l"]),
                    pd.to_datetime(item["T"], unit="ms", utc=True)
                )
                self._insert([{**item, "info": msg}])



class BinancePositionStore(PositionStore):
    _KEYS = ["symbol", "ps"]

    def _get_operation(self, change: "StoreChange") -> str | None:
        if change.data["ps"] == "BOTH":
            if float(change.data["pa"]) == 0:
                return "_delete"
            else:
                return f"_{change.operation}"
        else:
            return f"_{change.operation}"

    def _normalize(self, d: dict, op: str) -> "PositionItem":
        size = float(d["pa"])

        if d["ps"] == "BOTH":
            if size == 0:
                side = None
            elif size > 0:
                side = "BUY"
            else:
                side = "SELL"
        else:
            side = "BUY" if d["ps"] == "LONG" else "SELL"

        return {
            "symbol": d["s"],
            "side": side,
            "price": float(d["ep"]),
            "size": abs(size),
            "ps": d["ps"]
        }


class _BinanceDataStoreWrapper(DataStoreWrapper[T]):
    _TICKER_STORE = (BinanceTickerStore, "ticker")
    _TRADES_STORE = (BinanceTradesStore, "trade")
    _ORDERBOOK_STORE = (BinanceOrderbookStore, "orderbook")
    _ORDER_STORE = (BinanceOrderStore, "order")
    _EXECUTION_STORE = (BinanceExecutionStore, None)
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

        rtn = copy.deepcopy(subscribe_list)
        for endpoint, send in subscribe_list.items():
            rtn[endpoint]["params"] = []
            for p in send["params"]:
                if p == "LISTEN_KEY":
                    if self.store.listenkey is None:
                        raise RuntimeError(
                            f"`listenkey` has not been initialized. "
                            f"HINT: "
                            f"`store.initialize(..., 'token_private', client=client)`"
                        )

                    if self.store.listenkey not in rtn[endpoint]["params"]:
                        rtn[endpoint]["params"].append(self.store.listenkey)
        return rtn


class BinanceSpotDataStoreWrapper(_BinanceDataStoreWrapper[BinanceSpotDataStore]):
    _NAME = "binancespot"
    _WEBSOCKET_CHANNELS = BinanceSpotWebsocketChannels
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/api/v3/userDataStream", None),
        "token_private": ("POST", "/api/v3/userDataStream", None),
        "orderbook": ("GET", "/api/v3/depth", ["symbol"]),
        "order": ("GET", "/api/v3/openOrders", None),
    }
    _WRAP_STORE = BinanceSpotDataStore

    async def _initialize_request(
        self,
        client: "pybotters.Client",
        method: str,
        endpoint: str,
        params_or_data: dict | None = None,
        **kwargs,
    ):
        from .api import BinanceSpotAPI

        kwargs = kwargs or {}
        if URL(endpoint).path in BinanceSpotAPI._PUBLIC_ENDPOINTS:
            kwargs["auth"] = None
        return await super()._initialize_request(
            client, method, endpoint, params_or_data, **kwargs
        )


class BinanceUSDSMDataStoreWrapper(_BinanceDataStoreWrapper[BinanceUSDSMDataStore]):
    _NAME = "binanceusdsm"
    _WEBSOCKET_CHANNELS = BinanceUSDSMWebsocketChannels
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/fapi/v1/listenKey", None),
        "token_private": ("POST", "/fapi/v1/listenKey", None),
        "orderbook": ("GET", "/fapi/v1/depth", ["symbol"]),
        "order": ("GET", "/fapi/v1/openOrders", None),
    }
    _WRAP_STORE = BinanceUSDSMDataStore


class BinanceCOINMDataStoreWrapper(_BinanceDataStoreWrapper[BinanceCOINMDataStore]):
    _NAME = "binancecoinm"
    _WEBSOCKET_CHANNELS = BinanceCOINMWebsocketChannels
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/dapi/v1/listenKey", None),
        "token_private": ("POST", "/dapi/v1/listenKey", None),
        "orderbook": ("GET", "/dapi/v1/depth", ["symbol"]),
        "order": ("GET", "/dapi/v1/openOrders", None),
    }
    _WRAP_STORE = BinanceCOINMDataStore
