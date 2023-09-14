import warnings

import pandas as pd
from pybotters import bitFlyerDataStore
from pybotters.store import StoreChange, StoreStream

from ..core import (
    ExecutionStore,
    NormalizedStoreBuilder,
    OrderbookStore,
    OrderStore,
    PositionItem,
    PositionStore,
    TickerStore,
    TradesStore,
)


class bitFlyerNormalizedStoreBuilder(NormalizedStoreBuilder[bitFlyerDataStore]):
    def ticker(self) -> TickerStore:
        return TickerStore(
            self._store.ticker,
            mapper={
                "symbol": lambda store, o, s, d: d["product_code"],
                "price": lambda store, o, s, d: d["ltp"],
            },
        )

    def trades(self) -> TradesStore:
        return TradesStore(
            self._store.executions,
            mapper={
                "id": lambda store, o, s, d: str(d["id"]),
                "symbol": lambda store, o, s, d: d["product_code"],
                "side": lambda store, o, s, d: d["side"],
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["exec_date"], utc=True
                ),
            },
        )

    def orderbook(self) -> OrderbookStore:
        return OrderbookStore(
            self._store.board,
            mapper={
                "symbol": lambda store, o, s, d: d["product_code"],
                "side": lambda store, o, s, d: d["side"],
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
            },
        )

    def order(self) -> OrderStore:
        return OrderStore(
            self._store.childorders,
            mapper={
                "id": lambda store, o, s, d: d["child_order_acceptance_id"],
                "symbol": lambda store, o, s, d: d["product_code"],
                "side": lambda store, o, s, d: d["side"],
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "type": lambda store, o, s, d: d["child_order_type"],
            },
        )

    def execution(self) -> ExecutionStore:
        return ExecutionStore(
            self._store.childorderevents,
            mapper={
                "id": lambda store, o, s, d: d["child_order_acceptance_id"],
                "symbol": lambda store, o, s, d: d["product_code"],
                "side": lambda store, o, s, d: d["side"],
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                "timestamp": lambda store, o, s, d: pd.to_datetime(
                    d["event_date"], utc=True
                ),
            },
            # event_typeがEXECUTIONの時だけ_insertを実行
            on_watch_get_operation=lambda change: change.operation
            if change.data["event_type"] == "EXECUTION"
            else None,
        )

    def position(self) -> PositionStore:
        class bitFlyerPositionStore(PositionStore):
            _KEYS = []
            _NORMALIZED_ITEM_CLASS = PositionItem

            def _on_watch(self, change: "StoreChange") -> None:
                # TODO: bitflyerのポジションの同期方法を考える
                # pybottersにおけるbitflyerのポジション計算は結構複雑なので、
                # 確実に状態を同じにするために"一括同期"する。
                self.synchronize()

            def watch(self) -> "StoreStream":
                warnings.warn(
                    "bitFlyerPositionStore.watch is not recommended to use due to its "
                    "ad-hook implementation."
                )
                return super().watch()

        return bitFlyerPositionStore(
            self._store.positions,
            mapper={
                "symbol": lambda store, o, s, d: d["product_code"],
                "side": lambda store, o, s, d: d["side"],
                "price": lambda store, o, s, d: float(d["price"]),
                "size": lambda store, o, s, d: float(d["size"]),
                # キーを一致させるため
                "product_code": lambda store, o, s, d: d["product_code"],
                "commission": lambda store, o, s, d: d["commission"],
                "sfd": lambda store, o, s, d: d["sfd"],
            },
        )
