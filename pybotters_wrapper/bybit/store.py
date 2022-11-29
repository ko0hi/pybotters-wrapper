from __future__ import annotations

import pandas as pd
from pybotters.models.bybit import BybitInverseDataStore, BybitUSDTDataStore
from pybotters_wrapper.bybit import (
    BybitInverseWebsocketChannels,
    BybitUSDTWebsocketChannels,
)
from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.common.store import (
    ExecutionStore,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TickerStore,
    TradesStore,
)
from pybotters_wrapper.utils.mixins import BybitInverseMixin, BybitUSDTMixin


class BybitTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["symbol"], d["last_price"])


class BybitTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(
            d["trade_id"],
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            d["size"],
            pd.to_datetime(d["timestamp"]),
        )


class BybitOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            float(d["size"]),
        )


class BybitOrderStore(OrderStore):
    def _onmessage(self, msg: "Item", ws: "ClientWebSocketResponse"):
        if "topic" in msg:
            topic: str = msg["topic"]
            data = msg["data"]

            if topic == "order":
                for item in data:
                    normalized_item = self._normalize(item, None)
                    normalized_item = {**normalized_item, "info": item}
                    if item["order_status"] in ("Created", "New", "PartiallyFilled"):
                        self._update([normalized_item])
                    else:
                        self._delete([normalized_item])

            elif topic == "stop_order":
                for item in data:
                    normalized_item = self._normalize(item, None)
                    normalized_item = {**normalized_item, "info": item}
                    if item["order_status"] in ("Active", "Untriggered"):
                        self._update([normalized_item])
                    else:
                        self._delete([normalized_item])

    def _normalize(self, d: dict, op: str) -> "OrderItem":
        if "order_id" in d:
            id = d["order_id"]
        elif "stop_order_id" in d:
            id = d["stop_order_id"]
        else:
            raise RuntimeError(f"ID not found: {d}")

        return self._itemize(
            id,
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            float(d["qty"]),
            d["order_type"],
        )


class BybitExecutionStore(ExecutionStore):
    def _get_operation(self, change: "StoreChange") -> str:
        return "_insert"

    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        return self._itemize(
            d["order_id"],
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            float(d["exec_qty"]),
            pd.to_datetime(d["trade_time"]),
        )


class BybitPositionStore(PositionStore):
    _KEYS = ("symbol", "position_idx")

    def _normalize(self, d: dict, op: str) -> "PositionItem":
        return self._itemize(
            d["symbol"],
            d["side"].upper(),
            float(d["entry_price"]),
            float(d["size"]),
            position_idx=d["position_idx"],
        )


class BybitDataStoreMixin:
    _TICKER_STORE = (BybitTickerStore, "instrument")
    _TRADES_STORE = (BybitTradesStore, "trade")
    _ORDERBOOK_STORE = (BybitOrderbookStore, "orderbook")
    _ORDER_STORE = (BybitOrderStore, None)
    _EXECUTION_STORE = (BybitExecutionStore, "execution")
    _POSITION_STORE = (BybitPositionStore, "position")


class BybitUSDTDataStoreWrapper(
    BybitDataStoreMixin, BybitUSDTMixin, DataStoreWrapper[BybitUSDTDataStore]
):
    _WRAP_STORE = BybitUSDTDataStore
    _WEBSOCKET_CHANNELS = BybitUSDTWebsocketChannels
    _INITIALIZE_CONFIG = {
        # TODO: stop_orderどうするか
        "order": ("GET", "/private/linear/order/search", ["symbol"]),
        "position": ("GET", "/private/linear/position/list", None),
    }


class BybitInverseDataStoreWrapper(
    BybitDataStoreMixin, BybitInverseMixin, DataStoreWrapper[BybitInverseDataStore]
):
    _WRAP_STORE = BybitInverseDataStore
    _WEBSOCKET_CHANNELS = BybitInverseWebsocketChannels
    _INITIALIZE_CONFIG = {
        "order": ("GET", "/v2/private/order", ["symbol"]),
        "position": ("GET", "/v2/private/position/list", None),
    }
