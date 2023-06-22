from typing import Literal
from ...core import WebSocketChannels
from ..websocket_channels import BybitWebSocketChannelsMixin


class BybitInverseWebSocketChannels(
    BybitWebSocketChannelsMixin,
    WebSocketChannels[
        Literal[
            "instrument_info",
            "trade",
            "orderbook_l2_200",
            "stop_order",
            "wallet",
            "insurance",
            "kline_v2",
            "liquidation",
        ],
        str,
        dict,
    ],
):
    _ENDPOINT = "wss://stream.bybit.com/realtime"

    def insurance(self) -> str:
        return "insurance"

    def kline_v2(self, symbol: str, interval: int | str = 1) -> str:
        return f"klineV2.{interval}.{symbol}"

    def liquidation(self) -> str:
        return "liquidation"
