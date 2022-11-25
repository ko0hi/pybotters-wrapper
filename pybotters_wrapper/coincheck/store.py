from __future__ import annotations

import pandas as pd
from pybotters.models.coincheck import CoincheckDataStore

from pybotters_wrapper.common import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
)
from .socket import CoinCheckWebsocketChannels


class CoincheckTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["pair"], float(d["rate"]))


class CoincheckTradeStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            str(d["id"]),
            d["pair"],
            d["side"].upper(),
            float(d["rate"]),
            float(d["amount"]),
            pd.Timestamp.utcnow()
        )


class CoincheckOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            None,
            "BUY" if d["side"] == "bids" else "SELL",
            float(d["rate"]),
            float(d["amount"])
        )


class CoincheckDataStoreWrapper(DataStoreWrapper[CoincheckDataStore]):
    _NAME = "coincheck"
    _WRAP_STORE = CoincheckDataStore
    _WEBSOCKET_CHANNELS = CoinCheckWebsocketChannels
    _TICKER_STORE = (CoincheckTickerStore, "trades")
    _TRADES_STORE = (CoincheckTradeStore, "trades")
    _ORDERBOOK_STORE = (CoincheckOrderbookStore, "orderbook")
