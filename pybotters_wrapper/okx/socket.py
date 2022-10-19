from pybotters_wrapper.common import SocketChannels


class OKXSocketChannels(SocketChannels):
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
