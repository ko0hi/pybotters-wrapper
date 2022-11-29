from __future__ import annotations

import pandas as pd
from pybotters.models.gmocoin import GMOCoinDataStore
from pybotters_wrapper.common.store import (
    DataStoreWrapper,
    OrderbookItem,
    OrderbookStore,
    TickerItem,
    TickerStore,
    TradesItem,
    TradesStore,
)
from pybotters_wrapper.gmocoin import GMOWebsocketChannels
from pybotters_wrapper.utils.mixins import GMOCoinMixin


class GMOCoinTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["symbol"].name, float(d["last"]))


class GMOCoinTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            hash(tuple(d)),
            d["symbol"].name,
            d["side"].name,
            float(d["price"]),
            float(d["size"]),
            pd.to_datetime(d["timestamp"]),
        )


class GMOCoinOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            d["symbol"].name, d["side"].name, float(d["price"]), float(d["size"])
        )


class GMOCoinDataStoreWrapper(GMOCoinMixin, DataStoreWrapper[GMOCoinDataStore]):
    _WRAP_STORE = GMOCoinDataStore
    _WEBSOCKET_CHANNELS = GMOWebsocketChannels
    _TICKER_STORE = (GMOCoinTickerStore, "ticker")
    _TRADES_STORE = (GMOCoinTradesStore, "trades")
    _ORDERBOOK_STORE = (GMOCoinOrderbookStore, "orderbooks")
