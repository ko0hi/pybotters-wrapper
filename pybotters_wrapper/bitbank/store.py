from __future__ import annotations

from typing import Callable

import pandas as pd
import pybotters
from pybotters import bitbankDataStore
from pybotters.store import DataStore
from pybotters.typedefs import WsBytesHandler, WsStrHandler
from pybotters.ws import WebSocketRunner
from pybotters_wrapper.bitbank import bitbankWebsocketChannels
from pybotters_wrapper.core.store import (
    DataStoreWrapper,
    OrderbookItem,
    OrderbookStore,
    TickerItem,
    TickerStore,
    TradesItem,
    TradesStore,
)
from pybotters_wrapper.utils.mixins import bitbankMixin


class bitbankTickerStore(TickerStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TickerItem":
        return self._itemize(data["pair"], float(data["last"]))


class bitbankTradesStore(TradesStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TradesItem":
        return self._itemize(
            str(data["transaction_id"]),
            data["pair"],
            data["side"].upper(),
            float(data["price"]),
            float(data["amount"]),
            pd.to_datetime(data["executed_at"], utc=True),
        )


class bitbankOrderbookStore(OrderbookStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "OrderbookItem":
        return self._itemize(
            data["pair"], data["side"].upper(), float(data["price"]), float(data["size"])
        )


class bitbankDataStoreWrapper(bitbankMixin, DataStoreWrapper[bitbankDataStore]):
    _WRAP_STORE = bitbankDataStore
    _WEBSOCKET_CHANNELS = bitbankWebsocketChannels
    _TICKER_STORE = (bitbankTickerStore, "ticker")
    _TRADES_STORE = (bitbankTradesStore, "transactions")
    _ORDERBOOK_STORE = (bitbankOrderbookStore, "depth")

    async def connect(
        self,
        client: "pybotters.Client",
        *,
        endpoint: str = None,
        send: any = None,
        hdlr: "WsStrHandler" | "WsBytesHandler" = None,
        waits: list["DataStore" | str] = None,
        send_type: str = "json",
        hdlr_type: str = "json",
        auto_reconnect: bool = False,
        on_reconnection: "Callable" = None,
        **kwargs,
    ) -> dict[str, "WebSocketRunner"]:

        return await super().connect(
            client,
            endpoint=endpoint,
            send=send,
            hdlr=hdlr,
            waits=waits,
            send_type="str",
            hdlr_type="str",
            auto_reconnect=auto_reconnect,
            on_reconnection=on_reconnection,
            **kwargs,
        )
