import pandas as pd
from pybotters import KuCoinDataStore

from ..core import (
    ExecutionStore,
    NormalizedStoreBuilder,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TickerStore,
    TradesStore,
)


class KuCoinNormalizedStoreBuilder(NormalizedStoreBuilder[KuCoinDataStore]):
    def ticker(self) -> TickerStore:
        def _get_price(_store, _o, _s, data: dict) -> float:
            if "price" in data:
                # spot
                return float(data["price"])
            else:
                # futuresはtickerにltpが入ってないので仲値で代用
                return (float(data["bestAskPrice"]) + float(data["bestBidPrice"])) / 2

        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "price": _get_price,
            },
        )

    def trades(self) -> TradesStore:
        def _get_timestamp(_store, _o, _s, data: dict) -> int:
            if "time" in data:
                ts = data["time"]
            elif "ts" in data:
                ts = data["ts"]
            else:
                raise RuntimeError(f"Unexpected input: {data}")
            return pd.to_datetime(int(ts), unit="ns", utc=True)

        return TradesStore(
            self._store.execution,
            mapper={
                "id": lambda store, o, s, d: d["tradeId"],
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "timestamp": _get_timestamp,
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbook50,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: "SELL" if d["side"] == "ask" else "BUY",
                "price": lambda store, o, s, d: d["price"],
                "size": lambda store, o, s, d: d["size"],
                "k": lambda store, o, s, d: d["k"],
            },
            keys=["symbol", "k", "side"],
        )

    def order(self) -> OrderStore:
        return OrderStore(
            self._store.orders,
            mapper={
                "id": lambda store, o, s, d: d["orderId"],
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "type": lambda store, o, s, d: d.get("orderType", d["type"]),
            },
        )

    def execution(self) -> ExecutionStore:
        def _get_price(_store, _o, _s, data) -> float:
            try:
                return float(data["matchPrice"])
            except ValueError:
                return 0.0

        return ExecutionStore(
            self._store.orderevents,
            mapper={
                "id": lambda store, o, s, d: d["orderId"],
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": _get_price,
                "size": lambda store, o, s, d: float(d["matchSize"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    int(d["ts"]), unit="ns", utc=True
                ),
            },
            on_watch_get_operation=lambda change: "insert"
            if change.data["type"] == "match"
            else None,
        )

    def position(self) -> PositionStore:
        return PositionStore(
            self._store.positions,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: d["avgEntryPrice"],
                "size": lambda store, o, s, d: abs(float(d["currentQty"])),
            },
            keys=["symbol"],
        )
