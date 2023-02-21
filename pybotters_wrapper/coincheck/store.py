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
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TickerItem":
        return self._itemize(data["pair"], float(data["rate"]))


class CoincheckTradeStore(TradesStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TradesItem":
        return self._itemize(
            str(data["id"]),
            data["pair"],
            data["side"].upper(),
            float(data["rate"]),
            float(data["amount"]),
            pd.to_datetime(int(data["timestamp"]), unit="s", utc=True),
        )


class CoincheckOrderbookStore(OrderbookStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderbookItem":
        return self._itemize(
            data["pair"],
            "BUY" if data["side"] == "bids" else "SELL",
            float(data["rate"]),
            float(data["amount"]),
        )


class CoincheckDataStoreWrapper(CoincheckMixin, DataStoreWrapper[CoincheckDataStore]):
    _WRAP_STORE = CoincheckDataStore
    _WEBSOCKET_CHANNELS = CoinCheckWebsocketChannels
    _TICKER_STORE = (CoincheckTickerStore, "trades")
    _TRADES_STORE = (CoincheckTradeStore, "trades")
    _ORDERBOOK_STORE = (CoincheckOrderbookStore, "orderbook")
