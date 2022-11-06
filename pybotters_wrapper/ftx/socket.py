from pybotters_wrapper.common import WebsocketChannels


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
