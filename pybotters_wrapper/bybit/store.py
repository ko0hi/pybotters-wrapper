import pandas as pd
from pybotters.models.bybit import BybitUSDTDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.common.store import TickerStore, TradesStore, OrderbookStore
from pybotters_wrapper.bybit import BybitUSDTWebsocketChannels


class BybitUSDTTickerStore(TickerStore):
    def _transform_data(self, change: 'StoreChange') -> 'TickerItem':
        data = change.data
        return {
            "symbol": data["symbol"],
            "price": data["last_price"]
        }


class BybitUSDTTradesStore(TradesStore):
    def _transform_data(self, change: 'StoreChange') -> 'TradesItem':
        data = change.data
        return {
            "id": data["trade_id"],
            "symbol": data["symbol"],
            "side": data["side"].upper(),
            "price": float(data["price"]),
            "size": data["size"],
            "timestamp": pd.to_datetime(data["timestamp"])
        }


class BybitUSDTOrderbookStore(OrderbookStore):
    def _transform_data(self, change: 'StoreChange') -> 'OrderbookItem':
        data = change.data
        return {
            "symbol": data["symbol"],
            "side": data["side"].upper(),
            "price": float(data["price"]),
            "size": float(data["size"])
        }


class BybitUSDTDataStoreManagerWrapper(DataStoreManagerWrapper[BybitUSDTDataStore]):
    _SOCKET_CHANNELS_CLS = BybitUSDTWebsocketChannels
    _TICKER_STORE = (BybitUSDTTickerStore, "instrument")
    _TRADES_STORE = (BybitUSDTTradesStore, "trade")
    _ORDERBOOK_STORE = (BybitUSDTOrderbookStore, "orderbook")

    def __init__(self, store: BybitUSDTDataStore = None):
        super(BybitUSDTDataStoreManagerWrapper, self).__init__(
            store or BybitUSDTDataStore()
        )
