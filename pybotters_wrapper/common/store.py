from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Callable, Generic, TypeVar, Type, NamedTuple

import pandas as pd
import pybotters
from pybotters.store import DataStore, DataStoreManager

from pybotters_wrapper.utils import LoggingMixin
from pybotters_wrapper.common import WebsocketConnection


if TYPE_CHECKING:
    from pybotters import Item
    from pybotters.ws import ClientWebSocketResponse, WebSocketRunner
    from pybotters.typedefs import WsStrHandler, WsBytesHandler
    from pybotters.store import StoreChange
    from pybotters_wrapper.common import WebsocketChannels


T = TypeVar("T", bound=DataStoreManager)


class DataStoreManagerWrapper(Generic[T], LoggingMixin):
    _SOCKET_CHANNELS_CLS: Type[WebsocketChannels] = None

    _TICKER_STORE: tuple[Type[TickerStore], str] = None
    _TRADES_STORE: tuple[Type[TradesStore], str] = None
    _ORDERBOOK_STORE: tuple[Type[OrderbookStore], str] = None

    def __init__(self, store: T):
        self._store = store
        self._transformed_stores = {}
        self._init_transformed_stores()
        self._ws_channels = self._SOCKET_CHANNELS_CLS()
        self._ws_connections = []

    def __repr__(self):
        return self._store.__class__.__name__

    async def initialize(self, *args, **kwargs):
        return await self._store.initialize(*args, **kwargs)

    async def wait(self):
        await self._store.wait()

    def onmessage(self, msg: "Item", ws: "ClientWebSocketResponse") -> None:
        self._store.onmessage(msg, ws)

        for p in self._plugins.values():
            p.onmessage(msg, ws, self.store)

    def subscribe(
        self, channel: str | list[str] | list[tuple[str, dict]], **kwargs
    ) -> "DataStoreManagerWrapper":
        """購読チャンネル追加用メソッド

        >>> store = DataStoreManagerWrapper()
        >>> store.subscribe("ticker")
        >>> store.subscribe("ticker", symbol="BTCUSDT")
        >>> store.subscribe(["ticker", "orderbook"], symbol="BTCUSDT")
        >>> store.subscribe([("ticker", {"symbol": "BTC_USDT"}), ("ticker", {"symbol": "ETHUSDT"})])

        """
        if isinstance(channel, str):
            self._ws_channels.add(channel, **kwargs)
        elif isinstance(channel, list):
            for item in channel:
                if isinstance(item, str):
                    self._ws_channels.add(item, **kwargs)
                elif isinstance(item, tuple):
                    self._ws_channels.add(item[0], **{**kwargs, **item[1]})

    async def connect(
        self,
        client: "pybotters.Client",
        *,
        endpoint: str = None,
        send: any = None,
        hdlr: WsStrHandler | WsBytesHandler = None,
        waits: list[DataStore | str] = None,
        send_type: str = "json",
        hdlr_type: str = "json",
        **kwargs,
    ) -> dict[str, WebSocketRunner]:
        endpoint = self._parse_endpoint(endpoint)
        endpoint_to_send_jsons = self._parse_send_json(endpoint, send)
        hdlr = self._parse_hdlr_json(hdlr)

        for ep, sj in endpoint_to_send_jsons.items():
            await self._ws_connect(client, ep, sj, hdlr, send_type, hdlr_type, **kwargs)

        if waits is not None:
            await self._wait_socket_responses(waits)

        return self._ws_connections

    def _init_transformed_stores(self):
        self._transformed_stores["ticker"] = self._init_ticker_store()
        self._transformed_stores["trades"] = self._init_trades_store()
        self._transformed_stores["orderbook"] = self._init_orderbook_store()

    def _init_transformed_store(self, cls_name_tuple):
        if cls_name_tuple is None:
            return None
        store_cls, store_name = cls_name_tuple
        return store_cls(getattr(self.store, store_name))

    def _init_ticker_store(self) -> "TickerStore" | None:
        return self._init_transformed_store(self._TICKER_STORE)

    def _init_trades_store(self) -> "TradesStore" | None:
        return self._init_transformed_store(self._TRADES_STORE)

    def _init_orderbook_store(self) -> "OrderbookStore" | None:
        return self._init_transformed_store(self._ORDERBOOK_STORE)

    def _parse_endpoint(self, endpoint) -> str:
        return endpoint or self._ws_channels.ENDPOINT

    def _parse_send_json(self, endpoint, send_json) -> dict[str, list[any]]:
        if send_json is None:
            # a user registered channels via `DatastoreWrapper.subscribe`
            subscribe_lists = self._ws_channels.get_endpoint_and_channels()
            assert len(subscribe_lists), "No channels have not been subscribed."
            return subscribe_lists
        else:
            return {endpoint: send_json}

    def _parse_hdlr_json(self, hdlr_json):
        if hdlr_json is None:
            hdlr_json = self.onmessage
        else:
            if isinstance(hdlr_json, list):
                hdlr_json = hdlr_json + [self.onmessage]
            else:
                hdlr_json = [hdlr_json, self.onmessage]
        return hdlr_json

    async def _ws_connect(
        self,
        client,
        endpoint,
        send,
        hdlr,
        send_type: str = "json",
        hdlr_type: str = "json",
        **kwargs,
    ):
        self.log(f"Connect {endpoint} {send}")
        conn = WebsocketConnection(endpoint, send, hdlr, send_type, hdlr_type)
        await conn.connect(client, **kwargs)
        self._ws_connections.append(conn)

    async def _wait_socket_responses(self, waits):
        waits = [getattr(self, w) if isinstance(w, str) else w for w in waits]

        while True:
            await self._store.wait()
            is_done = [len(w) > 0 for w in waits]
            self.log(
                f"Waiting responses ... "
                f"{dict(zip(map(lambda x: x.__class__.__name__, waits), is_done))}"
            )
            if all(is_done):
                break
        self.log("All channels got ready")

    @property
    def store(self) -> T:
        return self._store

    # common stores
    @property
    def ticker(self):
        return self._transformed_stores["ticker"]

    @property
    def trades(self):
        return self._transformed_stores["trades"]

    @property
    def orderbook(self):
        return self._transformed_stores["orderbook"]

    @property
    def board(self):
        raise NotImplementedError

    @property
    def events(self):
        raise NotImplementedError

    @property
    def position(self):
        raise NotImplementedError

    @property
    def orders(self):
        raise NotImplementedError

    @property
    def exchange(self):
        return self.__module__.split(".")[-2]

    @property
    def ws_connections(self):
        return self._ws_connections

    @property
    def ws_channels(self):
        return self._ws_channels


class TransformedDataStore(DataStore):
    def __init__(self, ds: DataStore, *, auto_cast=False):
        super(TransformedDataStore, self).__init__(auto_cast=auto_cast)
        self._ds = ds
        self._sync_task = asyncio.create_task(self._watch())

    async def _wait(self):
        while True:
            await self._ds.wait()
            self._on_wait()

    async def _watch(self):
        with self._ds.watch() as stream:
            async for change in stream:
                self._on_watch(change)
                transformed_data = self._transform_data(change)
                method = self._get_method(change)
                method([self._make_register_item(transformed_data, change)])

    def _on_wait(self):
        ...

    def _on_watch(self, change: "StoreChange"):
        ...

    def _transform_data(self, change: "StoreChange") -> "Item":
        return change.data

    def _get_method(self, change: "StoreChange") -> Callable:
        return getattr(self, f"_{change.operation}")

    def _make_register_item(self, transformed_item: Item, change: StoreChange) -> Item:
        return {**transformed_item, "info": change.data}


class TickerItem(NamedTuple):
    symbol: str
    price: float


class TickerStore(TransformedDataStore):
    _KEYS = ["symbol"]

    def _transform_data(self, change: "StoreChange") -> "TickerItem":
        raise NotImplementedError


class TradesItem(NamedTuple):
    id: str | int
    symbol: str
    side: str
    price: float
    size: float
    timestamp: pd.Timestamp


class TradesStore(TransformedDataStore):
    _KEYS = ["id", "symbol"]

    def _transform_data(self, change: "StoreChange") -> "TradesItem":
        raise NotImplementedError


class OrderbookItem(NamedTuple):
    symbol: str
    side: str
    price: int | float
    size: float


class OrderbookStore(TransformedDataStore):
    _KEYS = ["symbol", "side", "price"]

    def __init__(self, *args, **kwargs):
        super(OrderbookStore, self).__init__(*args, **kwargs)
        self._mid = None

    def _transform_data(self, change: "StoreChange") -> "OrderbookItem":
        raise NotImplementedError

    def _on_wait(self):
        sells, buys = self.sorted().values()
        if len(sells) != 0 or len(buys) != 0:
            ba = sells[0]["price"]
            bb = buys[0]["price"]
            self._mid = (ba + bb) / 2

    def sorted(self, query: Item = None) -> dict[str, list[Item]]:
        if query is None:
            query = {}
        result = {"SELL": [], "BUY": []}
        for item in self:
            if all(k in item and query[k] == item[k] for k in query):
                result[item["side"]].append(item)
        result["SELL"].sort(key=lambda x: x["price"])
        result["BUY"].sort(key=lambda x: x["price"], reverse=True)
        return result

    @property
    def mid(self):
        return self._mid
