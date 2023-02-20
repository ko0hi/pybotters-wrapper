from __future__ import annotations

import warnings

import pandas as pd
from pybotters.models.bitflyer import bitFlyerDataStore
from pybotters.store import StoreChange
from pybotters_wrapper.bitflyer import bitFlyerWebsocketChannels
from pybotters_wrapper.core.store import (
    DataStoreWrapper,
    ExecutionItem,
    ExecutionStore,
    OrderbookItem,
    OrderbookStore,
    OrderItem,
    OrderStore,
    PositionItem,
    PositionStore,
    TickerItem,
    TickerStore,
    TradesItem,
    TradesStore,
)
from pybotters_wrapper.utils.mixins import bitflyerMixin


class bitFlyerTickerStore(TickerStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TickerItem":
        return self._itemize(data["product_code"], data["ltp"])


class bitFlyerTradesStore(TradesStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TradesItem":
        return self._itemize(
            data["id"],
            data["product_code"],
            data["side"],
            float(data["price"]),
            float(data["size"]),
            pd.to_datetime(data["exec_date"]),
        )


class bitFlyerOrderbookStore(OrderbookStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderbookItem":
        return self._itemize(
            data["product_code"],
            data["side"],
            float(data["price"]),
            float(data["size"]),
        )


class bitFlyerOrderStore(OrderStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderItem":
        return self._itemize(
            data["child_order_acceptance_id"],
            data["product_code"],
            data["side"],
            float(data["price"]),
            float(data["size"]),
            data["child_order_type"],
        )


class bitFlyerExecutionStore(ExecutionStore):
    def _get_operation(self, change: "StoreChange") -> str | None:
        if change.data["event_type"] == "EXECUTION":
            return "_insert"

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "ExecutionItem":
        return self._itemize(
            data["child_order_acceptance_id"],
            data["product_code"],
            data["side"],
            float(data["price"]),
            float(data["size"]),
            pd.to_datetime(data["event_date"]),
        )


class bitFlyerPositionStore(PositionStore):
    _KEYS = []

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "PositionItem":
        return self._itemize(
            data["product_code"],
            data["side"],
            float(data["price"]),
            float(data["size"]),
            product_code=data["product_code"],
            commission=data["commission"],
            sfd=data["sfd"],
        )

    def _on_watch(self, change: "StoreChange"):
        # TODO: bitflyerのポジションの同期方法を考える
        # pybottersにおけるbitflyerのポジション計算は結構複雑なので、
        # 確実に状態を同じにするために"一括同期"をしている。
        # 具体的には元ストアの更新をwatchで検知するたびに全取っ替えを行っている。
        # デメリットは計算量が多くなる点と、このNormalizedStoreのwatchが機能しなくなる点。
        self._clear()
        items = []
        for i in self._store.find():
            item = {
                **self._normalize(change.store, change.operation, change.source, i),
                "info": {"data": i, "source": change.source},
            }
            items.append(item)
        self._insert(items)

    async def watch(self) -> "StoreStream":
        warnings.warn(
            "bitFlyerPositionStore.watch is not recommended to use due to its "
            "ad-hook implementation."
        )
        return super().watch()


class bitFlyerDataStoreWrapper(bitflyerMixin, DataStoreWrapper[bitFlyerDataStore]):
    _WRAP_STORE = bitFlyerDataStore

    _WEBSOCKET_CHANNELS = bitFlyerWebsocketChannels

    _TICKER_STORE = (bitFlyerTickerStore, "ticker")
    _TRADES_STORE = (bitFlyerTradesStore, "executions")
    _ORDERBOOK_STORE = (bitFlyerOrderbookStore, "board")
    _ORDER_STORE = (bitFlyerOrderStore, "childorders")
    _EXECUTION_STORE = (bitFlyerExecutionStore, "childorderevents")
    _POSITION_STORE = (bitFlyerPositionStore, "positions")

    _INITIALIZE_CONFIG = {
        "order": ("GET", "/v1/me/getchildorders", ["product_code"]),
        "position": ("GET", "/v1/me/getpositions", ["product_code"]),
    }
