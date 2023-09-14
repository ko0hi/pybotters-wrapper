import pandas as pd
from pybotters import CoincheckDataStore

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


class CoincheckNormalizedStoreBuilder(NormalizedStoreBuilder[CoincheckDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.trades,
            mapper={
                "symbol": lambda store, o, s, d: d["pair"],
                "price": lambda store, o, s, d: float(d["rate"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.trades,
            mapper={
                "id": lambda store, o, s, d: str(d["id"]),
                "symbol": lambda store, o, s, d: d["pair"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["rate"]),
                "size": lambda store, o, s, d: float(d["amount"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["timestamp"], unit="s", utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbook,
            mapper={
                "symbol": lambda store, o, s, d: d["pair"],
                "side": lambda store, o, s, d: "BUY" if d["side"] == "bids" else "SELL",
                "price": lambda store, o, s, d: float(d["rate"]),
                "size": lambda store, o, s, d: float(d["amount"]),
            },
        )

    def order(self) -> OrderStore:
        raise UnsupportedStoreError("Coincheck does not support order store")

    def execution(self) -> ExecutionStore:
        raise UnsupportedStoreError("Coincheck does not support execution store")

    def position(self) -> PositionStore:
        raise UnsupportedStoreError("Coincheck does not support position store")
