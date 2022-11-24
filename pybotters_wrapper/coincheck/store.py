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
        return self._itemize(symbol=d["pair"], price=float(d["rate"]))


class CoincheckTradeStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            id=str(d["id"]),
            symbol=d["pair"],
            side=d["side"].upper(),
            price=float(d["rate"]),
            size=float(d["amount"]),
            timestamp=pd.Timestamp.utcnow()
        )


class CoincheckOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            symbol=None,
            side="BUY" if d["side"] == "bids" else "SELL",
            price=float(d["rate"]),
            size=float(d["amount"])
        )


class CoincheckDataStoreWrapper(DataStoreWrapper[CoincheckDataStore]):
    _NAME = "coincheck"
    _WRAP_STORE = CoincheckDataStore
    _WEBSOCKET_CHANNELS = CoinCheckWebsocketChannels
    _TICKER_STORE = (CoincheckTickerStore, "trades")
    _TRADES_STORE = (CoincheckTradeStore, "trades")
    _ORDERBOOK_STORE = (CoincheckOrderbookStore, "orderbook")
