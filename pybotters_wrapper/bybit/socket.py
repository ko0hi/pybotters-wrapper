from pybotters_wrapper.common import SocketChannels


class BybitSocket(SocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime"

    @classmethod
    def _subscribe(cls, *args):
        params = {"op": "subscribe", "args": list(args)}
        return params

    @classmethod
    def trades(cls, symbol, **kwargs):
        return cls._subscribe(f"trade.{symbol}")
