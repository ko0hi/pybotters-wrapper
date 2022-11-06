import pandas as pd
from pybotters.models.bitflyer import bitFlyerDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.common.store import TickerStore, TradesStore, OrderbookStore
from pybotters_wrapper.bitflyer import bitFlyerWebsocketChannels


class bitFlyerTickerStore(TickerStore):
    def _transform_data(self, change: 'StoreChange') -> 'TickerItem':
        data = change.data
        return {
            "symbol": data["product_code"],
            "price": data["ltp"],
        }


class bitFlyerTradesStore(TradesStore):
    def _transform_data(self, change: 'StoreChange') -> 'TradesItem':
        data = change.data
        side = data["side"]
        if side:
            order_id = side.lower() + "_child_order_acceptance_id"
        else:
            order_id = data["buy_child_order_acceptance_id"]
        return {
            "id": order_id,
            "symbol": data["product_code"],
            "side": side,
            "price": data["price"],
            "size": data["size"],
            "timestamp": pd.to_datetime(data["exec_date"])
        }


class bitFlyerOrderbookStore(OrderbookStore):
    def _transform_data(self, change: 'StoreChange') -> 'OrderbookItem':
        data = change.data
        return {
            "symbol": data["product_code"],
            "side": data["side"],
            "price": data["price"],
            "size": data["size"]
        }


class bitFlyerDataStoreManagerWrapper(DataStoreManagerWrapper[bitFlyerDataStore]):
    _SOCKET_CHANNELS_CLS = bitFlyerWebsocketChannels
    _TICKER_STORE = (bitFlyerTickerStore, "ticker")
    _TRADES_STORE = (bitFlyerTradesStore, "executions")
    _ORDERBOOK_STORE = (bitFlyerOrderbookStore, "board")

    def __init__(self, store: bitFlyerDataStore = None, *args, **kwargs):
        super(bitFlyerDataStoreManagerWrapper, self).__init__(store or bitFlyerDataStore())

