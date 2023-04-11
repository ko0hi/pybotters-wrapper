from __future__ import annotations

import time

from legacy.core import WebsocketChannels


class BinanceWebsocketChannels(WebsocketChannels):
    def subscribe(
        self, params: str | list[str], *args, **kwargs
    ) -> BinanceWebsocketChannels:
        return super().subscribe(params, *args, **kwargs)

    def make_subscribe_request(self, params: str | list[str], *args, **kwargs) -> dict:
        if isinstance(params, str):
            params = [params]
        return {
            "method": "SUBSCRIBE",
            "params": params,
            "id": int(time.monotonic() * 10**9),
        }

    def get(self) -> dict[str, list]:
        compressed = {}
        for endpoint, sends in self._subscribe_list.items():
            compressed[endpoint] = [
                {
                    "method": "SUBSCRIBE",
                    "params": [s["params"][0] for s in sends],
                    "id": sends[0]["id"],
                }
            ]
        return compressed

    # channels for normalized stores
    def ticker(self, symbol: str, **kwargs) -> BinanceWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@ticker")

    def trades(self, symbol: str, **kwargs) -> BinanceWebsocketChannels:
        return self.agg_trades(symbol)

    def orderbook(self, symbol: str, **kwargs) -> BinanceWebsocketChannels:
        return self.depth(symbol)

    def order(
        self, listen_key: str = "LISTEN_KEY", **kwargs
    ) -> BinanceWebsocketChannels:
        return self.listenkey(listen_key)

    def execution(
        self, listen_key: str = "LISTEN_KEY", **kwargs
    ) -> BinanceWebsocketChannels:
        return self.listenkey(listen_key)

    def position(
        self, listen_key: str = "LISTEN_KEY", **kwargs
    ) -> BinanceWebsocketChannels:
        return self.listenkey(listen_key)

    # other channels
    def agg_trades(self, symbol: str) -> BinanceWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@aggTrade")

    def book_ticker(self, symbol: str) -> BinanceWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@bookTicker")

    def depth(self, symbol: str) -> BinanceWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@depth")

    def kline(self, symbol: str, interval: str) -> BinanceWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@kline_{interval}")

    def listenkey(self, listen_key: str) -> BinanceWebsocketChannels:
        return self.subscribe(listen_key)


class BinanceSpotWebsocketChannels(BinanceWebsocketChannels):
    ENDPOINT = "wss://stream.binance.com/ws"

    def subscribe(
        self, params: str | list[str], *args, **kwargs
    ) -> BinanceSpotWebsocketChannels:
        return super().subscribe(params, *args, **kwargs)


class BinanceFuturesWebsocketChannels(BinanceWebsocketChannels):
    def continuous_kline(
        self, pair: str, contract: str, interval: str
    ) -> BinanceFuturesWebsocketChannels:
        return self.subscribe(
            f"{pair.lower()}_{contract.lower()}@continuousKline_{interval}"
        )

    def liquidation(self, symbol: str) -> BinanceFuturesWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@forceOrder")

    def mark_price(self, symbol: str) -> BinanceFuturesWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@markPrice")


class BinanceUSDSMWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://fstream.binance.com/ws"

    def subscribe(
        self, params: str | list[str], *args, **kwargs
    ) -> BinanceUSDSMWebsocketChannels:
        return super().subscribe(params, *args, **kwargs)

    def composite_index(self, symbol: str) -> BinanceUSDSMWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@compositeIndex")


class BinanceUSDSMTESTWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://stream.binancefuture.com/ws"

    def subscribe(
        self, params: str | list[str], *args, **kwargs
    ) -> BinanceUSDSMTESTWebsocketChannels:
        return super().subscribe(params, *args, **kwargs)

    def composite_index(self, symbol: str) -> BinanceUSDSMTESTWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@compositeIndex")


class BinanceCOINMWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://dstream.binance.com/ws"

    def subscribe(
        self, params: str | list[str], *args, **kwargs
    ) -> BinanceCOINMWebsocketChannels:
        return super().subscribe(params, *args, **kwargs)

    def index_price(
        self, symbol: str, interval: str = "1s"
    ) -> BinanceCOINMWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@indexPrice@{interval}")

    def index_price_kline(
        self, symbol: str, interval: str
    ) -> BinanceCOINMWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@indexPriceKline_{interval}")


class BinanceCOINMTESTWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://dstream.binancefuture.com/ws"

    def subscribe(
        self, params: str | list[str], *args, **kwargs
    ) -> BinanceCOINMTESTWebsocketChannels:
        return super().subscribe(params, *args, **kwargs)

    def index_price(
        self, symbol: str, interval: str = "1s"
    ) -> BinanceCOINMTESTWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@indexPrice@{interval}")

    def index_price_kline(
        self, symbol: str, interval: str
    ) -> BinanceCOINMTESTWebsocketChannels:
        return self.subscribe(f"{symbol.lower()}@indexPriceKline_{interval}")
