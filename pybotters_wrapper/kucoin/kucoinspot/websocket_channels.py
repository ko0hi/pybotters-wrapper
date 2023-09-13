from typing import Literal
import uuid
from ...core import WebSocketChannels


def join_symbols(symbols):
    return symbols if isinstance(symbols, str) else ",".join(symbols)


class KuCoinSpotWebSocketChannels(
    WebSocketChannels[
        Literal[
            "market_ticker",
            "market_match",
            "spot_market_level2depth50",
            "spot_market_trade_orders",
        ],
        str,
        dict,
    ]
):
    _ENDPOINT = "DYNAMIC_ENDPOINT"

    def ticker(self, symbol: str, **kwargs) -> str:
        return self.market_ticker(symbol)

    def trades(self, symbol: str, **kwargs) -> str:
        return self.market_match(symbol)

    def orderbook(self, symbol: str, **kwargs) -> str:
        return self.spot_market_level2depth50(symbol)

    def order(self, **kwargs) -> str:
        return self.spot_market_trade_orders()

    def execution(self, **kwargs) -> str:
        return self.spot_market_trade_orders()

    def market_ticker(self, *symbols: str) -> str:
        return "/market/ticker:" + join_symbols(symbols)

    def market_match(self, *symbols: str) -> str:
        return "/market/match:" + join_symbols(symbols)

    def spot_market_level2depth50(self, *symbols: str) -> str:
        return "/spotMarket/level2Depth50:" + join_symbols(symbols)

    def spot_market_trade_orders(self) -> str:
        return "/spotMarket/tradeOrders"

    def _parameter_template(self, parameter: str) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "type": "subscribe",
            "topic": parameter,
            "response": True,
        }
