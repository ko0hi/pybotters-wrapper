from __future__ import annotations

import pandas as pd
from pybotters.models.bybit import BybitInverseDataStore, BybitUSDTDataStore
from pybotters.store import Item, StoreChange
from pybotters.ws import ClientWebSocketResponse
from pybotters_wrapper.bybit import (
    BybitInverseWebsocketChannels,
    BybitUSDTWebsocketChannels,
)
from pybotters_wrapper.core import DataStoreWrapper
from pybotters_wrapper.core.store import (
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
from pybotters_wrapper.utils.mixins import BybitInverseMixin, BybitUSDTMixin


class BybitTickerStore(TickerStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TickerItem":
        return self._itemize(data["symbol"], float(data["last_price"]))


class BybitTradesStore(TradesStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TradesItem":
        return self._itemize(
            data["trade_id"],
            data["symbol"],
            data["side"].upper(),
            float(data["price"]),
            data["size"],
            pd.to_datetime(data["timestamp"], utc=True),
        )


class BybitOrderbookStore(OrderbookStore):
    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderbookItem":
        return self._itemize(
            data["symbol"],
            data["side"].upper(),
            float(data["price"]),
            float(data["size"]),
        )


class BybitOrderStore(OrderStore):
    def _on_msg(self, msg: "Item"):
        if "topic" in msg:
            topic: str = msg["topic"]
            data = msg["data"]

            if topic == "order":
                for item in data:
                    normalized_item = self._normalize(None, None, None, item)
                    normalized_item = {
                        **normalized_item,
                        "info": {"data": item, "source": None},
                    }
                    if item["order_status"] in ("Created", "New", "PartiallyFilled"):
                        self._update([normalized_item])
                    else:
                        self._delete([normalized_item])

            elif topic == "stop_order":
                for item in data:
                    normalized_item = self._normalize(None, None, None, item)
                    normalized_item = {
                        **normalized_item,
                        "info": {"data": item, "source": None},
                    }
                    if item["order_status"] in ("Active", "Untriggered"):
                        self._update([normalized_item])
                    else:
                        self._delete([normalized_item])

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderItem":
        if "order_id" in data:
            id = data["order_id"]
        elif "stop_order_id" in data:
            id = data["stop_order_id"]
        else:
            raise RuntimeError(f"ID not found: {data}")

        return self._itemize(
            id,
            data["symbol"],
            data["side"].upper(),
            float(data["price"]),
            float(data["qty"]),
            data["order_type"],
        )


class BybitExecutionStore(ExecutionStore):
    def _get_operation(self, change: "StoreChange") -> str:
        return "_insert"

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "ExecutionItem":
        return self._itemize(
            data["order_id"],
            data["symbol"],
            data["side"].upper(),
            float(data["price"]),
            float(data["exec_qty"]),
            pd.to_datetime(data["trade_time"], utc=True),
        )


class BybitPositionStore(PositionStore):
    _KEYS = ("symbol", "position_idx")

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "PositionItem":
        return self._itemize(
            data["symbol"],
            data["side"].upper(),
            float(data["entry_price"]),
            float(data["size"]),
            position_idx=data["position_idx"],
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
