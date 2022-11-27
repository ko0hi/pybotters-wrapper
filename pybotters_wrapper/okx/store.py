from __future__ import annotations

import pandas as pd
from pybotters.models.okx import OKXDataStore

from pybotters_wrapper.common import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
)
from pybotters_wrapper.okx import OKXWebsocketChannels
from pybotters_wrapper.utils.mixins import OKXMixin

class OKXTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["instId"], float(d["last"]))


class OKXTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            d["tradeId"],
            d["instId"],
            d["side"].upper(),
            float(d["px"]),
            float(d["sz"]),
            pd.to_datetime(d["ts"], unit="ms", utc=True),
        )


class OKXOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            d["instId"],
            "SELL" if d["side"] == "asks" else "BUY",
            float(d["px"]),
            float(d["sz"])
        )


class OKXDataStoreWrapper(OKXMixin, DataStoreWrapper[OKXDataStore]):
    _WRAP_STORE = OKXDataStore
    _WEBSOCKET_CHANNELS = OKXWebsocketChannels
    _TICKER_STORE = (OKXTickerStore, "tickers")
    _TRADES_STORE = (OKXTradesStore, "trades")
    _ORDERBOOK_STORE = (OKXOrderbookStore, "books")
