from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Literal, cast

if TYPE_CHECKING:
    from pybotters.store import Item
    from pybotters.ws import ClientWebSocketResponse

import aiohttp
import pybotters
from pybotters.store import DataStore
from pybotters.typedefs import WsBytesHandler, WsStrHandler

from pybotters_wrapper.core import (
    ExecutionStore,
    OrderbookStore,
    OrderStore,
    PositionStore,
    TDataStoreManager,
    TickerStore,
    TradesStore,
    TWebsocketOnReconnectionCallback,
)

from ..core import DataStoreWrapper
from .engine import SandboxEngine


class SandboxDataStoreWrapper(DataStoreWrapper[TDataStoreManager]):
    def __init__(self, simulate_store: DataStoreWrapper):
        self._simulate_store = simulate_store
        self._store = self._simulate_store.store
        self._engine: SandboxEngine | None = None
        super(SandboxDataStoreWrapper, self).__init__(
            None,  # type: ignore
            exchange_property=self._simulate_store._eprop,
            store_initializer=None,  # type: ignore
            normalized_store_builder=None,  # type: ignore
            websocket_request_customizer=None,  # type: ignore
            websocket_request_builder=None,  # type: ignore
        )

    def _build_normalized_stores(
        self,
    ) -> dict[
        str,
        TickerStore
        | TradesStore
        | OrderbookStore
        | OrderStore
        | ExecutionStore
        | PositionStore,
    ]:
        return {
            "order": OrderStore(None),
            "execution": ExecutionStore(None),
            "position": PositionStore(None),
        }

    async def initialize(
        self,
        aws_or_names: list[Awaitable[aiohttp.ClientResponse] | str | tuple[str, dict]],
        client: "pybotters.Client",
    ) -> SandboxDataStoreWrapper:
        await self._simulate_store.initialize(aws_or_names, client)
        return self

    async def initialize_token(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_token(client, **params)

    async def initialize_token_public(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_token_public(client, **params)

    async def initialize_token_private(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_token_private(client, **params)

    async def initialize_ticker(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_ticker(client, **params)

    async def initialize_trades(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_trades(client, **params)

    async def initialize_orderbook(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_orderbook(client, **params)

    async def initialize_order(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_order(client, **params)

    async def initialize_execution(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_execution(client, **params)

    async def initialize_position(self, client: "pybotters.Client", **params):
        return await self._simulate_store.initialize_position(client, **params)

    def subscribe(
        self,
        channel: str
        | list[str | tuple[str, dict]]
        | Literal["all", "public", "private"],
        symbol: str | None = None,
        **kwargs,
    ) -> SandboxDataStoreWrapper:
        self._simulate_store.subscribe(channel, symbol=symbol, **kwargs)
        return self

    async def connect(
        self,
        client: "pybotters.Client",
        *,
        endpoint: str | None = None,
        send: Any | None = None,
        hdlr: WsStrHandler | WsBytesHandler = None,
        waits: list[DataStore | str] | None = None,
        send_type: Literal["json", "str", "byte"] | None = None,
        hdlr_type: Literal["json", "str", "byte"] | None = None,
        auto_reconnect: bool = False,
        on_reconnection: TWebsocketOnReconnectionCallback | None = None,
        **kwargs,
    ) -> SandboxDataStoreWrapper:
        await self._simulate_store.connect(
            client,
            endpoint=endpoint,
            send=send,
            hdlr=hdlr,
            waits=waits,
            send_type=send_type,
            hdlr_type=hdlr_type,
            auto_reconnect=auto_reconnect,
            on_reconnection=on_reconnection,
            **kwargs,
        )

        return self

    async def wait(self):
        await self._simulate_store.wait()

    async def close(self):
        await self._simulate_store.close()

    def onmessage(self, msg: Item, ws: ClientWebSocketResponse) -> None:
        self._simulate_store.onmessage(msg, ws)

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

    @property
    def order(self) -> OrderStore:
        return cast(OrderStore, self._normalized_stores["order"])

    @property
    def execution(self) -> ExecutionStore:
        return cast(ExecutionStore, self._normalized_stores["execution"])

    @property
    def position(self) -> PositionStore:
        return cast(PositionStore, self._normalized_stores["position"])

    def _link_to_engine(self, engine: "SandboxEngine"):
        self._engine = engine

    @property
    def exchange(self) -> str:
        return self._simulate_store._eprop.exchange
