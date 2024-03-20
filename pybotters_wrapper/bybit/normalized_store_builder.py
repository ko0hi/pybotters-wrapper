import pandas as pd
from pybotters import BybitDataStore

from ..core import (
    ExecutionStore,
    NormalizedStoreBuilder,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TickerStore,
    TradesStore,
)


class BybitNormalizedStoreBuilder(
    NormalizedStoreBuilder[BybitDataStore]
):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "price": lambda store, o, s, d: float(d["lastPrice"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.trade,
            mapper={
                "id": lambda store, o, s, d: d["i"],
                "symbol": lambda store, o, s, d: d["s"],
                "side": lambda store, o, s, d: d["S"].upper(),
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["v"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["T"], unit="ms", utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbook,
            mapper={
                "symbol": lambda store, o, s, d: d["s"],
                "side": lambda store, o, s, d: d["S"].upper(),
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["v"]),
            },
        )

    def order(self) -> OrderStore:
        return OrderStore(
            self._store.order,
            mapper={
                "id": lambda store, o, s, d: d["orderId"],
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: d["qty"],
                "type": lambda store, o, s, d: d["orderType"],
            },
        )

    def execution(self) -> ExecutionStore:
        return ExecutionStore(
            self._store.execution,
            mapper={
                "id": lambda store, o, s, d: d["orderId"],
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["execPrice"]),
                "size": lambda store, o, s, d: d["execQty"],
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["execTime"], unit="ms", utc=True
                ),
            },
            on_watch_get_operation=lambda change: "insert",
        )

    def position(self) -> PositionStore:
        return PositionStore(
            self._store.position,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["entryPrice"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "positionIdx": lambda store, o, s, d: d["positionIdx"],
            },
            keys=["symbol", "positionIdx"],
        )
