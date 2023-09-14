import uuid

import pandas as pd
from pybotters.models.phemex import PhemexDataStore

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


class PhemexNormalizedStoreBuilder(NormalizedStoreBuilder[PhemexDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "price": lambda store, o, s, d: float(d["last"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.trade,
            mapper={
                "id": lambda store, o, s, d: str(uuid.uuid4()),
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["timestamp"], unit="ns", utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbook,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"],
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
            },
        )

    def order(self) -> OrderStore:
        raise UnsupportedStoreError("Phemex does not support order store")

    def execution(self) -> ExecutionStore:
        raise UnsupportedStoreError("Phemex does not support execution store")

    def position(self) -> PositionStore:
        raise UnsupportedStoreError("Phemex does not support position store")
