from __future__ import annotations

import time

from pybotters_wrapper.core import WebsocketChannels


class BinanceWebsocketChannels(WebsocketChannels):
    def _make_endpoint_and_request_pair(self, params, **kwargs):
        if isinstance(params, str):
            params = [params]

        send_json = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": int(time.monotonic() * 10**9),
        }

        return self.ENDPOINT, send_json

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
        return self._subscribe(f"{symbol.lower()}@ticker")

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
        return self._subscribe(f"{symbol.lower()}@aggTrade")

    def book_ticker(self, symbol: str) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@bookTicker")

    def depth(self, symbol: str) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@depth")

    def kline(self, symbol: str, interval: str) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@kline_{interval}")

    def listenkey(self, listen_key: str) -> BinanceWebsocketChannels:
        return self._subscribe(listen_key)


class BinanceSpotWebsocketChannels(BinanceWebsocketChannels):
    ENDPOINT = "wss://stream.binance.com/ws"


class BinanceFuturesWebsocketChannels(BinanceWebsocketChannels):
    def continuous_kline(
        self, pair: str, contract: str, interval: str
    ) -> BinanceFuturesWebsocketChannels:
        return self._subscribe(
            f"{pair.lower()}_{contract.lower()}@continuousKline_{interval}"
        )

    def liquidation(self, symbol: str) -> BinanceFuturesWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@forceOrder")

    def mark_price(self, symbol: str) -> BinanceFuturesWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@markPrice")


class BinanceUSDSMWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://fstream.binance.com/ws"

    def composite_index(self, symbol: str) -> BinanceUSDSMWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@compositeIndex")


class BinanceUSDSMTESTWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://stream.binancefuture.com/ws"

    def composite_index(self, symbol: str) -> BinanceUSDSMTESTWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@compositeIndex")



class BinanceCOINMWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://dstream.binance.com/ws"

    def index_price(
        self, symbol: str, interval: str = "1s"
    ) -> BinanceCOINMWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@indexPrice@{interval}")

    def index_price_kline(
        self, symbol: str, interval: str
    ) -> BinanceCOINMWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@indexPriceKline_{interval}")


class BinanceCOINMTESTWebsocketChannels(BinanceFuturesWebsocketChannels):
    ENDPOINT = "wss://dstream.binancefuture.com/ws"

    def index_price(
        self, symbol: str, interval: str = "1s"
    ) -> BinanceCOINMTESTWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@indexPrice@{interval}")

    def index_price_kline(
        self, symbol: str, interval: str
    ) -> BinanceCOINMTESTWebsocketChannels:
        return self._subscribe(f"{symbol.lower()}@indexPriceKline_{interval}")