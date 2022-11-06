from pybotters_wrapper.common import WebsocketChannels


class CoinCheckWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws-api.coincheck.com/"

    @classmethod
    def _subscribe(cls, **kwargs):
        params = {"type": "subscribe"}
        params.update(kwargs)
        return params

    @classmethod
    def trades(cls, symbol):
        return cls._subscribe(channel=f"{symbol}-trades")
