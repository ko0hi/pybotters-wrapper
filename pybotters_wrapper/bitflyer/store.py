import pandas as pd
from pybotters.models.bitflyer import bitFlyerDataStore
from pybotters_wrapper.common import (
    DataStoreManagerWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
)
from pybotters_wrapper.bitflyer import bitFlyerWebsocketChannels


class bitFlyerTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "symbol": d["product_code"],
            "price": d["ltp"],
        }


class bitFlyerTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        side = d["side"]
        if side:
            order_id = side.lower() + "_child_order_acceptance_id"
        else:
            order_id = d["buy_child_order_acceptance_id"]
        return {
            "id": order_id,
            "symbol": d["product_code"],
            "side": side,
            "price": d["price"],
            "size": d["size"],
            "timestamp": pd.to_datetime(d["exec_date"]),
        }


class bitFlyerOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "symbol": d["product_code"],
            "side": d["side"],
            "price": d["price"],
            "size": d["size"],
        }




class bitFlyerDataStoreManagerWrapper(DataStoreManagerWrapper[bitFlyerDataStore]):
    _SOCKET_CHANNELS_CLS = bitFlyerWebsocketChannels
    _TICKER_STORE = (bitFlyerTickerStore, "ticker")
    _TRADES_STORE = (bitFlyerTradesStore, "executions")
    _ORDERBOOK_STORE = (bitFlyerOrderbookStore, "board")

    def __init__(self, store: bitFlyerDataStore = None, *args, **kwargs):
        super(bitFlyerDataStoreManagerWrapper, self).__init__(
            store or bitFlyerDataStore()
        )
