import logging
from typing import TYPE_CHECKING, Generic, TypeVar

import loguru
import pybotters
from pybotters.store import DataStore, DataStoreManager

from pybotters_wrapper.common import SocketBase

if TYPE_CHECKING:
    from pybotters import Item
    from pybotters.ws import ClientWebSocketResponse


class OnMessagePlugin:
    def onmessage(
        self, msg: "Item", ws: "ClientWebSocketResponse", store: "DataStoreManager"
    ) -> None:
        raise NotImplementedError


T = TypeVar("T", bound=DataStoreManager)


class DataStoreWrapper(Generic[T]):
    _SOCKET = None

    def __init__(self, store: T, logger: "logging.Logger" = None):
        self._store = store
        self._plugins = {}
        self._logger = logger or loguru.logger
        self._ws = None

    async def initialize(self, *args, **kwargs):
        return await self._store.initialize(*args, **kwargs)

    async def wait(self):
        await self._store.wait()

    def onmessage(self, msg: "Item", ws: "ClientWebSocketResponse") -> None:
        self._store.onmessage(msg, ws)

        for p in self._plugins.values():
            p.onmessage(msg, ws, self.store)

    def register(self, plugin: OnMessagePlugin, name: str = None) -> OnMessagePlugin:
        name = name or f"p{len(self._plugins)}"
        self._plugins[name] = plugin
        return plugin

    async def connect(
        self,
        client: "pybotters.Client",
        send_json,
        *,
        endpoint=None,
        onmessage=None,
        waits: list[DataStore] = None,
    ):
        endpoint = endpoint or self.socket.ENDPOINT

        if onmessage is None:
            hdlr_json = self.onmessage
        else:
            if isinstance(onmessage, list):
                fns = onmessage + [self.onmessage]
            else:
                fns = [onmessage, self.onmessage]
            hdlr_json = lambda msg, ws: [c(msg, ws) for c in fns]  # noqa

        self._ws = await client.ws_connect(
            endpoint, send_json=send_json, hdlr_json=hdlr_json
        )

        if waits is not None:
            waits = [getattr(self, w) if isinstance(w, str) else w for w in waits]
            await self._wait_socket_responses(waits)

        return self._ws

    async def _wait_socket_responses(self, waits):
        while not all([len(w) for w in waits]):
            self._logger.debug("[WAITING SOCKET RESPONSE]")
            await self._store.wait()

    def connected(self):
        if self._ws:
            return self._ws.connected
        else:
            return None

    @property
    def socket(self) -> SocketBase:
        return self._SOCKET

    @property
    def store(self) -> T:
        return self._store

    @property
    def plugins(self):
        return self._plugins

    @property
    def ws(self):
        return self._ws

    @property
    def board(self):
        raise NotImplementedError

    @property
    def trades(self):
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
