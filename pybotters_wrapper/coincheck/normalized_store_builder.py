import pandas as pd
from pybotters import CoincheckDataStore

from ..core import (
    NormalizedStoreBuilder,
    PositionStore,
    ExecutionStore,
    OrderStore,
    OrderbookStore,
    TradesStore,
    TickerStore,
)


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
        pass

    def execution(self) -> ExecutionStore:
        pass

    def position(self) -> PositionStore:
        pass
