from __future__ import annotations

import pandas as pd
import pybotters
from pybotters.store import StoreChange
from pybotters_wrapper.common.store import (
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
from pybotters_wrapper.kucoin import (
    KuCoinFuturesWebsocketChannels,
    KuCoinSpotWebsocketChannels,
)
from pybotters_wrapper.utils.mixins import KuCoinFuturesMixin, KuCoinSpotMixin


class KuCoinTickerStore(TickerStore):
    def _normalize(self, d: dict, op: str) -> "TickerItem":
        if "price" in d:
            # spot
            price = float(d["price"])
        else:
            # futuresはtickerにltpが入ってないので仲値で代用
            price = (float(d["bestAskPrice"]) + float(d["bestBidPrice"])) / 2
        return self._itemize(d["symbol"], price)


class KuCoinTradesStore(TradesStore):
    def _normalize(self, d: dict, op: str) -> "TradesItem":
        if "time" in d:
            ts = d["time"]
        elif "ts" in d:
            ts = d["ts"]
        else:
            raise RuntimeError(f"Unexpected input: {d}")
        return self._itemize(
            d["tradeId"],
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            float(d["size"]),
            pd.to_datetime(int(ts), unit="ns", utc=True),  # spot / futures
        )


class KuCoinOrderbookStore(OrderbookStore):
    _KEYS = ["symbol", "k", "side"]

    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
        return self._itemize(
            d["symbol"],
            "SELL" if d["side"] == "ask" else "BUY",
            d["price"],
            d["size"],
            k=d["k"],
        )


class KuCoinOrderStore(OrderStore):
    def _normalize(self, d: dict, op: str) -> "OrderItem":
        return self._itemize(
            d["orderId"],
            d["symbol"],
            d["side"].upper(),
            float(d["price"]),
            float(d["size"]),
            d.get("orderType", d["type"]),  # spot / futures
        )


class KuCoinExecutionStore(ExecutionStore):
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
            pd.to_datetime(int(d["ts"]), unit="ns", utc=True),
        )


class KuCoinPositionStore(PositionStore):
    # one-way only
    _KEYS = ["symbol"]

    def _normalize(self, d: dict, op: str) -> "PositionItem":
        return self._itemize(
            d["symbol"], d["side"], d["avgEntryPrice"], abs(float(d["currentQty"]))
        )


class _KuCoinDataStoreWrapper(DataStoreWrapper[pybotters.KuCoinDataStore]):
    _WRAP_STORE = pybotters.KuCoinDataStore
    _INITIALIZE_CONFIG = {
        "token": ("POST", "/api/v1/bullet-private", None),
        "token_public": ("POST", "/api/v1/bullet-public", None),
        "token_private": ("POST", "/api/v1/bullet-private", None),
        "position": ("GET", "/api/v1/positions", None),
    }
    _TICKER_STORE = (KuCoinTickerStore, "ticker")
    _TRADES_STORE = (KuCoinTradesStore, "execution")
    _ORDERBOOK_STORE = (KuCoinOrderbookStore, "orderbook50")
    _ORDER_STORE = (KuCoinOrderStore, "orders")
    _EXECUTION_STORE = (KuCoinExecutionStore, "orderevents")
    _POSITION_STORE = (KuCoinPositionStore, "positions")

    """

    note...

    動的に定めたエンドポイントで上書きをしている

    """

    def _parse_endpoint(self, endpoint: str, client: pybotters.Client) -> str:
        try:
            return self.endpoint
        except RuntimeError:
            import pybotters_wrapper as pbw

            api = pbw.create_api(self.exchange, client)
            url = self._INITIALIZE_CONFIG["token"][1]
            resp = api.spost(url)
            data = resp.json()
            self.store._endpoint = self.store._create_endpoint(data["data"])
            self.log("Websocket token got automatically initialized", "warning")
            return self.endpoint

    def _parse_send(
        self, endpoint: str, send: any, client: pybotters.Client
    ) -> dict[str, list[any]]:
        assert endpoint is not None

        subscribe_lists = self._ws_channels.get()

        if len(subscribe_lists) == 0 and send is None:
            raise RuntimeError("No channels got subscribed")
            return {endpoint: send}

        rtn = {endpoint: []}

        if send is not None:
            if isinstance(send, dict):
                rtn[endpoint].append(send)
            elif isinstance(send, list):
                rtn[endpoint] += send
            else:
                raise TypeError(f"Invalid `send`: {send}")

        for _, v in subscribe_lists.items():
            rtn[endpoint] += v

        return rtn

    @property
    def endpoint(self) -> str:
        return self.store.endpoint


class KuCoinSpotDataStoreWrapper(KuCoinSpotMixin, _KuCoinDataStoreWrapper):
    _WEBSOCKET_CHANNELS = KuCoinSpotWebsocketChannels


class KuCoinFuturesDataStoreWrapper(KuCoinFuturesMixin, _KuCoinDataStoreWrapper):
    _WEBSOCKET_CHANNELS = KuCoinFuturesWebsocketChannels
