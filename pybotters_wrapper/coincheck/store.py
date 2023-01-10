from __future__ import annotations

import pandas as pd
from pybotters.models.coincheck import CoincheckDataStore
from pybotters_wrapper.core.store import (
    DataStoreWrapper,
    OrderbookItem,
    OrderbookStore,
    TickerItem,
    TickerStore,
    TradesItem,
    TradesStore,
)
from pybotters_wrapper.utils.mixins import CoincheckMixin

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
            pd.to_datetime(int(d["timestamp"]), unit="s"),
        )


class CoincheckOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            d["pair"],
            "BUY" if d["side"] == "bids" else "SELL",
            float(d["rate"]),
            float(d["amount"]),
        )


class CoincheckDataStoreWrapper(CoincheckMixin, DataStoreWrapper[CoincheckDataStore]):
    _WRAP_STORE = CoincheckDataStore
    _WEBSOCKET_CHANNELS = CoinCheckWebsocketChannels
    _TICKER_STORE = (CoincheckTickerStore, "trades")
    _TRADES_STORE = (CoincheckTradeStore, "trades")
    _ORDERBOOK_STORE = (CoincheckOrderbookStore, "orderbook")
