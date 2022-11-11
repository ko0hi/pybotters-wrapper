import pandas as pd
from pybotters.models.ftx import FTXDataStore

from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.common.store import (
    TickerStore,
    TradesStore,
    OrderbookStore,
    OrderStore,
    ExecutionStore,
    PositionStore
)
from pybotters_wrapper.ftx import FTXWebsocketChannels


class FTXTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {"symbol": d["market"], "price": d["last"]}


class FTXTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "id": d["id"],
            "symbol": d["market"],
            "side": d["side"].upper(),
            "price": d["price"],
            "size": d["size"],
            "timestamp": pd.to_datetime(d["time"]),
        }


class FTXOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return {
            "symbol": d["market"],
            "side": d["side"].upper(),
            "price": d["price"],
            "size": d["size"],
        }


class FTXOrderStore(OrderStore):
    def _normalize(self, d: dict, op: str) -> "OrderItem":
        return {
            "id": d["id"],
            "symbol": d["market"],
            "side": d["side"].upper(),
            "price": d["price"],
            "size": d["remainingSize"],
            "type": d["type"].upper()
        }


class FTXExecutionStore(ExecutionStore):
    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        return {
            "id": str(d["orderId"]),
            "symbol": d["market"],
            "side": d["side"].upper(),
            "price": d["price"],
            "size": d["size"],
            "timestamp": pd.to_datetime(d["time"]),
        }


class FTXPositionStore(PositionStore):
    def _normalize(self, d: dict, op: str) -> "PositionItem":
        if d["netSize"] == 0:
            side = None
        elif d["netSize"] > 0:
            side = "BUY"
        else:
            side = "SELL"

        return {
            "symbol": d["future"],
            "price": d["entryPrice"],
            "side": side,
            "size": d["size"]
        }


class FTXDataStoreWrapper(DataStoreWrapper[FTXDataStore]):
    _SOCKET_CHANNELS_CLS = FTXWebsocketChannels
    _TICKER_STORE = (FTXTickerStore, "ticker")
    _TRADES_STORE = (FTXTradesStore, "trades")
    _ORDERBOOK_STORE = (FTXOrderbookStore, "orderbook")
    _ORDER_STORE = (FTXOrderStore, "orders")
    _EXECUTION_STORE = (FTXExecutionStore, "fills")
    _POSITION_STORE = (FTXPositionStore, "positions")

    def __init__(self, store: FTXDataStore = None):
        super(FTXDataStoreWrapper, self).__init__(store or FTXDataStore())
