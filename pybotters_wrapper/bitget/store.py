import uuid

import pandas as pd

from pybotters.models.bitget import BitgetDataStore
from pybotters_wrapper.bitget import BitgetWebsocketChannels
from pybotters_wrapper.common import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
)


class BitgetTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["instId"], float(d["last"]))


class BitgetTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            id=str(uuid.uuid4()),
            symbol=d["instId"],
            side=d["side"].upper(),
            price=d["price"],
            size=d["size"],
            timestamp=pd.to_datetime(d["ts"], unit="ms"),
        )


class BitgetOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            symbol=d["instId"], side=d["side"].upper(), price=d["price"], size=d["size"]
        )


class BitgetDataStoreWrapper(DataStoreWrapper[BitgetDataStore]):
    _WRAP_STORE = BitgetDataStore
    _WEBSOCKET_CHANNELS = BitgetWebsocketChannels
    _TICKER_STORE = (BitgetTickerStore, "ticker")
    _TRADES_STORE = (BitgetTradesStore, "trade")
    _ORDERBOOK_STORE = (BitgetOrderbookStore, "orderbook")
