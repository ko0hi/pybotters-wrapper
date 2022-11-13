import uuid

from pybotters_wrapper.common import WebsocketChannels


class KucoinWebsocketChannels(WebsocketChannels):
    def _make_endpoint_and_request_pair(self, channel: str, **kwargs) -> [str, dict]:
        return None, {
            "id": str(uuid.uuid4()),
            "type": "subscribe",
            "topic": channel,
            "response": True,
        }

    def _join_symbols(self, symbols):
        if isinstance(symbols, str):
            return symbols
        else:
            return ",".join(symbols)


class KucoinSpotWebsocketChannels(KucoinWebsocketChannels):
    def ticker(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        return self.market_ticker(symbol)

    def trades(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        return self.market_match(symbol)

    def orderbook(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        return self.spot_market_level2depth50(symbol)

    def order(self, **kwargs) -> "TWebsocketChannels":
        return self.spot_market_trade_orders()

    def execution(self, **kwargs) -> "TWebsocketChannels":
        return self.spot_market_trade_orders()

    def market_ticker(self, *symbols: str):
        return self._subscribe("/market/ticker:" + self._join_symbols(symbols))

    def market_match(self, *symbols: str):
        return self._subscribe("/market/match:" + self._join_symbols(symbols))

    def spot_market_level2depth50(self, *symbols: str):
        return self._subscribe(
            "/spotMarket/level2Depth50:" + self._join_symbols(symbols)
        )

    def spot_market_trade_orders(self):
        return self._subscribe("/spotMarket/tradeOrders")


class KucoinFuturesWebsocketChannels(KucoinWebsocketChannels):
    def ticker(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        return self.contract_market_ticker_v2(symbol)

    def trades(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        return self.contract_market_execution(symbol)

    def orderbook(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        return self.contract_market_level2depth50(symbol)

    def order(self, **kwargs) -> "TWebsocketChannels":
        return self.contract_market_trade_orders()

    def execution(self, **kwargs) -> "TWebsocketChannels":
        return self.contract_market_trade_orders()

    def position(self, symbol: str, **kwargs) -> "TWebsocketChannels":
        return self.contract_position(symbol)

    def contract_market_ticker_v2(self, symbol: str):
        return self._subscribe(f"/contractMarket/tickerV2:{symbol}")

    def contract_market_execution(self, symbol: str):
        return self._subscribe(f"/contractMarket/execution:{symbol}")

    def contract_market_level2depth50(self, symbol: str):
        return self._subscribe(f"/contractMarket/level2Depth50:{symbol}")

    def contract_market_trade_orders(self):
        return self._subscribe("/contractMarket/tradeOrders")

    def contract_position(self, symbol: str):
        return self._subscribe(f"/contract/position: {symbol}")
