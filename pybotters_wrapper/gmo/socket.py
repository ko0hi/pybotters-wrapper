from pybotters_wrapper.common import SocketChannels


class GMOSocketChannels(SocketChannels):
    PUBLIC_ENDPOINT = "wss://api.coin.z.com/ws/public/v1"
    PRIVATE_ENDPOINT = "wss://api.coin.z.com/ws/private/v1"
    ENDPOINT = PUBLIC_ENDPOINT

    @classmethod
    def _subscribe(cls, channel, **kwargs):
        params = {"command": "subscribe", "channel": channel}
        params.update(kwargs)
        return params

    @classmethod
    def ticker(cls, symbol):
        return cls._subscribe("ticker", symbol=symbol)

    @classmethod
    def orderbooks(cls, symbol):
        return cls._subscribe("orderbooks", symbol=symbol)

    @classmethod
    def trades(cls, symbol, option="TAKER_ONLY"):
        return cls._subscribe("trades", symbol=symbol, option=option)

    @classmethod
    def execution_events(cls):
        return cls._subscribe("executionEvents")

    @classmethod
    def order_events(cls):
        return cls._subscribe("orderEvents")

    @classmethod
    def position_events(cls):
        return cls._subscribe("positionEvents")

    @classmethod
    def position_summary_events(cls):
        return cls._subscribe("positionSummaryEvents")

    @classmethod
    def public_channels(cls, symbol):
        return [cls.ticker(symbol), cls.orderbooks(symbol), cls.trades(symbol)]

    @classmethod
    def private_channels(cls):
        return [
            cls.execution_events(),
            cls.order_events(),
            cls.position_events(),
            cls.position_summary_events(),
        ]

    @classmethod
    def all_channels(cls, symbol):
        return cls.public_channels(symbol) + cls.private_channels()

    @classmethod
    def get_public_channels(cls, send_json):
        return [
            sj
            for sj in send_json
            if sj["channel"] in ("ticker", "orderbooks", "trades")
        ]

    @classmethod
    def get_private_channels(cls, send_json):
        return [
            sj
            for sj in send_json
            if sj["channel"]
            in (
                "executionEvents",
                "orderEvents",
                "positionEvents",
                "positionSummaryEvents",
            )
        ]
