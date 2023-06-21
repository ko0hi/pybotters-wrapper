from ..core import WebSocketChannels


class CoincheckWebsocketChannels(WebSocketChannels[None, str, dict]):
    _ENDPOINT = "wss://ws-api.coincheck.com/"

    def ticker(self, symbol: str, **kwargs) -> str:
        return f"{symbol}-trades"

    def trades(self, symbol: str, **kwargs) -> str:
        return f"{symbol}-trades"

    def orderbook(self, symbol: str, **kwargs) -> str:
        return f"{symbol}-orderbook"

    def _parameter_template(self, parameter: str) -> dict:
        return {
            "type": "subscribe",
            "channel": parameter,
        }
