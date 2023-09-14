from typing import Literal

from ..core import WebSocketChannels


class BitgetWebSocketChannels(
    WebSocketChannels[
        Literal[
            "books",
            "candlesticks",
            "account_inverse",
            "account_linear",
            "positions_inverse",
            "positions_linear",
            "orders_linear",
        ],
        dict,
        dict,
    ]
):
    _ENDPOINT = "wss://ws.bitget.com/mix/v1/stream"

    def ticker(self, symbol: str, **kwargs) -> dict:
        return {"channel": "ticker", "instId": symbol}

    def trades(self, symbol: str, **kwargs) -> dict:
        return {"channel": "trade", "instId": symbol}

    def orderbook(self, symbol: str, **kwargs) -> dict:
        return self.books(symbol)

    def books(self, symbol: str) -> dict:
        return {"channel": "books", "instId": symbol}

    def candlesticks(self, symbol: str, interval: str = "1m") -> dict:
        assert interval == "1m", "only '1m' interval is supported"
        return {"channel": f"candle{interval}", "instId": symbol}

    def account_inverse(self) -> dict:
        return {"channel": "account", "instId": "default", "instType": "DMCBL"}

    def account_linear(self) -> dict:
        return {"channel": "account", "instId": "default", "instType": "UMCBL"}

    def positions_inverse(self) -> dict:
        return {"channel": "positions", "instId": "default", "instType": "UMCBL"}

    def positions_linear(self) -> dict:
        return {"channel": "positions", "instId": "default", "instType": "UMCBL"}

    def orders_inverse(self) -> dict:
        return {"channel": "orders", "instId": "default", "instType": "UMCBL"}

    def orders_linear(self) -> dict:
        return {"channel": "orders", "instId": "default", "instType": "UMCBL"}

    def _parameter_template(self, parameter: dict) -> dict:
        parameter["instType"] = parameter.get("instType", "mc")
        return {"op": "subscribe", "args": [parameter]}
