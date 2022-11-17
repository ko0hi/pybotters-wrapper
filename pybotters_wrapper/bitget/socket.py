from pybotters_wrapper.common import WebsocketChannels


class BitgetWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.bitget.com/mix/v1/stream"

    @classmethod
    def _subscribe(cls, channel, **kwargs):
        d = {"channel": channel}
        d.update(**kwargs)
        params = {"op": "subscribe", "args": [d]}
        print(params)
        return params

    @classmethod
    def trades(cls, symbol, inst_type="mc", **kwargs):
        return cls._subscribe(channel="trade", instType=inst_type, instId=symbol)

