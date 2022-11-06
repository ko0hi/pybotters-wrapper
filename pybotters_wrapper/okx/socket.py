from pybotters_wrapper.common import WebsocketChannels


class OKXWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.okx.com:8443/ws/v5/public"

    @classmethod
    def _subscribe(cls, channel, **kwargs):
        d = {"channel": channel}
        d.update(kwargs)
        params = {"op": "subscribe", "args": [d]}
        return params

    @classmethod
    def trades(cls, symbol, *args):
        return cls._subscribe("trades", instId=symbol)
