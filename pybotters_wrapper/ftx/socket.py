from __future__ import annotations

from pybotters_wrapper.core import WebsocketChannels


class FTXWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ftx.com/ws"

    def _make_endpoint_and_request_pair(self, channel, **kwargs):
        params = {"op": "subscribe", "channel": channel}
        params.update(kwargs)
        return self.ENDPOINT, params

    def ticker(self, symbol: str, **kwargs):
        return self._subscribe("ticker", market=symbol)

    def trades(self, symbol, **kwargs):
        return self._subscribe("trades", market=symbol)

    def orderbook(self, symbol: str, **kwargs):
        return self._subscribe("orderbook", market=symbol)

    def order(self, **kwargs):
        return self._subscribe("orders")

    def execution(self, **kwargs):
        return self.fills()

    def position(self, **kwargs):
        return self.fills()

    def fills(self, **kwargs):
        return self._subscribe("fills")

    def orders(self, **kwargs):
        return self._subscribe("orders")
