from __future__ import annotations

import pandas as pd
from pybotters.models.okx import OKXDataStore

from pybotters_wrapper.core import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
)
from pybotters_wrapper.okx import OKXWebsocketChannels
from pybotters_wrapper.utils.mixins import OKXMixin


class OKXTickerStore(TickerStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TickerItem":
        return self._itemize(data["instId"], float(data["last"]))


class OKXTradesStore(TradesStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TradesItem":
        return self._itemize(
            data["tradeId"],
            data["instId"],
            data["side"].upper(),
            float(data["px"]),
            float(data["sz"]),
            pd.to_datetime(data["ts"], unit="ms", utc=True),
        )


class OKXOrderbookStore(OrderbookStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "OrderbookItem":
        return self._itemize(
            data["instId"],
            "SELL" if data["side"] == "asks" else "BUY",
            float(data["px"]),
            float(data["sz"])
        )


class OKXDataStoreWrapper(OKXMixin, DataStoreWrapper[OKXDataStore]):
    _WRAP_STORE = OKXDataStore
    _WEBSOCKET_CHANNELS = OKXWebsocketChannels
    _TICKER_STORE = (OKXTickerStore, "tickers")
    _TRADES_STORE = (OKXTradesStore, "trades")
    _ORDERBOOK_STORE = (OKXOrderbookStore, "books")
