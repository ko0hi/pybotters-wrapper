import pandas as pd

import pybotters

from pybotters_wrapper.common import DataStoreWrapper
from pybotters_wrapper.common.store import (
    TickerStore,
    TradesStore,
    OrderbookStore,
    OrderStore,
    ExecutionStore,
    PositionStore,
)
from pybotters_wrapper.kucoin import (
    KucoinSpotWebsocketChannels,
    KucoinFuturesWebsocketChannels,
)


class KucoinTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        if "price" in d:
            # spot
            price = float(d["price"])
        else:
            # futuresはtickerにltpが入ってないので仲値で代用
            price = (float(d["bestAskPrice"]) + float(d["bestBidPrice"])) / 2
        return self._itemize(d["symbol"], price)


class KucoinTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        return self._itemize(
            d["tradeId"],
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            float(d["size"]),
            pd.to_datetime(int(d.get("time", d["ts"])), unit="ns"),  # spot / futures
        )


class KucoinOrderbookStore(OrderbookStore):
    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            d["symbol"], "SELL" if d["side"] == "ask" else "BUY", d["price"], d["size"]
        )


class KucoinOrderStore(OrderStore):
    def _normalize(self, d: dict, op: str) -> "OrderItem":
        return self._itemize(
            d["orderId"],
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            float(d["size"]),
            d.get("orderType", d["type"]),  # spot / futures
        )


class KucoinExecutionStore(ExecutionStore):
    def _get_operation(self, change: "StoreChange") -> str | None:
        if change.data["type"] == "filled":
            return "_insert"

    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        try:
            price = float(d["price"])
        except ValueError:
            price = 0

        return self._itemize(
            d["orderId"],
            d["symbol"],
            d["side"].upper(),
            price,
            float(d["size"]),
            pd.to_datetime(int(d["ts"]), unit="ns"),
        )


class KucoinPositionStore(PositionStore):
    def _normalize(self, d: dict, op: str) -> "PositionItem":
        return self._itemize(
            d["symbol"], d["side"], d["avgEntryPrice"], abs(float(d["currentQty"]))
        )


class _KucoinDataStoreWrapper(DataStoreWrapper[pybotters.KuCoinDataStore]):
    _WRAP_STORE = pybotters.KuCoinDataStore
    _INITIALIZE_ENDPOINTS = {
        "token": ("POST", "/api/v1/bullet-public"),
        "token_public": ("POST", "/api/v1/bullet-public"),
        "token_private": ("POST", "/api/v1/bullet-private"),
        "position": ("GET", "/api/v1/positions")
    }
    _TICKER_STORE = (KucoinTickerStore, "ticker")
    _TRADES_STORE = (KucoinTradesStore, "execution")
    _ORDERBOOK_STORE = (KucoinOrderbookStore, "orderbook50")
    _ORDER_STORE = (KucoinOrderStore, "orders")
    _EXECUTION_STORE = (KucoinExecutionStore, "orderevents")
    _POSITION_STORE = (KucoinPositionStore, "positions")

    """

    note...

    動的に定めたエンドポイントで上書きをしている

    """

    def _parse_endpoint(self, endpoint) -> str:
        return endpoint or self.endpoint

    def _parse_send(self, endpoint, send) -> dict[str, list[any]]:
        assert endpoint is not None
        rtn = {endpoint: send}
        if send is None:
            rtn[endpoint] = []
            subscribe_lists = self._ws_channels.get()
            assert len(subscribe_lists), "No channels have not been subscribed."
            for k, v in subscribe_lists.items():
                rtn[endpoint] += v
        return rtn

    @property
    def endpoint(self) -> str:
        return self.store.endpoint


class KucoinSpotDataStoreWrapper(_KucoinDataStoreWrapper):
    _WEBSOCKET_CHANNELS = KucoinSpotWebsocketChannels


class KucoinFuturesDataStoreWrapper(_KucoinDataStoreWrapper):
    _WEBSOCKET_CHANNELS = KucoinFuturesWebsocketChannels
