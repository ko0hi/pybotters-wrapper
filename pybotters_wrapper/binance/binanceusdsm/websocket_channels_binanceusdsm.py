from typing import Literal

from ..common.listenkey_fetcher import DUMMY_LISTEN_KEY
from core.websocket_channels import WebSocketChannels


class BinanceUSDSMWebsocketChannels(
    WebSocketChannels[
        Literal[
            "agg_trades",
            "book_ticker",
            "depth",
            "kline",
            "listenkey",
            "continuous_kline",
            "mark_price",
            "composite_index",
        ]
    ]
):
    def ticker(self, symbol: str, **kwargs) -> str:
        return symbol

    def trades(self, symbol: str, **kwargs) -> str:
        return symbol

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

    def composite_index(self, symbol: str) -> str:
        return f"{symbol.lower()}@compositeIndex"

    def listenkey(self, listen_key: str = None) -> str:
        return listen_key or DUMMY_LISTEN_KEY
