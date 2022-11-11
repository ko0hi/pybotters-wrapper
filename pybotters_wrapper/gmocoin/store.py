import pandas as pd

from pybotters.models.gmocoin import GMOCoinDataStore
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.common.store import TickerStore, TradesStore, OrderbookStore
from pybotters_wrapper.gmocoin import GMOWebsocketChannels


class GMOCoinTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {"symbol": str(d["symbol"]), "price": float(d["last"])}


class GMOCoinTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "id": hash(tuple(d)),
            "symbol": str(d["symbol"]),
            "side": str(d["side"]),
            "price": float(d["price"]),
            "size": float(d["size"]),
            "timestamp": pd.to_datetime(d["timestamp"]),
        }


class GMOCoinOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "symbol": str(d["symbol"]),
            "side": str(d["side"]),
            "price": float(d["price"]),
            "size": float(d["size"]),
        }


class GMOCoinDataStoreWrapper(DataStoreWrapper[GMOCoinDataStore]):
    _SOCKET_CHANNELS_CLS = GMOWebsocketChannels
    _TICKER_STORE = (GMOCoinTickerStore, "ticker")
    _TRADES_STORE = (GMOCoinTradesStore, "trades")
    _ORDERBOOK_STORE = GMOCoinOrderbookStore, "orderbooks"

    def __init__(self, store: GMOCoinDataStore = None, *args, **kwargs):
        super(GMOCoinDataStoreWrapper, self).__init__(
            store or GMOCoinDataStore()
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
