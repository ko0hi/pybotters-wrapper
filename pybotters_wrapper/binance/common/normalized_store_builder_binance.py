import pandas as pd
from pybotters.models.binance import (
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
    BinanceCOINMDataStore,
)

from ...core import (
    TickerStore,
    TradesStore,
    OrderbookStore,
    OrderStore,
    ExecutionStore,
    PositionStore,
    NormalizedStoreBuilder,
)


class BinanceNormalizedStoreBuilder(
    NormalizedStoreBuilder[
        BinanceSpotDataStore | BinanceUSDSMDataStore | BinanceCOINMDataStore
        ]
):
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
                "symbol": lambda store, o, s, d: str(d["s"]).upper(),
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
                "side": lambda store, o, s, d: d["S"],
                "price": lambda store, o, s, d: float(d["p"]),
                "size": lambda store, o, s, d: float(d["q"]),
                "type": lambda store, o, s, d: d["o"],
            },
        )

    def execution(self) -> ExecutionStore:
        # 対応ストアがないのでmsgをオーバーライド
        def _on_msg(self, msg):
            if "e" in msg:
                item = None
                if msg["e"] == "ORDER_TRADE_UPDATE":
                    # futures
                    item = msg["o"]
                elif msg["e"] == "executionReport":
                    item = msg
                if item and item["X"] in ("TRADE", "PARTIALLY_FILLED", "FILLED"):
                    item = self._normalize(
                        self._base_store,
                        "insert",
                        {},
                        item,
                    )
                    self._insert([{**item, "info": {"data": msg, "source": None}}])

        return ExecutionStore(
            None,
            mapper={
                "id": lambda store, o, s, d: str(d["i"]),
                "symbol": lambda store, o, s, d: d["s"].upper(),
                "side": lambda store, o, s, d: d["S"],
                "price": lambda store, o, s, d: float(d["L"]),
                "size": lambda store, o, s, d: float(d["l"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["T"], unit="ms", utc=True
                ),
            },
            on_msg=_on_msg,
        )

    def position(self) -> PositionStore:
        def mapper(store, operation, source, data) -> dict:
            size = float(data["pa"])

            if data["ps"] == "BOTH":
                if size == 0:
                    side = None
                elif size > 0:
                    side = "BUY"
                else:
                    side = "SELL"
            else:
                side = "BUY" if data["ps"] == "LONG" else "SELL"
            return {
                "symbol": data["s"].upper(),
                "side": side,
                "price": float(data["ep"]),
                "size": abs(size),
                "ps": data["ps"],
            }

        return PositionStore(self._store.position, mapper=mapper)
