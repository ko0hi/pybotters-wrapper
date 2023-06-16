import uuid

import pandas as pd
from pybotters import GMOCoinDataStore

from ..core import (
    NormalizedStoreBuilder,
    PositionStore,
    ExecutionStore,
    OrderStore,
    OrderbookStore,
    TradesStore,
    TickerStore,
)


class GMOCoinNormalizedStoreBuilder(NormalizedStoreBuilder[GMOCoinDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"].name,
                "price": lambda store, o, s, d: float(d["last"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.executions,
            mapper={
                "id": str(uuid.uuid4()),
                "symbol": lambda store, o, s, d: d["symbol"].name,
                "side": lambda store, o, s, d: d["side"].name,
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["timestamp"], utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbooks,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"].name,
                "side": lambda store, o, s, d: d["side"].name,
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
            },
        )

    def order(self) -> OrderStore:
        return OrderStore(
            self._store.orders,
            mapper={
                "id": lambda store, o, s, d: str(d["order_id"]),
                "symbol": lambda store, o, s, d: d["symbol"].name,
                "side": lambda store, o, s, d: d["side"].name,
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "type": lambda store, o, s, d: d["execution_type"].name,
            },
        )

    def execution(self) -> ExecutionStore:
        return ExecutionStore(
            self._store.executions,
            mapper={
                "id": lambda store, o, s, d: str(d["order_id"]),
                "symbol": lambda store, o, s, d: d["symbol"].name,
                "side": lambda store, o, s, d: d["side"].name,
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["timestamp"], utc=True
                ),
            },
        )

    def position(self) -> PositionStore:
        return PositionStore(
            self._store.positions,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"].name,
                "side": lambda store, o, s, d: d["side"].name,
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                # キーを一致させるため
                "position_id": lambda store, o, s, d: d["position_id"],
            },
            keys=["symbol", "side", "position_id"],
        )
