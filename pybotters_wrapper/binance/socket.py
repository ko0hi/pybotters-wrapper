from pybotters_wrapper.common import SocketChannels


class BinanceSocketChannels(SocketChannels):
    ID = 0
    ENDPOINT = "wss://fstream.binance.com/ws"

    @classmethod
    def _subscribe(cls, params):
        if isinstance(params, str):
            params = [params]

        send_json = {"method": "SUBSCRIBE", "params": params, "id": cls.ID}
        cls.ID += 1

        return send_json

    @classmethod
    def trades(cls, symbol, **kwargs):
        return cls.agg_trades(symbol)

    @classmethod
    def agg_trades(cls, symbol):
        name = f"{symbol}@aggTrade"
        return cls._subscribe(name)

    @classmethod
    def mark_price(cls, symbol, every_seconds=False):
        name = f"{symbol}@markPrice"
        if every_seconds:
            name += "@1s"
        return cls._subscribe(name)

    @classmethod
    def kline(cls, symbol, interval="1m"):
        cls._check_interval(interval)
        name = f"{symbol}@kline_{interval}"
        return cls._subscribe(name)

    @classmethod
    def continuous_kline(cls, pair, contract, interval):
        cls._check_interval(interval)
        name = f"{pair}_{contract}@continuousKline_{interval}"
        return cls._subscribe(name)

    @classmethod
    def ticker(cls, symbol):
        name = f"{symbol}@ticker"
        return cls._subscribe(name)

    @classmethod
    def book_ticker(cls, symbol):
        name = f"{symbol}@bookTicker"
        return cls._subscribe(name)

    @classmethod
    def liquidation(cls, symbol):
        name = f"{symbol}@forceOrder"
        return cls._subscribe(name)

    @classmethod
    def depth_partial(cls, symbol, levels=20, update_speed=None):
        assert levels in [5, 10, 20]
        name = f"{symbol}@depth{levels}"
        if update_speed is not None:
            assert update_speed in [100, 500]
            name += f"@{update_speed}"
        return cls._subscribe(name)

    @classmethod
    def depth_diff(cls, symbol, update_speed=None):
        name = f"{symbol}@depth"
        if update_speed is not None:
            assert update_speed in [100, 500]
            name += f"@{update_speed}"
        return cls._subscribe(name)

    @classmethod
    def _check_interval(cls, interval):
        assert interval in [
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        ]
