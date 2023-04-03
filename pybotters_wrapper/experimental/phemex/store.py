from __future__ import annotations

import uuid

import pandas as pd
from pybotters.models.phemex import PhemexDataStore

from pybotters_wrapper.core import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
)
from pybotters_wrapper.phemex import PhemexWebsocketChannels
from pybotters_wrapper.utils.mixins import PhemexMixin


class PhemexTickerStore(TickerStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TickerItem":
        return self._itemize(data["symbol"], float(data["last"]))


class PhemexTradesStore(TradesStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TradesItem":
        return self._itemize(
            str(uuid.uuid4()),
            data["symbol"],
            data["side"].upper(),
            data["price"],
            data["size"],
            pd.to_datetime(data["timestamp"], unit="ns", utc=True),
        )


class PhemexOrderbookStore(OrderbookStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "OrderbookItem":
        return self._itemize(data["symbol"], data["side"], data["price"], data["size"])


class PhemexDataStoreWrapper(PhemexMixin, DataStoreWrapper[PhemexDataStore]):
    _WRAP_STORE = PhemexDataStore
    _WEBSOCKET_CHANNELS = PhemexWebsocketChannels
    _TICKER_STORE = (PhemexTickerStore, "ticker")
    _TRADES_STORE = (PhemexTradesStore, "trade")
    _ORDERBOOK_STORE = (PhemexOrderbookStore, "orderbook")
