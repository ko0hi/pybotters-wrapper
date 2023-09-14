import pandas as pd
from pybotters import BybitInverseDataStore, BybitUSDTDataStore

from ..core import (
    ExecutionStore,
    NormalizedStoreBuilder,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TickerStore,
    TradesStore,
)


class BybitNormalizedStoreBuilder(
    NormalizedStoreBuilder[BybitUSDTDataStore | BybitInverseDataStore]
):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.instrument,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "price": lambda store, o, s, d: float(d["last_price"]),
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.trade,
            mapper={
                "id": lambda store, o, s, d: d["trade_id"],
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: d["size"],
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["timestamp"], utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.orderbook,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
            },
        )

    def order(self) -> OrderStore:
        def _extract_order_id(_store, _operation, _symbol, data: dict) -> str:
            if "order_id" in data:
                return data["order_id"]
            elif "stop_order_id" in data:
                return data["stop_order_id"]
            else:
                raise RuntimeError(f"ID not found: {data}")

        return OrderStore(
            self._store.order,
            mapper={
                "id": _extract_order_id,
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: d["qty"],
                "type": lambda store, o, s, d: d["order_type"],
            },
        )

    def execution(self) -> ExecutionStore:
        return ExecutionStore(
            self._store.execution,
            mapper={
                "id": lambda store, o, s, d: d["order_id"],
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: d["exec_qty"],
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["trade_time"], utc=True
                ),
            },
            on_watch_get_operation=lambda change: "_insert",
        )

    def position(self) -> PositionStore:
        return PositionStore(
            self._store.position,
            mapper={
                "symbol": lambda store, o, s, d: d["symbol"],
                "side": lambda store, o, s, d: d["side"].upper(),
                "price": lambda store, o, s, d: float(d["entry_price"]),
                "size": lambda store, o, s, d: d["size"],
                "position_idx": lambda store, o, s, d: d["position_idx"],
            },
            keys=["symbol", "position_idx"],
        )
