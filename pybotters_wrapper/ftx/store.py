import pandas as pd
from pybotters.models.ftx import FTXDataStore

from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.common.store import TickerStore, TradesStore, OrderbookStore
from pybotters_wrapper.ftx import FTXWebsocketChannels


class FTXTickerStore(TickerStore):
    def _transform_data(self, change: 'StoreChange') -> 'TickerItem':
        data = change.data
        return {"symbol": data["market"], "price": data["last"]}


class FTXTradesStore(TradesStore):
    def _transform_data(self, change: 'StoreChange') -> 'TradesItem':
        data = change.data
        return {
            "id": data["id"],
            "symbol": data["market"],
            "side": data["side"].upper(),
            "price": data["price"],
            "size": data["size"],
            "timestamp": pd.to_datetime(data["time"])
        }


class FTXOrderbookStore(OrderbookStore):
    def _transform_data(self, change: 'StoreChange') -> 'OrderbookItem':
        data = change.data
        return {
            "symbol": data["market"],
            "side": data["side"].upper(),
            "price": data["price"],
            "size": data["size"]
        }


class FTXDataStoreManagerWrapper(DataStoreManagerWrapper[FTXDataStore]):
    _SOCKET_CHANNELS_CLS = FTXWebsocketChannels
    _TICKER_STORE = (FTXTickerStore, "ticker")
    _TRADES_STORE = (FTXTradesStore, "trades")
    _ORDERBOOK_STORE = (FTXOrderbookStore, "orderbook")

    def __init__(self, store: FTXDataStore = None):
        super(FTXDataStoreManagerWrapper, self).__init__(store or FTXDataStore())

