from __future__ import annotations

import asyncio
from typing import TypeVar

import pandas as pd
import pybotters
from pybotters.models.binance import (
    BinanceCOINMDataStore,
    BinanceDataStoreBase,
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
)
from pybotters.store import Item, StoreChange
from legacy.binance.socket import (
    BinanceCOINMTESTWebsocketChannels,
    BinanceCOINMWebsocketChannels,
    BinanceSpotWebsocketChannels,
    BinanceUSDSMTESTWebsocketChannels,
    BinanceUSDSMWebsocketChannels,
)
from legacy.core.store import (
    DataStoreWrapper,
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
from pybotters_wrapper.utils.mixins import (
    BinanceCOINMMixin,
    BinanceCOINMTESTMixin,
    BinanceSpotMixin,
    BinanceUSDSMMixin,
    BinanceUSDSMTESTMixin,
)
from yarl import URL

T = TypeVar("T", bound=BinanceDataStoreBase)


class BinanceTickerStore(TickerStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TickerItem":
        return self._itemize(data["s"].upper(), float(data["c"]))


class BinanceTradesStore(TradesStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TradesItem":
        return self._itemize(
            str(data["a"]),
            data["s"].upper(),
            "SELL" if data["m"] else "BUY",
            float(data["p"]),
            float(data["q"]),
            pd.to_datetime(data["T"], unit="ms", utc=True),
        )


class BinanceOrderbookStore(OrderbookStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderbookItem":
        return self._itemize(
            data["s"].upper(), data["S"], float(data["p"]), float(data["q"])
        )


class BinanceOrderStore(OrderStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderItem":
        return self._itemize(
            str(data["i"]),
            data["s"].upper(),
            data["S"],
            float(data["p"]),
            float(data["q"]) - float(data["z"]),
            data["o"],
        )


class BinanceExecutionStore(ExecutionStore):
    """対応ストアなし"""

    def _on_msg(self, msg: "Item"):
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
                    item["s"].upper(),
                    item["S"],
                    float(item["L"]),
                    float(item["l"]),
                    pd.to_datetime(item["T"], unit="ms", utc=True),
                )
                self._insert([{**item, "info": {"data": msg, "source": None}}])


class BinancePositionStore(PositionStore):
    _KEYS = ["symbol", "ps"]

    def _get_operation(self, change: "StoreChange") -> str:
        if change.data["ps"] == "BOTH":
            if float(change.data["pa"]) == 0:
                return "_delete"
            else:
                return f"_{change.operation}"
        else:
            return f"_{change.operation}"

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "PositionItem":
        size = float(data["pa"])

        if data["ps"] == "BOTH":
            if size == 0:
                side = None
            elif size > 0:
                side = "BUY"
            else:
                side = "SELL"
        else:
            side = "BUY" if data["ps"] == "LONG" else "SELL"

        return self._itemize(
            data["s"].upper(),
            side,
            float(data["ep"]),
            abs(size),
            ps=data["ps"],
        )


class _BinanceDataStoreWrapper(DataStoreWrapper[T]):
    _TICKER_STORE = (BinanceTickerStore, "ticker")
    _TRADES_STORE = (BinanceTradesStore, "trade")
    _ORDERBOOK_STORE = (BinanceOrderbookStore, "orderbook")
    _ORDER_STORE = (BinanceOrderStore, "order")
    _EXECUTION_STORE = (BinanceExecutionStore, None)
    _POSITION_STORE = (BinancePositionStore, "position")

    def _parse_connect_send(
        self, endpoint: str, send: any, client: pybotters.Client
    ) -> dict[str, list[any]]:
        subscribe_list = super()._parse_connect_send(endpoint, send, client)

        for endpoint, sends in subscribe_list.items():
            for i, send in enumerate(sends):
                new_params = []
                for p in set(send["params"]):
                    if p == "LISTEN_KEY":
                        if self.store.listenkey is None:
                            import pybotters_wrapper as pbw
                            from yarl import URL

                            api = pbw.create_api(self.exchange, client)
                            _, url, _ = self._INITIALIZE_CONFIG["token"]
                            resp = api.spost(url)
                            data = resp.json()
                            key = data["listenKey"]
                            self.store.listenkey = key
                            asyncio.create_task(
                                self.store._listenkey(URL(resp.url), client._session)
                            )
                            self.log(
                                "`listenkey` got automatically initialized. ", "warning"
                            )
                        new_params.append(self.store.listenkey)
                    else:
                        new_params.append(p)
                subscribe_list[endpoint][i]["params"] = new_params

        return subscribe_list


class BinanceSpotDataStoreWrapper(
    _BinanceDataStoreWrapper[BinanceSpotDataStore], BinanceSpotMixin
):
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
        url: str,
        params_or_data: dict | None = None,
        **kwargs,
    ):
        from .api import BinanceSpotAPI

        kwargs = kwargs or {}
        if URL(url).path in BinanceSpotAPI._PUBLIC_ENDPOINTS:
            kwargs["auth"] = None
        return await super()._initialize_request(
            client, method, url, params_or_data, **kwargs
        )


class BinanceUSDSMDataStoreWrapper(
    BinanceUSDSMMixin, _BinanceDataStoreWrapper[BinanceUSDSMDataStore]
):
    _WEBSOCKET_CHANNELS = BinanceUSDSMWebsocketChannels
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/fapi/v1/listenKey", None),
        "token_private": ("POST", "/fapi/v1/listenKey", None),
        "orderbook": ("GET", "/fapi/v1/depth", ["symbol"]),
        "order": ("GET", "/fapi/v1/openOrders", None),
        "position": ("GET", "/fapi/v2/positionRisk", None),
    }
    _WRAP_STORE = BinanceUSDSMDataStore


class BinanceUSDSMTESTDataStoreWrapper(
    BinanceUSDSMTESTMixin, _BinanceDataStoreWrapper[BinanceUSDSMDataStore]
):
    _WEBSOCKET_CHANNELS = BinanceUSDSMTESTWebsocketChannels

    _INITIALIZE_CONFIG = {
        "token": ("POST", "/fapi/v1/listenKey", None),
        "token_private": ("POST", "/fapi/v1/listenKey", None),
        "orderbook": ("GET", "/fapi/v1/depth", ["symbol"]),
        "order": ("GET", "/fapi/v1/openOrders", None),
        "position": ("GET", "/fapi/v2/positionRisk", None)
    }
    _WRAP_STORE = BinanceUSDSMDataStore


class BinanceCOINMDataStoreWrapper(
    _BinanceDataStoreWrapper[BinanceCOINMDataStore], BinanceCOINMMixin
):
    _WEBSOCKET_CHANNELS = BinanceCOINMWebsocketChannels
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/dapi/v1/listenKey", None),
        "token_private": ("POST", "/dapi/v1/listenKey", None),
        "orderbook": ("GET", "/dapi/v1/depth", ["symbol"]),
        "order": ("GET", "/dapi/v1/openOrders", None),
        "position": ("GET", "/dapi/v1/positionRisk", None)
    }
    _WRAP_STORE = BinanceCOINMDataStore


class BinanceCOINMTESTDataStoreWrapper(
    _BinanceDataStoreWrapper[BinanceCOINMDataStore], BinanceCOINMTESTMixin
):
    _WEBSOCKET_CHANNELS = BinanceCOINMTESTWebsocketChannels
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/dapi/v1/listenKey", None),
        "token_private": ("POST", "/dapi/v1/listenKey", None),
        "orderbook": ("GET", "/dapi/v1/depth", ["symbol"]),
        "order": ("GET", "/dapi/v1/openOrders", None),
        "position": ("GET", "/dapi/v1/positionRisk", None)
    }
    _WRAP_STORE = BinanceCOINMDataStore
