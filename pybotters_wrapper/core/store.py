from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Awaitable, Callable, Generic, Type, TypedDict, TypeVar

import aiohttp
import pandas as pd
import pybotters
from aiohttp.client_reqrep import ClientResponse
from loguru import logger
from pybotters.store import DataStore, DataStoreManager
from pybotters_wrapper.core import WebsocketConnection
from pybotters_wrapper.utils.mixins import ExchangeMixin, LoggingMixin

if TYPE_CHECKING:
    from pybotters import Item
    from pybotters.store import StoreChange
    from pybotters.typedefs import WsBytesHandler, WsStrHandler
    from pybotters.ws import ClientWebSocketResponse, WebSocketRunner
    from pybotters_wrapper.core import WebsocketChannels

T = TypeVar("T", bound=DataStoreManager)
InitializeRequestConfig = tuple[str, str, list[str] | tuple[str] | None]


class DataStoreWrapper(Generic[T], ExchangeMixin, LoggingMixin):
    _WRAP_STORE: Type[T] = None

    _WEBSOCKET_CHANNELS: Type[WebsocketChannels] = None

    _TICKER_STORE: tuple[Type[TickerStore], str] = None
    _TRADES_STORE: tuple[Type[TradesStore], str] = None
    _ORDERBOOK_STORE: tuple[Type[OrderbookStore], str] = None
    _ORDER_STORE: tuple[Type[OrderStore], str] = None
    _EXECUTION_STORE: tuple[Type[ExecutionStore], str] = None
    _POSITION_STORE: tuple[Type[PositionStore], str] = None

    _INITIALIZE_CONFIG: dict[str, InitializeRequestConfig | None] = {
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

    _NORMALIZED_STORE_CHANNELS = [
        "ticker",
        "trades",
        "orderbook",
        "order",
        "execution",
        "position",
    ]

    def __init__(self, store: T = None):
        self._store = store or self._WRAP_STORE()

        self._normalized_stores: dict[str, NormalizedDataStore] = {}
        self._init_normalized_stores()

        self._ws_channels = self._WEBSOCKET_CHANNELS()
        self._ws_connections = []

    async def initialize(
        self,
        aws_or_names: list[Awaitable[aiohttp.ClientResponse] | str | tuple[str, dict]],
        client: "pybotters.Client" = None,
    ) -> "DataStoreWrapper":
        self.log(f"Initialize requests {aws_or_names}")

        def _check_client():
            assert (
                client is not None
            ), "need to pass `client` as store.initialize(..., client=client)"

        def _raise_invalid_params(name, params):
            raise RuntimeError(
                f"Missing required parameters for initializing "
                f"'{name}' of {self.__class__.__name__}: "
                f"{params} (HINT: store.initialize([('{name}', "
                f"{str({p: '...' for p in params})}), ...))"
            )

        request_tasks = []
        for a_or_n in aws_or_names:
            if isinstance(a_or_n, Awaitable):
                # validateの用にレスポンスにアクセスしたいのでTaskとしてスケジューリング
                request_tasks.append(asyncio.create_task(a_or_n))

            elif isinstance(a_or_n, str):
                _check_client()

                name = a_or_n

                (
                    method,
                    endpoint,
                    required_params,
                ) = self._get_initialize_request_config(name)

                if endpoint:
                    if required_params is not None:
                        _raise_invalid_params(name, required_params)
                    request_tasks.append(
                        asyncio.create_task(
                            self._initialize_request(client, method, endpoint)
                        )
                    )

            elif (
                isinstance(a_or_n, tuple)
                and len(a_or_n) == 2
                and isinstance(a_or_n[0], str)
                and isinstance(a_or_n[1], dict)
            ):
                _check_client()

                name, params = a_or_n

                (
                    method,
                    endpoint,
                    required_params,
                ) = self._get_initialize_request_config(name)

                if endpoint:
                    missing_params = set(required_params).difference(params.keys())
                    if len(missing_params) > 0:
                        _raise_invalid_params(name, required_params)

                    request_tasks.append(
                        asyncio.create_task(
                            self._initialize_request(client, method, endpoint, params)
                        )
                    )

        try:
            await self._store.initialize(*request_tasks)
        except AttributeError:
            # initializeはDataStoreManagerのメソッドではなく、各実装クラスレベルでのメソッド
            # bitbankDataStoreなど実装がない
            pass
        finally:
            for aw in request_tasks:
                await self._validate_initialize_response(aw)

        return self

    def subscribe(
        self, channel: str | list[str] | list[tuple[str, dict]], **kwargs
    ) -> "DataStoreWrapper":
        """購読チャンネル追加用メソッド"""
        if channel == "all":
            channel = self._NORMALIZED_STORE_CHANNELS

        elif channel == "public":
            channel = ["ticker", "trades", "orderbook"]

        elif channel == "private":
            channel = ["order", "execution", "position"]

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
        endpoint = self._parse_connect_endpoint(endpoint, client)
        endpoint_to_sends = self._parse_connect_send(endpoint, send, client)
        hdlr = self._parse_connect_hdlr(hdlr, client)

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
        for k, store in self._normalized_stores.items():
            if store is not None:
                store._onmessage(msg, ws)

    def _get_initialize_request_config(self, key: str) -> InitializeRequestConfig:
        if key not in self._INITIALIZE_CONFIG:
            self.log(
                f"Unsupported endpoint: {key}, "
                f"available endpoints are {list(self._INITIALIZE_CONFIG.keys())}",
                "warning",
            )
            return None, None, None

        config = self._INITIALIZE_CONFIG[key]

        if len(config) != 3 or not (
            isinstance(config[0], str)
            and isinstance(config[1], str)
            and (isinstance(config[2], (list, tuple)) or config[2] is None)
        ):
            raise RuntimeError(f"Invalid initialize endpoint: {config}")
        return config

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
        elif isinstance(cls_name_tuple, tuple) and len(cls_name_tuple) == 2:
            store_cls, store_name = cls_name_tuple
            assert issubclass(store_cls, NormalizedDataStore)
            if store_name is None:
                return store_cls()
            elif isinstance(store_name, str):
                try:
                    return store_cls(getattr(self.store, store_name))
                except AttributeError:
                    return None
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

    def _parse_connect_endpoint(self, endpoint: str, client: pybotters.Client) -> str:
        return endpoint or self._ws_channels.ENDPOINT

    def _parse_connect_send(
        self, endpoint: str, send: any, client: pybotters.Client
    ) -> dict[str, list[any]]:
        subscribe_lists = self._ws_channels.get()

        if len(subscribe_lists) == 0:
            if endpoint is None or send is None:
                raise RuntimeError("No channels got subscribed")
            return {endpoint: send}

        if endpoint is not None and send is not None:
            if endpoint in subscribe_lists:
                if isinstance(send, dict):
                    subscribe_lists[endpoint].append(send)
                elif isinstance(send, list):
                    subscribe_lists[endpoint] += send
                else:
                    raise TypeError(f"Invalid `send`: {send}")
            else:
                subscribe_lists[endpoint] = send

        return subscribe_lists

    def _parse_connect_hdlr(self, hdlr_json: any, client: pybotters.Client):
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

    def _get_normalized_store(self, name: str) -> NormalizedDataStore:
        store = self._normalized_stores[name]
        if store is None:
            raise RuntimeError(
                f"Unsupported normalized store: {name} ({self.exchange})"
            )
        return store

    def _initialize_request(
        self,
        client: "pybotters.Client",
        method: str,
        endpoint: str,
        params_or_data: dict | None = None,
        **kwargs,
    ):
        # exchange用のapiを使ってBASE_URLを足す
        import pybotters_wrapper as pbw

        api = pbw.create_api(self.exchange, client)
        params = dict(method=method, url=endpoint)
        params["params" if method == "GET" else "data"] = params_or_data
        return api.request(**params, **kwargs)

    async def _validate_initialize_response(self, task: asyncio.Task):
        result: ClientResponse = task.result()
        if result.status != 200:
            try:
                data = await result.json()
            except Exception:
                data = None
            raise RuntimeError(f"Initialization failed: {result.url} {data}")

    @property
    def store(self) -> T:
        return self._store

    # common stores
    @property
    def ticker(self) -> TickerStore:
        return self._get_normalized_store("ticker")

    @property
    def trades(self) -> TradesStore:
        return self._get_normalized_store("trades")

    @property
    def orderbook(self) -> OrderbookStore:
        return self._get_normalized_store("orderbook")

    @property
    def order(self) -> OrderStore:
        return self._get_normalized_store("order")

    @property
    def execution(self) -> ExecutionStore:
        return self._get_normalized_store("execution")

    @property
    def position(self) -> PositionStore:
        return self._get_normalized_store("position")

    @property
    def ws_connections(self) -> list[WebsocketConnection]:
        return self._ws_connections

    @property
    def ws_channels(self) -> WebsocketChannels:
        return self._ws_channels


class NormalizedDataStore(DataStore):
    _AVAILABLE_OPERATIONS = ("_insert", "_update", "_delete")

    def __init__(self, store: DataStore = None, auto_cast=False):
        super(NormalizedDataStore, self).__init__(auto_cast=auto_cast)
        self._store = store
        if self._store is not None:
            self._wait_task = asyncio.create_task(self._wait_store())
            self._watch_task = asyncio.create_task(self._watch_store())
        else:
            self._wait_task = None
            self._watch_task = None
        self._queue = pybotters.WebSocketQueue()
        self._queue_task = asyncio.create_task(self._wait_msg())

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self._store.__class__.__module__}.{self._store.__class__.__name__})"
        )

    def _onmessage(self, msg: "Item", ws: "ClientWebSocketResponse"):
        self._queue.onmessage(msg, ws)

    @logger.catch
    async def _wait_store(self):
        while True:
            await self._store.wait()
            self._on_wait()

    @logger.catch
    async def _watch_store(self):
        with self._store.watch() as stream:
            async for change in stream:
                self._on_watch(change)

    @logger.catch
    async def _wait_msg(self):
        async for msg in self._queue.iter_msg():
            self._on_msg(msg)

    def _on_wait(self):
        ...

    def _on_watch(self, change: "StoreChange"):
        op = self._get_operation(change)
        if op is not None:
            # StoreChange.[data|source]はdeep copyされたものが入っている
            normalized_data = self._normalize(
                change.store, change.operation, change.source, change.data
            )
            item = self._make_item(normalized_data, change)
            self._check_operation(op)
            op_fn = getattr(self, op)
            op_fn([item])

    def _get_operation(self, change: "StoreChange") -> str | None:
        return f"_{change.operation}"

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "Item":
        return data

    def _make_item(self, transformed_item: "Item", change: "StoreChange") -> "Item":
        # ストアに格納するアイテムとしてはchange.sourceは不要かもしれないが、watchした際に元のitemの
        # sourceをたどりたい場合がありうるので付帯させる
        return {
            **transformed_item,
            "info": {"data": change.data, "source": change.source},
        }

    def _check_operation(self, operation: str):
        if operation not in self._AVAILABLE_OPERATIONS:
            raise RuntimeError(
                f"Unsupported operation '{operation}' for {self.__class__.__name__}"
            )

    def _itemize(self, *args, **kwargs):
        raise NotImplementedError

    def _on_msg(self, msg: "Item"):
        ...


class TickerItem(TypedDict):
    symbol: str
    price: float


class TickerStore(NormalizedDataStore):
    _KEYS = ["symbol"]

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TickerItem":
        raise NotImplementedError

    def _itemize(self, symbol: str, price: float, **kwargs):
        # キーワード引数で任意の要素をアイテムに追加できる
        # 取引所ごとに_KEYSを変更したい場合などに使用（例：KucoinOrderbookStore）
        return TickerItem(symbol=symbol, price=price, **kwargs)  # noqa


class TradesItem(TypedDict):
    id: str
    symbol: str
    side: str
    price: float
    size: float
    timestamp: pd.Timestamp


class TradesStore(NormalizedDataStore):
    _KEYS = ["id", "symbol"]

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "TradesItem":
        raise NotImplementedError

    def _itemize(
        self,
        id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ) -> "TradesItem":
        return TradesItem(
            id=id,
            symbol=symbol,
            side=side,
            price=price,
            size=size,
            timestamp=timestamp,
            **kwargs,  # noqa
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

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderbookItem":
        raise NotImplementedError

    def _on_wait(self):
        sells, buys = self.sorted().values()
        if len(sells) != 0 and len(buys) != 0:
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

    def _itemize(self, symbol: str, side: str, price: float, size: float, **kwargs):
        return OrderbookItem(
            symbol=symbol, side=side, price=price, size=size, **kwargs  # noqa
        )

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

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "OrderItem":
        raise NotImplementedError

    def _itemize(
        self,
        id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        type: str,
        **kwargs,
    ):
        return OrderItem(
            id=id,
            symbol=symbol,
            side=side,
            price=price,
            size=size,
            type=type,
            **kwargs,  # noqa
        )


class ExecutionItem(TypedDict):
    id: str
    symbol: str
    side: str
    price: float
    size: float
    timestamp: pd.Timestamp


class ExecutionStore(NormalizedDataStore):
    _KEYS = []
    _AVAILABLE_OPERATIONS = ("_insert",)

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "ExecutionItem":
        raise NotImplementedError

    def _itemize(
        self,
        id: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
        timestamp: pd.Timestamp,
        **kwargs,
    ):
        return ExecutionItem(
            id=id,
            symbol=symbol,
            side=side,
            price=price,
            size=size,
            timestamp=timestamp,
            **kwargs,  # noqa
        )


class PositionItem(TypedDict):
    symbol: str
    side: str
    price: float
    size: float


class PositionStore(NormalizedDataStore):
    _KEYS = ["symbol", "side"]

    def _normalize(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> "PositionItem":
        raise NotImplementedError

    def _itemize(self, symbol: str, side: str, price: float, size: float, **kwargs):
        return PositionItem(
            symbol=symbol, side=side, price=price, size=size, **kwargs  # noqa
        )

    def size(self, side: str, symbol: str = None) -> float:
        query = {"side": side}
        if symbol:
            query["symbol"] = symbol
        return sum([x["size"] for x in self.find(query)])

    def price(self, side: str, symbol: str = None) -> float:
        query = {"side": side}
        if symbol:
            query["symbol"] = symbol
        positions = self.find(query)
        size = self.size(side)
        if size > 0:
            return sum([p["price"] * p["size"] for p in positions]) / size
        else:
            return 0

    def summary(self, symbol: str = None):
        rtn = {}
        for s in ["BUY", "SELL"]:
            rtn[f"{s}_size"] = self.size(s, symbol)
            rtn[f"{s}_price"] = self.price(s, symbol)

        if rtn["BUY_size"] > 0 and rtn["SELL_size"] == 0:
            rtn["side"] = "BUY"
        elif rtn["BUY_size"] == 0 and rtn["SELL_size"] > 0:
            rtn["side"] = "SELL"
        elif rtn["BUY_size"] > 0 and rtn["SELL_size"] > 0:
            rtn["side"] = "BOTH"
        else:
            rtn["side"] = None

        return rtn
