from __future__ import annotations

import uuid

import pandas as pd
from pybotters.models.bitget import BitgetDataStore
from pybotters_wrapper.bitget import BitgetWebsocketChannels
from pybotters_wrapper.core.store import (
    DataStoreWrapper,
    OrderbookItem,
    OrderbookStore,
    TickerItem,
    TickerStore,
    TradesItem,
    TradesStore,
)
from pybotters_wrapper.utils.mixins import BitgetMixin


class BitgetTickerStore(TickerStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TickerItem":
        return self._itemize(data["instId"], float(data["last"]))


class BitgetTradesStore(TradesStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "TradesItem":
        return self._itemize(
            id=str(uuid.uuid4()),
            symbol=data["instId"],
            side=data["side"].upper(),
            price=data["price"],
            size=data["size"],
            timestamp=pd.to_datetime(data["ts"], unit="ms", utc=True),
        )


class BitgetOrderbookStore(OrderbookStore):
    def _normalize(self, store: "DataStore", operation: str, source: dict, data: dict) -> "OrderbookItem":
        return self._itemize(
            symbol=data["instId"], side=data["side"].upper(), price=data["price"], size=data["size"]
        )


class BitgetDataStoreWrapper(BitgetMixin, DataStoreWrapper[BitgetDataStore]):
    _WRAP_STORE = BitgetDataStore
    _WEBSOCKET_CHANNELS = BitgetWebsocketChannels
    _TICKER_STORE = (BitgetTickerStore, "ticker")
    _TRADES_STORE = (BitgetTradesStore, "trade")
    _ORDERBOOK_STORE = (BitgetOrderbookStore, "orderbook")
