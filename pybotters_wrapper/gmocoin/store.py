import uuid
import pandas as pd

from pybotters.models.gmocoin import GMOCoinDataStore
from pybotters_wrapper.common import DataStoreManagerWrapper
from pybotters_wrapper.common.store import TickerStore, TradesStore, OrderbookStore
from pybotters_wrapper.gmocoin import GMOWebsocketChannels


class GMOCoinTickerStore(TickerStore):
    def _transform_data(self, change: "StoreChange") -> "TickerItem":
        data = change.data
        return {"symbol": str(data["symbol"]), "price": float(data["last"])}


class GMOCoinTradesStore(TradesStore):
    def _transform_data(self, change: "StoreChange") -> "TradesItem":
        data = change.data
        return {
            "id": uuid.uuid4(),
            "symbol": str(data["symbol"]),
            "side": str(data["side"]),
            "price": float(data["price"]),
            "size": float(data["size"]),
            "timestamp": pd.to_datetime(data["timestamp"]),
        }


class GMOCoinOrderbookStore(OrderbookStore):
    def _transform_data(self, change: 'StoreChange') -> 'OrderbookItem':
        data = change.data
        return {
            "symbol": str(data["symbol"]),
            "side": str(data["side"]),
            "price": float(data["price"]),
            "size": float(data["size"])
        }


class GMOCoinDataStoreManagerWrapper(DataStoreManagerWrapper[GMOCoinDataStore]):
    _SOCKET_CHANNELS_CLS = GMOWebsocketChannels
    _TICKER_STORE = (GMOCoinTickerStore, "ticker")
    _TRADES_STORE = (GMOCoinTradesStore, "trades")
    _ORDERBOOK_STORE = GMOCoinOrderbookStore, "orderbooks"

    def __init__(self, store: GMOCoinDataStore = None, *args, **kwargs):
        super(GMOCoinDataStoreManagerWrapper, self).__init__(
            store or GMOCoinDataStore(), *args, **kwargs
        )

    @classmethod
    def _parse_trades_watch_item(cls, item: "Item") -> dict:
        return {
            "timestamp": pd.to_datetime(item["timestamp"], utc=True),
            "symbol": str(item["symbol"].name),
            "side": str(item["side"].name),
            "size": float(item["size"]),
            "price": float(item["price"]),
            "info": item,
        }
