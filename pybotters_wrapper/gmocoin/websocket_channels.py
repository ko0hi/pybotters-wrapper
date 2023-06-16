from ..core import WebSocketChannels


class GMOCoinWebsocketChannels(WebSocketChannels):
    _PUBLIC_ENDPOINT = "wss://api.coin.z.com/ws/public/v1"
    _PRIVATE_ENDPOINT = "wss://api.coin.z.com/ws/private/v1"
    _ENDPOINT = _PUBLIC_ENDPOINT

    def ticker(self, symbol: str, **kwargs) -> dict:
        return {
            "channel": "ticker",
            "symbol": symbol,
        }

    def trades(self, symbol: str, option: str = "TAKER_ONLY", **kwargs) -> dict:
        return {
            "channel": "trades",
            "symbol": symbol,
            "option": option,
        }

    def orderbook(self, symbol: str, **kwargs) -> dict:
        return self.orderbooks(symbol)

    def order(self, **kwargs) -> dict:
        return self.order_events()

    def execution(self, **kwargs) -> dict:
        return self.execution_events()

    def position(self, **kwargs) -> dict:
        return self.position_events()

    def orderbooks(self, symbol: str) -> dict:
        return {
            "channel": "orderbooks",
            "symbol": symbol,
        }

    def execution_events(self) -> dict:
        return {"channel": "executionEvents"}

    def order_events(self) -> dict:
        return {"channel": "orderEvents"}

    def position_events(self) -> dict:
        return {"channel": "positionEvents"}

    def position_summary_events(self) -> dict:
        return {"channel": "positionSummaryEvents"}

    def _get_endpoint(self, parameter: dict) -> str:
        return (
            self._PRIVATE_ENDPOINT
            if parameter["channel"].endswith("Events")
            else self._PUBLIC_ENDPOINT
        )

    def _parameter_template(self, parameter: dict) -> dict:
        return {
            "command": "subscribe",
            **parameter,
        }
