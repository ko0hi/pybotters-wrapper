from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Generic, Literal

import aiohttp
import pybotters
from loguru import logger
from pybotters.store import DataStore

from .._typedefs import TDataStoreManager
from . import (
    ExecutionStore,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TickerStore,
    TradesStore,
    NormalizedDataStore,
)
from .exchange_property import ExchangeProperty
from .normalized_store_builder import NormalizedStoreBuilder
from .store_initializer import StoreInitializer
from .websocket_connection import WebSocketConnection, WebsocketOnReconnectionCallback
from .websocket_request_builder import WebSocketRequestBuilder
from .websocket_resquest_customizer import WebSocketRequestCustomizer

if TYPE_CHECKING:
    from pybotters import Item
    from pybotters.typedefs import WsBytesHandler, WsStrHandler


class DataStoreWrapper(Generic[TDataStoreManager]):
    def __init__(
        self,
        store: TDataStoreManager,
        *,
        exchange_property: ExchangeProperty,
        store_initializer: StoreInitializer,
        normalized_store_builder: NormalizedStoreBuilder,
        websocket_request_builder: WebSocketRequestBuilder,
        websocket_request_customizer: WebSocketRequestCustomizer,
    ):
        self._store = store
        self._ws_connections = []
        self._eprop = exchange_property
        self._initializer = store_initializer
        self._normalized_store_builder = normalized_store_builder
        self._normalized_stores = self._build_normalized_stores()
        self._ws_request_builder = websocket_request_builder
        self._websocket_request_customizer = websocket_request_customizer

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(
        self,
        aws_or_names: list[Awaitable[aiohttp.ClientResponse] | str | tuple[str, dict]],
        client: "pybotters.Client",
    ) -> "DataStoreWrapper":
        return await self._initializer.initialize(aws_or_names, client)

    def subscribe(
        self, channel: str | list[str] | list[tuple[str, dict]], **kwargs
    ) -> "DataStoreWrapper":
        self._ws_request_builder.subscribe(channel, **kwargs)
        return self

    async def connect(
        self,
        client: "pybotters.Client",
        *,
        endpoint: str = None,
        send: any = None,
        hdlr: WsStrHandler | WsBytesHandler = None,
        waits: list[DataStore | str] = None,
        send_type: Literal["json", "str", "byte"] = "json",
        hdlr_type: Literal["json", "str", "byte"] = "json",
        auto_reconnect: bool = False,
        on_reconnection: WebsocketOnReconnectionCallback | None = None,
        **kwargs,
    ) -> DataStoreWrapper:
        self._websocket_request_customizer.set_client(client)
        ws_requests = self._ws_request_builder.get(
            request_customizer=self._websocket_request_customizer
        )

        if hdlr is None:
            hdlr = self.onmessage
        else:
            if isinstance(hdlr, list):
                hdlr = hdlr + [self.onmessage]
            else:
                hdlr = [hdlr, self.onmessage]

        for _endpoint, _send in ws_requests:
            conn = WebSocketConnection(_endpoint, _send, hdlr, send_type, hdlr_type)
            await conn.connect(client, auto_reconnect, on_reconnection, **kwargs)
            self._ws_connections.append(conn)

        if endpoint is not None and send is not None:
            conn = WebSocketConnection(endpoint, send, hdlr, send_type, hdlr_type)
            await conn.connect(client, auto_reconnect, on_reconnection, **kwargs)
            self._ws_connections.append(conn)

        if waits is not None:
            await self._wait_socket_responses(waits)

        return self

    async def wait(self):
        await self._store.wait()

    async def close(self):
        for conn in self._ws_connections:
            await conn.close()

        for k, store in self._normalized_stores.items():
            if store is not None:
                await store.close()

    def onmessage(self, msg: "Item", ws: "ClientWebSocketResponse") -> None:
        self._store.onmessage(msg, ws)
        # NormalizedStoreの要素は通常watch経由で更新するが、１：１で対応するストアがない場合に、
        # 全てのwebsocket messageを入力とする経路を用意している
        for k, store in self._normalized_stores.items():
            if store is not None:
                store._onmessage(msg, ws)

    async def _wait_socket_responses(self, waits):
        waits = [getattr(self, w) if isinstance(w, str) else w for w in waits]

        while True:
            await self._store.wait()
            is_done = [len(w) > 0 for w in waits]
            logger.debug(
                f"Waiting responses ... "
                f"{dict(zip(map(lambda x: x.__class__.__name__, waits), is_done))}"
            )
            if all(is_done):
                break

    def _build_normalized_stores(self) -> dict[str, NormalizedDataStore]:
        stores = {}
        for name, store in self._normalized_store_builder.get().items():
            store.start()
            stores[name] = store
        return stores

    def _get_normalized_store(
        self, name: str
    ) -> (
        TickerStore
        | TradesStore
        | OrderbookStore
        | OrderStore
        | ExecutionStore
        | PositionStore
    ):
        store = self._normalized_stores[name]
        if store is None:
            raise RuntimeError(
                f"Unsupported normalized store for {self._eprop.exchange}: {name}"
            )
        return store

    @property
    def store(self) -> TDataStoreManager:
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
    def ws_connections(self) -> list[WebSocketConnection]:
        return self._ws_connections
