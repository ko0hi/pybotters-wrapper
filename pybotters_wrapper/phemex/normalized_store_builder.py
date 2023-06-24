import uuid

import pandas as pd
from pybotters.models.phemex import PhemexDataStore

from ..core import (
    NormalizedStoreBuilder,
    PositionStore,
    ExecutionStore,
    OrderStore,
    OrderbookStore,
    TradesStore,
    TickerStore,
)


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
        pass

    def execution(self) -> ExecutionStore:
        pass

    def position(self) -> PositionStore:
        pass
