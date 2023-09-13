import uuid
from typing import Literal

from ...core import WebSocketChannels


class KuCoinFuturesWebSocketChannels(
    WebSocketChannels[
        Literal[
            "contract_market_ticker_v2",
            "contract_market_execution",
            "contract_market_level2depth50",
            "contract_market_trade_orders",
            "contract_position",
        ],
        str,
        dict,
    ]
):
    _ENDPOINT = "DYNAMIC_ENDPOINT"

    def ticker(self, symbol: str, **kwargs) -> str:
        return self.contract_market_ticker_v2(symbol)

    def trades(self, symbol: str, **kwargs) -> str:
        return self.contract_market_execution(symbol)

    def orderbook(self, symbol: str, **kwargs) -> str:
        return self.contract_market_level2depth50(symbol)

    def order(self, **kwargs) -> str:
        return self.contract_market_trade_orders()

    def execution(self, **kwargs) -> str:
        return self.contract_market_trade_orders()

    def position(self, **kwargs) -> str:
        assert "symbol" in kwargs, "symbol is required"
        return self.contract_position(kwargs["symbol"])

    def contract_market_ticker_v2(self, symbol: str) -> str:
        return f"/contractMarket/tickerV2:{symbol}"

    def contract_market_execution(self, symbol: str) -> str:
        return f"/contractMarket/execution:{symbol}"

    def contract_market_level2depth50(self, symbol: str) -> str:
        return f"/contractMarket/level2Depth50:{symbol}"

    def contract_market_trade_orders(self) -> str:
        return "/contractMarket/tradeOrders"

    def contract_position(self, symbol: str) -> str:
        return f"/contract/position:{symbol}"

    def _parameter_template(self, parameter: str) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "type": "subscribe",
            "topic": parameter,
            "response": True,
        }
