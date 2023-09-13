import pandas as pd
from pybotters import OKXDataStore

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


class OKXNormalizedStoreBuilder(NormalizedStoreBuilder[OKXDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.tickers,
            mapper={
                "symbol": lambda store, o, s, d: d["instId"],
                "price": lambda store, o, s, d: float(d["last"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.trades,
            mapper={
                "id": lambda store, o, s, d: d["tradeId"],
                "symbol": lambda store, o, s, d: d["instId"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["px"]),
                "size": lambda store, o, s, d: float(d["sz"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["ts"], unit="ms", utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.books,
            mapper={
                "symbol": lambda store, o, s, d: d["instId"],
                "side": lambda store, o, s, d: "SELL" if d["side"] == "asks" else "BUY",
                "price": lambda store, o, s, d: float(d["px"]),
                "size": lambda store, o, s, d: float(d["sz"]),
            },
        )

    def order(self) -> OrderStore:
        raise UnsupportedStoreError("OKX does not support order store")

    def execution(self) -> ExecutionStore:
        raise UnsupportedStoreError("OKX does not support execution store")

    def position(self) -> PositionStore:
        raise UnsupportedStoreError("OKX does not support position store")
