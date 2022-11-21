from __future__ import annotations

from pybotters_wrapper.common import WebsocketChannels


class BitgetWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.bitget.com/mix/v1/stream"

    def _make_endpoint_and_request_pair(
        self, channel: str, params: dict, **kwargs
    ) -> [str, dict]:
        return self.ENDPOINT, {
            "op": "subscribe",
            "args": [{"channel": channel, "instType": "mc", **params}],
        }

    def ticker(self, symbol: str, **kwargs) -> BitgetWebsocketChannels:
        return self._subscribe("ticker", {"instId": symbol})

    def trades(self, symbol, **kwargs) -> BitgetWebsocketChannels:
        return self._subscribe("trade", {"instId": symbol})

    def orderbook(self, symbol: str, **kwargs) -> BitgetWebsocketChannels:
        return self.books(symbol)

    def books(self, symbol):
        return self._subscribe("books", {"instId": symbol})
