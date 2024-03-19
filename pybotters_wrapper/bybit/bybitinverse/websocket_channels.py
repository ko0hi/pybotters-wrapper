from typing import Literal

from ...core import WebSocketChannels
from ..websocket_channels import BybitWebSocketChannelsMixin


class BybitInverseWebSocketChannels(
    BybitWebSocketChannelsMixin,
    WebSocketChannels[
        Literal[
            "trade",
            "kline",
            "liquidation",
        ],
        str,
        dict,
    ],
):
    _ENDPOINT = "wss://stream.bybit.com/v5/public/inverse"
    _PUBLIC_ENDPOINT = _ENDPOINT
    _PRIVATE_ENDPOINT = "wss://stream.bybit.com/v5/private"
    _CATEGORY = "inverse"
