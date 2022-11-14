from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    Type,
    NamedTuple,
    TypedDict,
)

import asyncio
import aiohttp
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


class DataStoreWrapper(Generic[T], LoggingMixin):
    _WRAP_STORE: Type[T] = None

    _WEBSOCKET_CHANNELS: Type[WebsocketChannels] = None

    _TICKER_STORE: tuple[Type[TickerStore], str] = None
    _TRADES_STORE: tuple[Type[TradesStore], str] = None
    _ORDERBOOK_STORE: tuple[Type[OrderbookStore], str] = None
    _ORDER_STORE: tuple[Type[OrderStore], str] = None
    _EXECUTION_STORE: tuple[Type[ExecutionStore], str] = None
    _POSITION_STORE: tuple[Type[PositionStore], str] = None

    _INITIALIZE_ENDPOINTS: dict[str, tuple[str, str]] = {
        # for binance, gmo, kucoin
        "token": None,
        # for kucoin
        "token_public": None,
        "token_private": None,
        "ticker": None,
        "trades": None,
        "orderbook": None,
        "order": None,
        "execution": None,
        "position": None,
    }

    _NORMALIZED_CHANNELS = [
        "ticker",
        "trades",
        "orderbook",
        "order",
        "execution",
        "position",
    ]

    def __init__(self, store: T = None):
        self._store = store or self._WRAP_STORE()

        self._normalized_stores = {}
        self._init_normalized_stores()

        self._ws_channels = self._WEBSOCKET_CHANNELS()
        self._ws_connections = []

    def __repr__(self):
        return self._store.__class__.__name__

    async def initialize(
        self,
        *aws_or_names: Awaitable[aiohttp.ClientResponse] | str | tuple[str, dict],
        client: pybotters.Client = None,
    ) -> "DataStoreWrapper":
        def _check_client():
            assert (
                    client is not None
            ), "need to specify `client` as store.initialize(..., client=client)"

        aws = []
        for a_or_n in aws_or_names:
            if isinstance(a_or_n, Awaitable):
                aws.append(a_or_n)
            elif isinstance(a_or_n, str):
                _check_client()
                if a_or_n in self._INITIALIZE_ENDPOINTS:
                    method, endpoint = self._get_initialize_endpoint(a_or_n)
                    if endpoint:
                        aws.append(client.request(method, endpoint))
                else:
                    raise RuntimeError(
                        f"Unknown endpoint name: {a_or_n}, "
                        f"available endpoints are {self._INITIALIZE_ENDPOINTS}"
                    )
            elif isinstance(a_or_n, tuple):
                _check_client()
                if (
                    len(a_or_n) == 2
                    and isinstance(a_or_n[0], str)
                    and isinstance(a_or_n[1], dict)
                ):
                    method, endpoint = self._get_initialize_endpoint(a_or_n[0])
                    if endpoint:
                        params = dict(method=method, url=endpoint)
                        params["params" if method == "GET" else "data"] = a_or_n[1]
                        aws.append(client.request(**params))
                else:
                    raise RuntimeError(f"Unsupported type: {a_or_n}")
        try:
            await self._store.initialize(*aws)
        except AttributeError:
            # initializeはDataStoreManagerのメソッドではなく、各実装クラスレベルでのメソッド
            # bitbankDataStoreなど実装がない
            pass
        return self

    def subscribe(
        self, channel: str | list[str] | list[tuple[str, dict]], **kwargs
    ) -> "DataStoreWrapper":
        """購読チャンネル追加用メソッド

        >>> store = DataStoreWrapper()
        >>> store.subscribe("ticker")
        >>> store.subscribe("ticker", symbol="BTCUSDT")
        >>> store.subscribe(["ticker", "orderbook"], symbol="BTCUSDT")
        >>> store.subscribe([("ticker", {"symbol": "BTC_USDT"}), ("ticker", {"symbol": "ETHUSDT"})])

        """
        if channel == "default":
            channel = self._NORMALIZED_CHANNELS

        if isinstance(channel, str):
            self._ws_channels.add(channel, **kwargs)
        elif isinstance(channel, list):
            for item in channel:
                if isinstance(item, str):
                    self._ws_channels.add(item, **kwargs)
                elif isinstance(item, tuple):
                    self._ws_channels.add(item[0], **{**kwargs, **item[1]})

        return self

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
        auto_reconnect: bool = False,
        on_reconnection: Callable = None,
        **kwargs,
    ) -> dict[str, WebSocketRunner]:
        endpoint = self._parse_endpoint(endpoint)
        endpoint_to_sends = self._parse_send(endpoint, send)
        hdlr = self._parse_hdlr(hdlr)

        for ep, sj in endpoint_to_sends.items():
            await self._ws_connect(
                client,
                ep,
                sj,
                hdlr,
                send_type,
                hdlr_type,
                auto_reconnect,
                on_reconnection,
                **kwargs,
            )

        if waits is not None:
            await self._wait_socket_responses(waits)

        return self._ws_connections

    async def wait(self):
        await self._store.wait()

    def onmessage(self, msg: "Item", ws: "ClientWebSocketResponse") -> None:
        self._store.onmessage(msg, ws)

    def _get_initialize_endpoint(self, key: str) -> tuple[str, str]:
        if key not in self._INITIALIZE_ENDPOINTS:
            raise RuntimeError(f"Unsupported initialize endpoint key: `{key}`")

        method_and_endpoint = self._INITIALIZE_ENDPOINTS[key]

        if method_and_endpoint is None:
            return None, None

        if len(method_and_endpoint) != 2 or not (
            isinstance(method_and_endpoint[0], str)
            and isinstance(method_and_endpoint[1], str)
        ):
            raise RuntimeError(f"INITIALIZE_ENDPOINT must be tuple[str, str]")
        return method_and_endpoint

    def _init_normalized_stores(self):
        self._normalized_stores["ticker"] = self._init_ticker_store()
        self._normalized_stores["trades"] = self._init_trades_store()
        self._normalized_stores["orderbook"] = self._init_orderbook_store()
        self._normalized_stores["order"] = self._init_order_store()
        self._normalized_stores["execution"] = self._init_execution_store()
        self._normalized_stores["position"] = self._init_position_store()

    def _init_normalized_store(
        self, cls_name_tuple: tuple[Type[NormalizedDataStore], str]
    ) -> NormalizedDataStore | None:
        if cls_name_tuple is None:
            return None
        elif isinstance(cls_name_tuple[1], str):
            store_cls, store_name = cls_name_tuple
            return store_cls(getattr(self.store, store_name))
        else:
            raise RuntimeError(f"Unsupported: {cls_name_tuple}")

    def _init_ticker_store(self) -> "TickerStore" | None:
        return self._init_normalized_store(self._TICKER_STORE)

    def _init_trades_store(self) -> "TradesStore" | None:
        return self._init_normalized_store(self._TRADES_STORE)

    def _init_orderbook_store(self) -> "OrderbookStore" | None:
        return self._init_normalized_store(self._ORDERBOOK_STORE)

    def _init_order_store(self) -> "OrderStore" | None:
        return self._init_normalized_store(self._ORDER_STORE)

    def _init_execution_store(self) -> "ExecutionStore" | None:
        return self._init_normalized_store(self._EXECUTION_STORE)

    def _init_position_store(self) -> "PositionStore" | None:
        return self._init_normalized_store(self._POSITION_STORE)

    def _parse_endpoint(self, endpoint) -> str:
        return endpoint or self._ws_channels.ENDPOINT

    def _parse_send(self, endpoint, send) -> dict[str, list[any]]:
        if send is None:
            # channels must be registered with `DatastoreWrapper.subscribe`
            subscribe_lists = self._ws_channels.get()
            assert len(subscribe_lists), "No channels have not been subscribed."
            return subscribe_lists
        else:
            return {endpoint: send}

    def _parse_hdlr(self, hdlr_json):
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
        auto_reconnect: bool = False,
        on_reconnection: Callable = None,
        **kwargs,
    ):
        self.log(f"Connect {endpoint} {send}")
        conn = WebsocketConnection(endpoint, send, hdlr, send_type, hdlr_type)
        await conn.connect(client, auto_reconnect, on_reconnection, **kwargs)
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
    def ticker(self) -> TickerStore:
        return self._normalized_stores["ticker"]

    @property
    def trades(self) -> TradesStore:
        return self._normalized_stores["trades"]

    @property
    def orderbook(self) -> OrderbookStore:
        return self._normalized_stores["orderbook"]

    @property
    def order(self) -> OrderStore:
        return self._normalized_stores["order"]

    @property
    def execution(self) -> ExecutionStore:
        return self._normalized_stores["execution"]

    @property
    def position(self) -> PositionStore:
        return self._normalized_stores["position"]

    @property
    def exchange(self) -> str:
        return self.__module__.split(".")[-2]

    @property
    def ws_connections(self) -> list[WebsocketConnection]:
        return self._ws_connections

    @property
    def ws_channels(self) -> WebsocketChannels:
        return self._ws_channels


class NormalizedDataStore(DataStore):
    _AVAILABLE_OPERATIONS = ("_insert", "_update", "_delete")

    def __init__(self, store: DataStore, auto_cast=False):
        super(NormalizedDataStore, self).__init__(auto_cast=auto_cast)
        self._store = store
        self._wait_task = asyncio.create_task(self._wait_store())
        self._watch_task = asyncio.create_task(self._watch_store())

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self._store.__class__.__module__}.{self._store.__class__.__name__})"
        )

    async def _wait_store(self):
        while True:
            await self._store.wait()
            self._on_wait()

    async def _watch_store(self):
        with self._store.watch() as stream:
            async for change in stream:
                self._on_watch(change)

    def _on_wait(self):
        ...

    def _on_watch(self, change: "StoreChange"):
        op = self._get_operation(change)
        if op is not None:
            normalized_data = self._normalize({**change.data}, change.operation)
            item = self._make_item(normalized_data, change)
            self._check_operation(op)
            op_fn = getattr(self, op)
            op_fn([item])

    def _get_operation(self, change: "StoreChange") -> str | None:
        return f"_{change.operation}"

    def _normalize(self, d: dict, op: str) -> "Item":
        return d

    def _make_item(self, transformed_item: "Item", change: "StoreChange") -> "Item":
        return {**transformed_item, "info": change.data}

    def _check_operation(self, op):
        if op not in self._AVAILABLE_OPERATIONS:
            raise RuntimeError(
                f"Unsupported operation '{op}' for {self.__class__.__name__}"
            )

    def _itemize(self, *args, **kwargs):
        raise NotImplementedError


class TickerItem(TypedDict):
    symbol: str
    price: float


class TickerStore(NormalizedDataStore):
    _KEYS = ["symbol"]

    def _normalize(self, d: dict, op: str) -> "TickerItem":
        raise NotImplementedError

    def _itemize(self, symbol: str, price: float):
        return TickerItem(symbol=symbol, price=price)


class TradesItem(TypedDict):
    id: str | int
    symbol: str
    side: str
    price: float
    size: float
    timestamp: pd.Timestamp


class TradesStore(NormalizedDataStore):
    _KEYS = ["id", "symbol"]

    def _normalize(self, d: dict, op: str) -> "TradesItem":
        raise NotImplementedError

    def _itemize(
        self,
        id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        timestamp: pd.Timestamp,
    ) -> "TradesItem":
        return TradesItem(
            id=id, symbol=symbol, side=side, price=price, size=size, timestamp=timestamp
        )


class OrderbookItem(TypedDict):
    symbol: str
    side: str
    price: int | float
    size: float


class OrderbookStore(NormalizedDataStore):
    _KEYS = ["symbol", "side", "price"]

    def __init__(self, *args, **kwargs):
        super(OrderbookStore, self).__init__(*args, **kwargs)
        self._mid = None

    def _normalize(self, d: dict, op: str) -> "OrderbookItem":
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

    def _itemize(self, symbol: str, side: str, price: float, size: float):
        return OrderbookItem(symbol=symbol, side=side, price=price, size=size)

    @property
    def mid(self):
        return self._mid


class OrderItem(TypedDict):
    id: str
    symbol: str
    side: str
    price: float
    size: float
    type: str


class OrderStore(NormalizedDataStore):
    _KEYS = ["id", "symbol"]

    def _normalize(self, d: dict, op: str) -> "OrderItem":
        raise NotImplementedError

    def _itemize(
        self, id: str, symbol: str, side: str, price: float, size: float, type: str
    ):
        return OrderItem(
            id=id, symbol=symbol, side=side, price=price, size=size, type=type
        )


class ExecutionItem(TypedDict):
    id: str
    symbol: str
    side: str
    price: float
    size: float
    timestamp: pd.Timestamp


class ExecutionStore(NormalizedDataStore):
    _KEYS = ["id", "symbol"]
    _AVAILABLE_OPERATIONS = ("_insert",)

    def _normalize(self, d: dict, op: str) -> "ExecutionItem":
        raise NotImplementedError

    def _itemize(
        self,
        id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        timestamp: pd.Timestamp,
    ):
        return ExecutionItem(
            id=id, symbol=symbol, side=side, price=price, size=size, timestamp=timestamp
        )


class PositionItem(TypedDict):
    symbol: str
    side: str
    price: float
    size: float


class PositionStore(NormalizedDataStore):
    _KEYS = ["symbol"]

    def _normalize(self, d: dict, op: str) -> "PositionItem":
        raise NotImplementedError

    def _itemize(self, symbol: str, side: str, price: float, size: float):
        return PositionItem(symbol=symbol, side=side, price=price, size=size)
