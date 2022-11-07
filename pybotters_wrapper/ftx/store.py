import pandas as pd
from pybotters.models.ftx import FTXDataStore

from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.common.store import TickerStore, TradesStore, OrderbookStore
from pybotters_wrapper.ftx import FTXWebsocketChannels


class FTXTickerStore(TickerStore):
    def _normalize(self, d:  dict, op) -> 'TickerItem':
        return {"symbol": d["market"], "price": d["last"]}


class FTXTradesStore(TradesStore):
    def _normalize(self, d: dict, op) -> 'TradesItem':
        return {
            "id": d["id"],
            "symbol": d["market"],
            "side": d["side"].upper(),
            "price": d["price"],
            "size": d["size"],
            "timestamp": pd.to_datetime(d["time"])
        }


class FTXOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op) -> 'OrderbookItem':
        return {
            "symbol": d["market"],
            "side": d["side"].upper(),
            "price": d["price"],
            "size": d["size"]
        }


class FTXDataStoreManagerWrapper(DataStoreManagerWrapper[FTXDataStore]):
    _SOCKET_CHANNELS_CLS = FTXWebsocketChannels
    _TICKER_STORE = (FTXTickerStore, "ticker")
    _TRADES_STORE = (FTXTradesStore, "trades")
    _ORDERBOOK_STORE = (FTXOrderbookStore, "orderbook")

    def __init__(self, store: FTXDataStore = None):
        super(FTXDataStoreManagerWrapper, self).__init__(store or FTXDataStore())

