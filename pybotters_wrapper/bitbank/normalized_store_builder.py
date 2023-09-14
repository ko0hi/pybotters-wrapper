import pandas as pd
from pybotters import bitbankDataStore

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


class bitbankNormalizedStoreBuilder(NormalizedStoreBuilder[bitbankDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["pair"],
                "price": lambda store, o, s, d: float(d["last"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.transactions,
            mapper={
                "id": lambda store, o, s, d: str(d["transaction_id"]),
                "symbol": lambda store, o, s, d: d["pair"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["amount"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["executed_at"], utc=True, unit="ms"
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.depth,
            mapper={
                "symbol": lambda store, o, s, d: d["pair"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
            },
        )

    def order(self) -> OrderStore:
        raise UnsupportedStoreError("order")

    def execution(self) -> ExecutionStore:
        raise UnsupportedStoreError("execution")

    def position(self) -> PositionStore:
        raise UnsupportedStoreError("position")
