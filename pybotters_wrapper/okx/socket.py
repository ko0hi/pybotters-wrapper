from pybotters_wrapper.common import WebsocketChannels


class OKXWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.okx.com:8443/ws/v5/public"

    def _make_endpoint_and_request_pair(self, channel, **kwargs):
        d = {"channel": channel}
        d.update(kwargs)
        params = {"op": "subscribe", "args": [d]}
        return self.ENDPOINT, params

    def ticker(self, symbol: str, **kwargs):
        return self._subscribe("tickers", instId=symbol)

    def trades(self, symbol: str, **kwargs):
        return self._subscribe("trades", instId=symbol)

    def orderbook(self, symbol: str, **kwargs):
        return self._subscribe("books", instId=symbol)
