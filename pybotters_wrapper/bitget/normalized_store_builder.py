import uuid

import pandas as pd
from pybotters import BitgetDataStore

from ..core import (
    ExecutionStore,
    NormalizedStoreBuilder,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TickerStore,
    TradesStore,
)
from ..exceptions import UnsupportedStoreError


class BitgetNormalizedStoreBuilder(NormalizedStoreBuilder[BitgetDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["instId"],
                "price": lambda store, o, s, d: float(d["last"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.trade,
            mapper={
                "id": lambda store, o, s, d: str(uuid.uuid4()),
                "symbol": lambda store, o, s, d: d["instId"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["ts"], unit="ms", utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbook,
            mapper={
                "symbol": lambda store, o, s, d: d["instId"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: d["price"],
                "size": lambda store, o, s, d: d["size"],
            },
        )

    def order(self) -> OrderStore:
        raise UnsupportedStoreError("order")

    def execution(self) -> ExecutionStore:
        raise UnsupportedStoreError("execution")

    def position(self) -> PositionStore:
        raise UnsupportedStoreError("position")
