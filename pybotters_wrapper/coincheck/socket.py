from __future__ import annotations

from pybotters_wrapper.core import WebsocketChannels


class CoinCheckWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws-api.coincheck.com/"

    def _make_endpoint_and_request_pair(self, channel: str, **kwargs) -> [str, dict]:
        return self.ENDPOINT, {"type": "subscribe", "channel": channel}

    def ticker(self, symbol: str, **kwargs) -> CoinCheckWebsocketChannels:
        return self._subscribe(f"{symbol}-trades")

    def trades(self, symbol: str, **kwargs) -> CoinCheckWebsocketChannels:
        return self._subscribe(f"{symbol}-trades")

    def orderbook(self, symbol: str, **kwargs) -> CoinCheckWebsocketChannels:
        return self._subscribe(f"{symbol}-orderbook")
