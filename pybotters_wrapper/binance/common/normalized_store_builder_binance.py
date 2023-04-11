import pandas as pd
from pybotters.models.binance import BinanceUSDSMDataStore

from core import (
    TickerStore,
    TradesStore,
    OrderbookStore,
    OrderStore,
    ExecutionStore,
    PositionStore,
    NormalizedStoreBuilder,
)


class BinanceNormalizedStoreBuilder(NormalizedStoreBuilder[BinanceUSDSMDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["s"].upper(),
                "price": lambda store, o, s, d: float(d["c"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.trade,
            mapper={
                "id": lambda store, o, s, d: str(d["a"]),
                "symbol": lambda store, o, s, d: str(d["s"]).upper,
                "side": lambda store, o, s, d: "SELL" if d["m"] else "BUY",
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["q"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["T"], unit="ms", utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbook,
            mapper={
                "symbol": lambda store, o, s, d: d["s"].upper(),
                "side": lambda store, o, s, d: d["S"],
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["q"]),
            },
        )

    def order(self) -> OrderStore:
        return OrderStore(
            self._store.order,
            mapper={
                "id": lambda store, o, s, d: str(d["i"]),
                "symbol": lambda store, o, s, d: d["s"].upper(),
                "side": lambda store, o, s, d: float(d["S"]),
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["q"]),
                "type": lambda store, o, s, d: d["o"],
            },
        )

    def execution(self) -> ExecutionStore:
        # 対応ストアがないのでmsgをオーバーライド
        def _on_msg(store, msg):
            if "e" in msg:
                item = None
                if msg["e"] == "ORDER_TRADE_UPDATE":
                    # futures
                    item = msg["o"]
                elif msg["e"] == "executionReport":
                    item = msg
                if item and item["X"] in ("TRADE", "PARTIALLY_FILLED", "FILLED"):
                    item = store._normalize(
                        store._base_store,
                        "insert",
                        {},
                        item,
                    )
                    store._insert([{**item, "info": {"data": msg, "source": None}}])

        return ExecutionStore(
            None,
            mapper={
                "id": lambda store, o, s, d: str(d["i"]),
                "symbol": lambda store, o, s, d: d["s"].upper(),
                "side": lambda store, o, s, d: float(d["S"]),
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["q"]),
                "type": lambda store, o, s, d: d["o"],
            },
            on_msg=_on_msg,
        )

    def position(self) -> PositionStore:
        def _get_operation(change: "StoreChange") -> str:
            """binanceは常に"""
            if change.data["ps"] == "BOTH":
                # one-way
                if float(change.data["pa"]) == 0:
                    return "_delete"
                else:
                    return f"_{change.operation}"
            else:
                # two-way
                return f"_{change.operation}"

        return PositionStore(
            self._store.position,
            on_watch_get_operation=_get_operation,
            mapper={
                "symbol": lambda store, o, s, d: d["s"].upper(),
                "side": lambda store, o, s, d: float(d["S"]),
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["q"]),
                "ps": lambda store, o, s, d: d["ps"],
            },
        )
