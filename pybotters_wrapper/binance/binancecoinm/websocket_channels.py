import time
from typing import Literal

from ..listenkey_fetcher import DUMMY_LISTEN_KEY
from ...core import WebSocketChannels


class BinanceCOINMWebsocketChannels(
    WebSocketChannels[
        Literal[
            "agg_trades",
            "book_ticker",
            "depth",
            "kline",
            "continuous_kline",
            "liquidation",
            "mark_price",
            "index_price",
            "index_price_kline",
            "listenkey",
        ]
    ]
):
    _ENDPOINT = "wss://dstream.binance.com/ws"

    def ticker(self, symbol: str, **kwargs) -> str:
        return f"{symbol.lower()}@ticker"

    def trades(self, symbol: str, **kwargs) -> str:
        return self.agg_trades(symbol)

    def orderbook(self, symbol: str, **kwargs) -> str:
        return self.depth(symbol)

    def order(self, listen_key: str = None, **kwargs) -> str:
        return self.listenkey(listen_key)

    def execution(self, listen_key: str = None, **kwargs) -> str:
        return self.listenkey(listen_key)

    def position(self, listen_key: str = None, **kwargs) -> str:
        return self.listenkey(listen_key)

    def agg_trades(self, symbol: str) -> str:
        return f"{symbol.lower()}@aggTrade"

    def book_ticker(self, symbol: str) -> str:
        return f"{symbol.lower()}@bookTicker"

    def depth(self, symbol: str) -> str:
        return f"{symbol.lower()}@depth"

    def kline(self, symbol: str, interval: str) -> str:
        return f"{symbol.lower()}@kline_{interval}"

    def continuous_kline(self, pair: str, contract: str, interval: str) -> str:
        return f"{pair.lower()}_{contract.lower()}@continuousKline_{interval}"

    def liquidation(self, symbol: str) -> str:
        return f"{symbol.lower()}@forceOrder"

    def mark_price(self, symbol: str) -> str:
        return f"{symbol.lower()}@markPrice"

    def index_price(self, symbol: str, interval: str = "1s") -> str:
        return f"{symbol.lower()}@indexPrice@{interval}"

    def index_price_kline(self, symbol: str, interval: str) -> str:
        return f"{symbol.lower()}@indexPriceKline_{interval}"

    def listenkey(self, listen_key: str = None) -> str:
        return listen_key or DUMMY_LISTEN_KEY

    def _parameter_template(self, parameter: str) -> dict:
        return {
            "method": "SUBSCRIBE",
            "params": [parameter],
            "id": int(time.monotonic() * 10**9),
        }
