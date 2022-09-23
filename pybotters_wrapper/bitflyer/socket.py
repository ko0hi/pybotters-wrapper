from pybotters_wrapper.common import SocketBase


class BitflyerSocket(SocketBase):
    ID = 0
    ENDPOINT = "wss://ws.lightstream.bitflyer.com/json-rpc"

    @classmethod
    def _subscribe(cls, channel, **kwargs):
        params = {"method": "subscribe", "params": {"channel": channel, "id": cls.ID}}
        params.update(kwargs)
        BitflyerSocket.ID += 1
        return params

    @classmethod
    def ticker(cls, symbol):
        return cls._subscribe(f"lightning_ticker_{symbol}")

    @classmethod
    def board(cls, symbol):
        return cls._subscribe(f"lightning_board_{symbol}")

    @classmethod
    def book(cls, symbol, **kwargs):
        return [cls.board(symbol), cls.board_snapshot(symbol)]

    @classmethod
    def board_snapshot(cls, symbol):
        return cls._subscribe(f"lightning_board_snapshot_{symbol}")

    @classmethod
    def executions(cls, symbol):
        return cls._subscribe(f"lightning_executions_{symbol}")

    @classmethod
    def trades(cls, symbol, **kwargs):
        return cls.executions(symbol)

    @classmethod
    def child_order(cls):
        return cls._subscribe("child_order_events")

    @classmethod
    def parent_order(cls):
        return cls._subscribe("parent_order_envets")

    @classmethod
    def public_channels(cls, symbol):
        return [
            cls.ticker(symbol),
            cls.board(symbol),
            cls.board_snapshot(symbol),
            cls.executions(symbol),
        ]

    @classmethod
    def private_channels(cls):
        return [cls.child_order(), cls.parent_order()]

    @classmethod
    def all_channels(cls, symbol):
        return cls.public_channels(symbol) + cls.private_channels()
