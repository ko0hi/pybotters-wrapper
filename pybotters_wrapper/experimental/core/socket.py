from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Awaitable, Callable, TypeVar, Optional, Literal, Union

import pybotters
from pybotters.typedefs import WsBytesHandler, WsJsonHandler, WsStrHandler
from pybotters.ws import WebSocketRunner

from pybotters_wrapper.utils.mixins import LoggingMixin

WsHandler = WsStrHandler | WsBytesHandler | WsJsonHandler

TWebsocketChannels = TypeVar("TWebsocketChannels", bound="WebsocketChannels")


class WebsocketChannels(LoggingMixin):
    """Websocketのチャンネル購読リクエストを生成するクラス。各取引所の実装クラスでは

    - ENDPOINTを設定
    - `make_subscribe_request`のオーバーライド
    - `NormalizedDataStore`に対応する５つの購読メソッドを実装（storeがサポートされているもの）

    が必要になる。

    `make_subscribe_request`は任意の引数を取り、取引所に送る形式に変換する関数である。

    トピックによってendpointが変わる場合（例：GMOCoin）は `make_subscribe_endpoint`を
    オーバーライドして、動的にENDPOINTを定義すること。

    `make_subscribe_request`・`make_subscribe_endpoint`で生成されたリクエストとエンドポイントの
    ペアは`_subscribe_list`にエンドポイントをキーとして保存される。

    `_subscribe_list`は`get`で習得できる。リクエストの集約等行いたい場合は`get`をオーバーライドする。

    """

    ENDPOINT = None

    def __init__(self):
        # endpoint-2-channels
        self._subscribe_list = defaultdict(list)
        self._cash = defaultdict(set)

    def get(self) -> dict[str, list]:
        return self._subscribe_list

    def get_subscribe_list(self, endpoint: str = None, send: dict | list[dict] = None):
        subscribe_lists = self._subscribe_list
        if len(subscribe_lists) == 0:
            if endpoint is None or send is None:
                raise RuntimeError("Empty subscribe list")

        if endpoint is not None and send is not None:
            if endpoint in subscribe_lists:
                if isinstance(send, dict):
                    subscribe_lists[endpoint].append(send)
                elif isinstance(send, list) and isinstance(send[0], dict):
                    subscribe_lists[endpoint] += send
                else:
                    raise TypeError(f"Unsupported `send`: {send}")
            else:
                subscribe_lists[endpoint] = send
        return subscribe_lists

    def _make_subscribe_request(self, *args, **kwargs) -> dict:
        """購読リクエスト（i.e., `send_json`）を生成する。引数はsubscribeメソッドに準ずる。"""
        raise NotImplementedError

    def _make_subscribe_endpoint(self, *args, **kwargs) -> str:
        """エンドポイントを生成する。引数はsubscribeメソッドに準ずる。"""
        return self.ENDPOINT

    def _subscribe(self, *args, **kwargs) -> "TWebsocketChannels":
        """購読リストに追加する。引数は各取引所の実装クラスでオーバーロードする。"""
        send = self._make_subscribe_request(*args, **kwargs)
        endpoint = self._make_subscribe_endpoint(*args, **kwargs)

        endpoint = kwargs.get("endpoint", endpoint)
        send_str = str(send)

        if send_str not in self._cash[endpoint]:
            self._subscribe_list[endpoint].append(send)
            self._cash[endpoint].add(send_str)
            self.log(f"Add socket channel: {endpoint} / {send}")

        return self

    def ticker(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        """TickerStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def trades(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        """TradesStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def orderbook(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        """OrderbookStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def order(self, **kwargs) -> "TWebsocketChannels":
        """OrderStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def execution(self, **kwargs) -> "TWebsocketChannels":
        """ExecutionStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def position(self, **kwargs) -> "TWebsocketChannels":
        """PositionStore用のチャンネルをsubscribeする"""
        raise NotImplementedError

    def subscribe(
        self, channel: str | list[str | tuple[str, dict[str, any]]], **kwargs
    ):
        if channel == "all":
            channel = [
                "ticker",
                "trades",
                "orderbook",
                "order",
                "execution",
                "position",
            ]

        elif channel == "public":
            channel = ["ticker", "trades", "orderbook"]

        elif channel == "private":
            channel = ["order", "execution", "position"]

        if isinstance(channel, str):
            getattr(self, channel)(**kwargs)
        elif isinstance(channel, list):
            for item in channel:
                if isinstance(item, str):
                    getattr(self, item)(**kwargs)
                elif isinstance(item, tuple):
                    getattr(self, item[0])(**{**kwargs, **item[1]})


WebsocketOnReconnectionCallback = Callable[
    ["WebsocketConnection", pybotters.Client], Union[None, Awaitable[None]]
]


class WebsocketConnection(LoggingMixin):
    def __init__(
        self,
        endpoint: str,
        send: any,
        hdlr: WsHandler | list[WsHandler],
        send_type: Literal["json", "str", "byte"] = "json",
        hdlr_type: Literal["json", "str", "byte"] = "json",
    ):
        self._ws: Optional[WebSocketRunner] = None
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
    ) -> WebsocketConnection:
        """
        WebSocketに接続します。

        Args:
            client (pybotters.Client): pybottersのクライアントインスタンス。
            auto_reconnect (bool, optional): 自動再接続を有効にするか。デフォルトは False。
            on_reconnection (WebsocketOnReconnectionCallback, optional): 再接続時に実行するコールバック。デフォルトは None。
            **kwargs: `pybotters.WebSocketRunner`の引数。

        Returns:
            WebsocketConnection: 自分自身のインスタンス。
        """
        await self._ws_connect(client, **kwargs)

        # pybotters自動で再接続するのでそれで事足りる？
        if auto_reconnect:
            asyncio.create_task(self._auto_reconnect(client, on_reconnection, **kwargs))

        return self

    async def _auto_reconnect(
        self,
        client: "pybotters.Client",
        on_reconnection: Optional[WebsocketOnReconnectionCallback] = None,
        **kwargs,
    ):
        while True:
            if not self.connected:
                self.log(f"websocket disconnected: {self._endpoint} {self._send}")

                # 一部の取引所はトークンの更新などをしないといけないので、そういう時に使うはず。
                if on_reconnection is not None:
                    if asyncio.iscoroutinefunction(on_reconnection):
                        await on_reconnection(self, client)
                    else:
                        on_reconnection(self, client)

                # pybottersのWebSocketRunnerのタスクを終了する
                self._ws._task.cancel()

                await self._ws_connect(client, **kwargs)

                self.log(f"websocket recovered: {self._endpoint} {self._send}")

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

    @classmethod
    def from_websocket_channels(
        cls,
        client: "pybotters.Client",
        ws_channels: WebsocketChannels,
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
    ):
        endpoint = endpoint or ws_channels.ENDPOINT

        subscribe_lists = ws_channels.get()

        if len(subscribe_lists) == 0:
            if endpoint is None or send is None:
                raise RuntimeError("No subscribe list")

        if endpoint is not None and send is not None:
            if endpoint in subscribe_lists:
                if isinstance(send, dict):
                    subscribe_lists[endpoint].append(send)
                elif isinstance(send, list) and isinstance(send[0], dict):
                    subscribe_lists[endpoint] += send
                else:
                    raise TypeError(f"Unsupported `send`: {send}")
            else:
                subscribe_lists[endpoint] = send

