from __future__ import annotations

from legacy.core import WebsocketChannels


class bitbankWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://stream.bitbank.cc/socket.io/?EIO=3&transport=websocket"

    def subscribe(
        self, channel: str | list[str], *args, **kwargs
    ) -> bitbankWebsocketChannels:
        return super().subscribe(channel, *args, **kwargs)

    def make_subscribe_request(self, channel: str | list[str], **kwargs) -> dict:
        if isinstance(channel, str):
            channel = [channel]
        return '42["join-room",' + ",".join([f'"{str(c)}"' for c in channel]) + "]"

    def ticker(self, symbol: str, **kwargs) -> bitbankWebsocketChannels:
        return self.subscribe(f"ticker_{symbol}")

    def trades(self, symbol: str, **kwargs) -> bitbankWebsocketChannels:
        return self.transaction(symbol)

    def orderbook(self, symbol: str, **kwargs) -> bitbankWebsocketChannels:
        return self.depth_whole(symbol)

    def transaction(self, symbol: str) -> bitbankWebsocketChannels:
        return self.subscribe(f"transactions_{symbol}")

    def depth_whole(self, symbol: str) -> bitbankWebsocketChannels:
        return self.subscribe(f"depth_whole_{symbol}")
