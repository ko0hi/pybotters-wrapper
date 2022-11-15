from __future__ import annotations


import time
from pybotters_wrapper.common import WebsocketChannels


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


    # channels for normalized stores
    def ticker(self, symbol: str, **kwargs) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol}@ticker")

    def trades(self, symbol: str, **kwargs) -> BinanceWebsocketChannels:
        return self.agg_trades(symbol)

    def orderbook(self, symbol: str, **kwargs) -> BinanceWebsocketChannels:
        return self.depth(symbol)

    def order(self, listen_key: str, **kwargs) -> BinanceWebsocketChannels:
        return self.listenkey(listen_key)

    def execution(self, listen_key: str, **kwargs) -> BinanceWebsocketChannels:
        return self.listenkey(listen_key)

    def position(self, listen_key: str, **kwargs) -> BinanceWebsocketChannels:
        return self.listenkey(listen_key)

    # other channels
    def agg_trades(self, symbol: str) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol}@aggTrade")

    def book_ticker(self, symbol: str) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol}@bookTicker")

    def depth(self, symbol: str) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol}@depth")

    def kline(self, symbol: str, interval: str) -> BinanceWebsocketChannels:
        return self._subscribe(f"{symbol}@kline_{interval}")

    def listenkey(self, listen_key: str) -> BinanceWebsocketChannels:
        return self._subscribe(listen_key)


class BinanceSpotWebsocketChannels(BinanceWebsocketChannels):
    ENDPOINT = "wss://stream.binance.com/ws"


class BinanceFuturesWebsocketChannels(BinanceWebsocketChannels):
    def continuous_kline(
        self, pair: str, contract: str, interval: str
    ) -> WebsocketChannels:
        return self._subscribe(f"{pair}_{contract}@continuousKline_{interval}")

    def liquidation(self, symbol: str) -> BinanceFuturesWebsocketChannels:
        return self._subscribe(f"{symbol}@forceOrder")

    def mark_price(self, symbol: str) -> BinanceFuturesWebsocketChannels:
        return self._subscribe(f"{symbol}@markPrice")


class BinanceUSDSMWebsocketChannels(BinanceWebsocketChannels):
    ENDPOINT = "wss://fstream.binance.com/ws"

    def composite_index(self, symbol: str) -> BinanceUSDSMWebsocketChannels:
        return self._subscribe(f"{symbol}@compositeIndex")


class BinanceCOINMWebsocketChannels(BinanceWebsocketChannels):
    ENDPOINT = "wss://dstream.binance.com/ws"

    def index_price(
        self, symbol: str, interval: str = "1s"
    ) -> BinanceCOINMWebsocketChannels:
        return self._subscribe(f"{symbol}@indexPrice{interval}")

    def index_price_kline(
        self, symbol: str, interval: str
    ) -> BinanceCOINMWebsocketChannels:
        return self._subscribe(f"{symbol}@indexPriceKline_{interval}")
