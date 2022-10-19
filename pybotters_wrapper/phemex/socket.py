from pybotters_wrapper.common import SocketChannels


class PhemexSocketChannels(SocketChannels):
    ENDPOINT = "wss://phemex.com/ws"
    ID = 0

    @classmethod
    def _subscribe(cls, method, *args):
        params = {"id": cls.ID, "method": method, "params": list(args)}
        cls.ID += 1
        return params

    @classmethod
    def trades(cls, symbol, **kwargs):
        return cls._subscribe("trade.subscribe", symbol)
