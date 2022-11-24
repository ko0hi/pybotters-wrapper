import uuid

import pandas as pd

from pybotters.models.phemex import PhemexDataStore
from pybotters_wrapper.common import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
)
from pybotters_wrapper.phemex import PhemexWebsocketChannels


class PhemexTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["symbol"], float(d["last"]))


class PhemexTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            str(uuid.uuid4()),
            d["symbol"],
            d["side"].upper(),
            d["price"],
            d["size"],
            pd.to_datetime(d["timestamp"], unit="ns"),
        )


class PhemexOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(d["symbol"], d["side"], d["price"], d["size"])


class PhemexDataStoreWrapper(DataStoreWrapper[PhemexDataStore]):
    _NAME = "phemex"
    _WRAP_STORE = PhemexDataStore
    _WEBSOCKET_CHANNELS = PhemexWebsocketChannels
    _TICKER_STORE = (PhemexTickerStore, "ticker")
    _TRADES_STORE = (PhemexTradesStore, "trade")
    _ORDERBOOK_STORE = (PhemexOrderbookStore, "orderbook")
