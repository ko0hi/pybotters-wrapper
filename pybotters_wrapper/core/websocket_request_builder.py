from __future__ import annotations

from collections import defaultdict
from typing import TypeVar, Literal, Callable, Type

TWebsocketRequestBuilder = TypeVar(
    "TWebsocketRequestBuilder", bound="WebsocketRequestBuilder"
)
from .websocket_channels import WebSocketChannels
from .websocket_resquest_customizer import WebSocketRequestCustomizer


class WebSocketRequestBuilder:
    _ENDPOINT: str = None
    _DEFAULT_WEBSOCKET_CHANNELS_CLASS: Type[WebSocketChannels] = None

    def __init__(
        self,
        channels: WebSocketChannels | None = None,
    ):
        if channels is None:
            assert self._DEFAULT_WEBSOCKET_CHANNELS_CLASS is not None
        self._channels = channels or self._DEFAULT_WEBSOCKET_CHANNELS_CLASS()
        self._request_lists = defaultdict(list)

    def get(
        self,
        *,
        request_customizer: WebSocketRequestCustomizer = None,
    ) -> dict[str, list[dict | str]]:
        request_lists = self._request_lists
        if request_customizer is not None:
            new_lists = {}
            for endpoint, request_list in request_lists.items():
                new_lists[endpoint] = request_customizer(endpoint, request_list)
            request_lists = new_lists
        return request_lists

    def subscribe(
        self,
        channel: str
        | list[str | tuple[str, dict]]
        | Literal["all", "public", "private"],
        **kwargs,
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
            self._subscribe_by_channel_name(channel)
            item = self._channels.channel(channel, **kwargs)
            return self._register(item.endpoint, item.parameter)
        elif isinstance(channel, list):
            for _channel in channel:
                if isinstance(_channel, str):
                    self._subscribe_by_channel_name(_channel, **kwargs)
                elif isinstance(_channel, tuple):
                    self._subscribe_by_channel_name(_channel[0], **_channel[1])
                else:
                    raise TypeError(f"Unsupported: {_channel}")
            return self

    def subscribe_specific(
        self, endpoint: str, parameter: any
    ) -> TWebsocketRequestBuilder:
        return self._register(endpoint, parameter)

    def _subscribe_by_channel_name(
        self, channel_name: str, **kwargs
    ) -> TWebsocketRequestBuilder:
        item = self._channels.channel(channel_name, **kwargs)
        return self._register(item.endpoint, item.parameter)

    def _register(self, endpoint: str, parameter: any) -> TWebsocketRequestBuilder:
        self._request_lists[endpoint].append(parameter)
        return self

