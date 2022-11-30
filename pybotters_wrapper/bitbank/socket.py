from __future__ import annotations

from pybotters_wrapper.core import WebsocketChannels


class bitbankWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://stream.bitbank.cc/socket.io/?EIO=3&transport=websocket"

    def _make_endpoint_and_request_pair(self, *params, **kwargs) -> [str, str]:
        return (
            self.ENDPOINT,
            '42["join-room",' + ",".join([f'"{str(p)}"' for p in params]) + "]",
        )

    def ticker(self, symbol: str, **kwargs) -> bitbankWebsocketChannels:
        return self._subscribe(f"ticker_{symbol}")

    def trades(self, symbol: str, **kwargs) -> bitbankWebsocketChannels:
        return self.transaction(symbol)

    def orderbook(self, symbol: str, **kwargs) -> bitbankWebsocketChannels:
        return self.depth_whole(symbol)

    def transaction(self, symbol: str) -> bitbankWebsocketChannels:
        return self._subscribe(f"transactions_{symbol}")

    def depth_whole(self, symbol: str) -> bitbankWebsocketChannels:
        return self._subscribe(f"depth_whole_{symbol}")
