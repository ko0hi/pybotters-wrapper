from __future__ import annotations

import asyncio
from typing import Callable, TypeVar, Optional, Literal, Union, Awaitable

import pybotters
from loguru import logger
from pybotters.typedefs import WsBytesHandler, WsJsonHandler, WsStrHandler
from pybotters.ws import WebSocketRunner

WsHandler = WsStrHandler | WsBytesHandler | WsJsonHandler

TWebsocketChannels = TypeVar("TWebsocketChannels", bound="WebsocketChannels")
WebsocketOnReconnectionCallback = Callable[
    ["WebsocketConnection", pybotters.Client], Union[None, Awaitable[None]]
]


class WebSocketConnection:
    def __init__(
        self,
        endpoint: str,
        send: dict | list[dict] | str,
        hdlr: WsHandler | list[WsHandler],
        send_type: Literal["json", "str", "byte"] = "json",
        hdlr_type: Literal["json", "str", "byte"] = "json",
    ):
        self._ws: WebSocketRunner | None = None
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
        on_reconnection: Optional[WebsocketOnReconnectionCallback] = None,
        **kwargs,
    ) -> WebSocketConnection:
        """
        WebSocketに接続します。

        Args:
            client (pybotters.Client): pybottersのクライアントインスタンス。
            auto_reconnect (bool, optional): 自動再接続を有効にするか。デフォルトは False。
            on_reconnection (WebsocketOnReconnectionCallback, optional): 再接続時に実行するコールバック。デフォルトは None。
            **kwargs: `pybotters.WebSocketRunner`の引数。

        Returns:
            WebSocketConnection: 自分自身のインスタンス。
        """
        await self._ws_connect(client, **kwargs)

        # pybotters自動で再接続するのでそれで事足りる？
        if auto_reconnect:
            asyncio.create_task(self._auto_reconnect(client, on_reconnection, **kwargs))

        return self

    async def close(self):
        if self._ws is not None:
            self._ws._task.cancel()
            try:
                await self._ws._task
            except asyncio.CancelledError:
                ...
        self._ws = None

    async def _auto_reconnect(
        self,
        client: "pybotters.Client",
        on_reconnection: Optional[WebsocketOnReconnectionCallback] = None,
        **kwargs,
    ):
        while True:
            if not self.connected:
                logger.debug(f"websocket disconnected: {self._endpoint} {self._send}")

                # 一部の取引所はトークンの更新などをしないといけないので、そういう時に使うはず。
                if on_reconnection is not None:
                    if asyncio.iscoroutinefunction(on_reconnection):
                        await on_reconnection(self, client)
                    else:
                        on_reconnection(self, client)

                # pybottersのWebSocketRunnerのタスクを終了する
                await self.close()

                await self._ws_connect(client, **kwargs)

                logger.debug(f"websocket recovered: {self._endpoint} {self._send}")

            await asyncio.sleep(15)

    async def _ws_connect(self, client: pybotters.Client, **kwargs):
        params = {
            f"send_{self._send_type}": self._send,
            f"hdlr_{self._hdlr_type}": self._hdlr,
        }
        self._ws = await client.ws_connect(self._endpoint, **params, **kwargs)

    @property
    def connected(self) -> bool:
        return self._ws and self._ws.connected
