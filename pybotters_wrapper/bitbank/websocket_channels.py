from typing import Literal

from ..core import WebSocketChannels


class bitbankWebsocketChannels(
    WebSocketChannels[Literal["transaction", "depth_whole"], str, str]
):
    _ENDPOINT = "wss://stream.bitbank.cc/socket.io/?EIO=2&transport=websocket"

    def ticker(self, symbol: str, **kwargs) -> str:
        return f"ticker_{symbol}"

    def trades(self, symbol: str, **kwargs) -> str:
        return self.transaction(symbol)

    def orderbook(self, symbol: str, **kwargs) -> list[str]:
        return [self.depth_whole(symbol), self.depth_diff(symbol)]

    def depth_whole(self, symbol: str) -> str:
        return f"depth_whole_{symbol}"

    def depth_diff(self, symbol: str) -> str:
        return f"depth_diff_{symbol}"

    def transaction(self, symbol: str) -> str:
        return f"transactions_{symbol}"

    def _parameter_template(self, parameter: str) -> str:
        return f'42["join-room","{parameter}"]'
