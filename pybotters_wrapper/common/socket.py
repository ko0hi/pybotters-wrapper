class SocketBase:
    ENDPOINT = None

    @classmethod
    def _subscribe(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def trades(cls, symbol, **kwargs):
        raise NotImplementedError

    @classmethod
    def book(cls, symbol, **kwargs):
        raise NotImplementedError

    @classmethod
    def all_channels(cls, *args, **kwargs):
        raise NotImplementedError
