from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Callable, TypeVar

import pybotters
from pybotters.typedefs import WsBytesHandler, WsJsonHandler, WsStrHandler
from pybotters.ws import WebSocketRunner
from pybotters_wrapper.utils.mixins import LoggingMixin

WsHandler = WsStrHandler | WsBytesHandler | WsJsonHandler

TWebsocketChannels = TypeVar("TWebsocketChannels", bound="WebsocketChannels")


class WebsocketChannels(LoggingMixin):
    ENDPOINT = None

    def __init__(self):
        # endpoint-2-channels
        self._subscribe_list = defaultdict(list)
        self._cash = defaultdict(set)

    def get(self) -> dict[str, list]:
        return self._subscribe_list

    def make_subscribe_request(self, *args, **kwargs) -> dict:
        """ 購読リクエスト（i.e., `send_json`）を生成する。引数はsubscribeメソッドに準ずる。
        """
        raise NotImplementedError

    def make_subscribe_endpoint(self, *args, **kwargs) -> str:
        """ エンドポイントを生成する。引数はsubscribeメソッドに準ずる。
        """
        return self.ENDPOINT

    def subscribe(self, *args, **kwargs) -> "TWebsocketChannels":
        """ 購読リストに追加する。引数は各取引所の実装クラスでオーバーロードする。
        """
        send = self.make_subscribe_request(*args, **kwargs)
        endpoint = self.make_subscribe_endpoint(*args, **kwargs)

        endpoint = kwargs.get("endpoint", endpoint)
        send_str = str(send)

        if send_str not in self._cash[endpoint]:
            self._subscribe_list[endpoint].append(send)
            self._cash[endpoint].add(send_str)
            self.log(f"Add socket channel: {endpoint} / {send}")

        return self

    def ticker(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        raise NotImplementedError

    def trades(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        raise NotImplementedError

    def orderbook(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        raise NotImplementedError

    def order(self, **kwargs) -> "TWebsocketChannels":
        raise NotImplementedError

    def execution(self, **kwargs) -> "TWebsocketChannels":
        raise NotImplementedError

    def position(self, **kwargs) -> "TWebsocketChannels":
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
            self._hdlr = lambda msg, ws: [c(msg, ws) for c in hdlr]  # noqa
        else:
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
            asyncio.create_task(self._auto_reconnect(client, on_reconnection, **kwargs))

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
