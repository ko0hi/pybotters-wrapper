from typing import Literal

from ..core import WebSocketChannels


class OKXWebSocketChannels(WebSocketChannels[Literal["ticker"], dict, dict]):
    _PUBLIC_ENDPOINT = "wss://ws.okx.com:8443/ws/v5/public"
    _PRIVATE_ENDPOINT = "wss://ws.okx.com:8443/ws/v5/private"
    _ENDPOINT = _PUBLIC_ENDPOINT

    def ticker(self, symbol: str, **kwargs) -> dict:
        return self.tickers(symbol)

    def trades(self, symbol: str, **kwargs) -> dict:
        return {"channel": "trades", "instId": symbol}

    def orderbook(self, symbol: str, **kwargs) -> dict:
        return self.books(symbol)

    def tickers(self, symbol: str) -> dict:
        return {"channel": "tickers", "instId": symbol}

    def books(self, symbol: str) -> dict:
        return {"channel": "books", "instId": symbol}

    def _parameter_template(self, parameter: dict) -> dict:
        return {"op": "subscribe", "args": [parameter]}
