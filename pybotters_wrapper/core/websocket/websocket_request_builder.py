from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal, NamedTuple, Self

from .websocket_channels import WebSocketChannels
from .websocket_resquest_customizer import WebSocketRequestCustomizer


class WebsocketRequest(NamedTuple):
    endpoint: str
    send: str | dict | list[dict]


class WebSocketRequestBuilder:
    def __init__(self, channels: WebSocketChannels):
        self._channels = channels
        self._request_lists: dict = defaultdict(list)

    def get(
        self,
        *,
        request_customizer: WebSocketRequestCustomizer | None = None,
    ) -> list[WebsocketRequest]:
        if request_customizer is not None:
            new_lists = {}
            # 動的にリクエスト内容を書き換える必要がある場合にcustomizerを使う
            # （例：kucoinのwebsocket endopoint、binanceのlisten key）
            for endpoint, request_list in self._request_lists.items():
                new_endpoint, new_request_list = request_customizer(
                    endpoint, request_list
                )
                new_lists[new_endpoint] = new_request_list
            self._request_lists = new_lists
        return [WebsocketRequest(k, v) for (k, v) in self._request_lists.items()]

    def subscribe(
        self,
        channel: str
        | list[str | tuple[str, dict]]
        | Literal["all", "public", "private"],
        *,
        symbol: str | None = None,
        **kwargs,
    ) -> Self:
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

        kwargs["symbol"] = symbol

        if isinstance(channel, str):
            return self._subscribe_by_channel_name(channel, **kwargs)
        elif isinstance(channel, list):
            for _channel in channel:
                if isinstance(_channel, str):
                    self._subscribe_by_channel_name(_channel, **kwargs)
                elif isinstance(_channel, tuple):
                    self._subscribe_by_channel_name(_channel[0], **_channel[1])
                else:
                    raise TypeError(f"Unsupported: {_channel}")
            return self

    def subscribe_specific(self, endpoint: str, parameter: Any) -> Self:
        return self._register(endpoint, parameter)

    def _subscribe_by_channel_name(self, channel_name: str, **kwargs) -> Self:
        subscribe_item = self._channels.channel(channel_name, **kwargs)
        if isinstance(subscribe_item, list):
            for item in subscribe_item:
                self._register(item.endpoint, item.parameter)
        else:
            self._register(subscribe_item.endpoint, subscribe_item.parameter)
        return self

    def _register(self, endpoint: str, parameter: Any) -> Self:
        self._request_lists[endpoint].append(parameter)
        return self
