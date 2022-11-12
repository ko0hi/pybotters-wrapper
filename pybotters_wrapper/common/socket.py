from typing import Callable
from collections import defaultdict

import asyncio

import pybotters
from pybotters.ws import WebSocketRunner
from pybotters.typedefs import WsStrHandler, WsBytesHandler, WsJsonHandler
from pybotters.store import DataStore

from pybotters_wrapper.utils import LoggingMixin


WsHandler = WsStrHandler | WsBytesHandler | WsJsonHandler


class WebsocketChannels(LoggingMixin):
    ENDPOINT = None

    def __init__(self):
        # endpoint-2-channels
        self._subscribe_list = defaultdict(list)
        self._cash = defaultdict(set)

    def add(self, channel, **kwargs):
        return getattr(self, channel)(**kwargs)

    def get_subscribe_list(self) -> dict[str, list]:
        return self._subscribe_list

    def _subscribe(self, *args, **kwargs) -> dict:
        endpoint, send = self._make_endpoint_and_request_pair(*args, **kwargs)
        send_str = str(send)
        if send_str not in self._cash[endpoint]:
            self._subscribe_list[endpoint].append(send)
            self._cash[endpoint].add(send_str)
            self.log(f"Add socket channel: {endpoint} / {send}")

        return endpoint, send

    def _make_endpoint_and_request_pair(self, *args, **kwargs) -> [str, dict]:
        raise NotImplementedError

    def ticker(self, symbol: str, **kwargs):
        raise NotImplementedError

    def trades(self, symbol: str, **kwargs):
        raise NotImplementedError

    def orderbook(self, symbol: str, **kwargs):
        raise NotImplementedError

    def order(self, **kwargs):
        raise NotImplementedError

    def position(self, **kwargs):
        raise NotImplementedError

    def all_channels(self, *args, **kwargs):
        raise NotImplementedError

    def public(self, **kwargs):
        raise NotImplementedError

    def private(self, **kwargs):
        raise NotImplementedError


class WebsocketConnection(LoggingMixin):
    def __init__(
        self,
        endpoint: str,
        send: any,
        hdlr: WsHandler | list[WsHandler],
        send_type: str = "json",
        hdlr_type: str = "json",
    ):
        self._ws: WebSocketRunner = None
        self._endpoint = endpoint
        self._send = send
        if isinstance(hdlr, list):
            hdlr = lambda msg, ws: [c(msg, ws) for c in hdlr]  # noqa
        self._hdlr = hdlr
        self._send_type = send_type
        self._hdlr_type = hdlr_type

    async def connect(
        self,
        client: "pybotters.Client",
        auto_reconnect: bool = False,
        on_reconnection: Callable = None,
        **kwargs,
    ) -> WebSocketRunner:
        params = {
            f"send_{self._send_type}": self._send,
            f"hdlr_{self._hdlr_type}": self._hdlr,
        }
        self._ws = await client.ws_connect(self._endpoint, **params, **kwargs)

        if auto_reconnect:
            asyncio.create_task(self._auto_reconnect(client, on_reconnection))

        return self

    async def _auto_reconnect(
        self, client: "pybotters.Client", on_reconnection: Callable = None, **kwargs
    ):
        while True:
            if not self.connected:
                self.log(f"websocket disconnected: {self._endpoint} {self._send}")
                self._ws._task.cancel()
                await self.connect(client, **kwargs)
                if on_reconnection:
                    if asyncio.iscoroutinefunction(on_reconnection):
                        await on_reconnection()
                    else:
                        on_reconnection()
                self.log(f"websocket recovered: {self._endpoint} {self._send}")

            await asyncio.sleep(15)

    @property
    def connected(self) -> bool:
        return self._ws and self._ws.connected
