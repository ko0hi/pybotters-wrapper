from typing import Literal

from ..websocket_channels import BybitWebSocketChannelsMixin
from ...core import WebSocketChannels


class BybitUSDTWebSocketChannels(
    BybitWebSocketChannelsMixin,
    WebSocketChannels[
        Literal[
            "instrument_info",
            "trade",
            "orderbook_l2_200",
            "stop_order",
            "wallet",
            "candle",
            "liquidation",
        ],
        str,
        str,
    ],
):
    _ENDPOINT = "wss://stream.bybit.com/realtime_public"
    _PUBLIC_ENDPOINT = _ENDPOINT
    _PRIVATE_ENDPOINT = "wss://stream.bybit.com/realtime_private"

    def _get_endpoint(self, parameter: str) -> str:
        if parameter in ("position", "execution", "order", "stop_order", "wallet"):
            return self._PRIVATE_ENDPOINT
        else:
            return self._PUBLIC_ENDPOINT

    def candle(self, symbol: str, interval: int | str = 1) -> str:
        return f"candle.{interval}.{symbol}"

    def liquidation(self, symbol: str) -> str:
        return f"liquidation.{symbol}"
