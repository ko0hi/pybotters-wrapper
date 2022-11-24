import pandas as pd
from pybotters.models.bitflyer import bitFlyerDataStore
from pybotters_wrapper.common import (
    DataStoreWrapper,
    TickerStore,
    TradesStore,
    OrderbookStore,
    OrderStore,
    ExecutionStore,
    PositionStore,
)
from pybotters_wrapper.bitflyer import bitFlyerWebsocketChannels


class bitFlyerTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(d["product_code"], d["ltp"])


class bitFlyerTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        side = d["side"]
        if side:
            order_id = d[side.lower() + "_child_order_acceptance_id"]
        else:
            order_id = d["buy_child_order_acceptance_id"]
        return self._itemize(
            order_id,
            d["product_code"],
            side,
            float(d["price"]),
            float(d["size"]),
            pd.to_datetime(d["exec_date"]),
        )


class bitFlyerOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        return self._itemize(
            d["product_code"], d["side"], float(d["price"]), float(d["size"])
        )


class bitFlyerOrderStore(OrderStore):
    def _normalize(self, d: dict, op: str) -> "OrderItem":
        return self._itemize(
            d["child_order_acceptance_id"],
            d["product_code"],
            d["side"],
            float(d["price"]),
            float(d["size"]),
            d["child_order_type"],
        )


class bitFlyerExecutionStore(ExecutionStore):
    def _get_operation(self, change: "StoreChange") -> str | None:
        if change.data["event_type"] == "EXECUTION":
            return "_insert"

    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        return self._itemize(
            d["child_order_acceptance_id"],
            d["product_code"],
            d["side"],
            float(d["price"]),
            float(d["size"]),
            pd.to_datetime(d["event_date"]),
        )


class bitFlyerPositionStore(PositionStore):
    def _normalize(self, d: dict, op: str) -> "PositionItem":
        return self._itemize(
            d["product_code"],
            d["side"],
            float(d["price"]),
            float(d["size"]),
        )


class bitFlyerDataStoreWrapper(DataStoreWrapper[bitFlyerDataStore]):
    _NAME = "bitflyer"
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
        "position": ("GET", "/v1/me/getpositions", ["product_code"])
    }