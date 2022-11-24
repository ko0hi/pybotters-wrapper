from __future__ import annotations

from pybotters_wrapper.common import WebsocketChannels


class OKXWebsocketChannels(WebsocketChannels):
    PUBLIC_ENDPOINT = "wss://ws.okx.com:8443/ws/v5/public"
    PRIVATE_ENDPOINT = "wss://ws.okx.com:8443/ws/v5/private"
    ENDPOINT = PUBLIC_ENDPOINT

    def _make_endpoint_and_request_pair(self, channel, **kwargs):
        d = {"channel": channel}
        d.update(kwargs)
        params = {"op": "subscribe", "args": [d]}
        # TODO: private endpoint
        return self.ENDPOINT, params

    def ticker(self, symbol: str, **kwargs):
        return self.tickers(symbol)

    def trades(self, symbol: str, **kwargs):
        return self._subscribe("trades", instId=symbol)

    def orderbook(self, symbol: str, **kwargs):
        return self.books(symbol)

    def tickers(self, symbol: str):
        return self._subscribe("tickers", instId=symbol)

    def books(self, symbol: str):
        return self._subscribe("books", instId=symbol)
