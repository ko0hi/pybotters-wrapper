from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable

if TYPE_CHECKING:
    from pybotters_wrapper.sandbox import SandboxEngine

import aiohttp
import pybotters
from pybotters.store import DataStore, DataStoreManager
from pybotters.typedefs import WsBytesHandler, WsStrHandler
from pybotters.ws import WebSocketRunner
from pybotters_wrapper.core import (
    DataStoreWrapper,
    ExecutionStore,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TickerStore,
    TradesStore,
    WebsocketChannels,
)


class SandboxDataStoreWrapper(DataStoreWrapper):
    # dummy
    _WRAP_STORE = DataStoreManager
    _WEBSOCKET_CHANNELS = WebsocketChannels

    def __init__(self, simulate_store=DataStoreWrapper):
        super(SandboxDataStoreWrapper, self).__init__()
        self._simulate_store = simulate_store
        self._store = self._simulate_store.store
        self._engine: SandboxEngine = None

        # overwrite
        self._INITIALIZE_CONFIG = self._simulate_store._INITIALIZE_CONFIG

    async def initialize(
        self,
        aws_or_names: list[Awaitable[aiohttp.ClientResponse] | str | tuple[str, dict]],
        client: "pybotters.Client" = None,
    ) -> "DataStoreWrapper":
        return await self._simulate_store.initialize(aws_or_names, client)

    def subscribe(
        self, channel: str | list[str] | list[tuple[str, dict]], **kwargs
    ) -> "DataStoreWrapper":
        return self._simulate_store.subscribe(channel, **kwargs)

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
        return await self._simulate_store.connect(
            client,
            endpoint=endpoint,
            send=send,
            hdlr=hdlr,
            waits=waits,
            send_type=send_type,
            hdlr_type=hdlr_type,
            auto_reconnect=auto_reconnect,
            on_reconnection=on_reconnection,
        )

    # public系はシミュレートするストアのものを返す
    # private系はsandbox固有のものを返す
    @property
    def ticker(self) -> TickerStore:
        return self._simulate_store.ticker

    @property
    def trades(self) -> TradesStore:
        return self._simulate_store.trades

    @property
    def orderbook(self) -> OrderbookStore:
        return self._simulate_store.orderbook

    # SandboxEngineによって正規化されたアイテムが挿入されるので_normalizeのオーバーライドなしでok
    def _init_execution_store(self) -> "ExecutionStore":
        return ExecutionStore()

    def _init_order_store(self) -> "OrderStore":
        return OrderStore()

    def _init_position_store(self) -> "PositionStore":
        return PositionStore()

    def _link_to_engine(self, engine: "SandboxEngine"):
        self._engine = engine

    @property
    def exchange(self) -> str:
        return self._simulate_store.exchange

    @property
    def package(self) -> str:
        return self._simulate_store.package
