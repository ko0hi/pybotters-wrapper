import time
from typing import Literal, TypedDict

from ..core import WebSocketChannels


class PhemexWebsocketParameter(TypedDict):
    method: str
    params: list[str]


class PhemexWebsocketChannels(WebSocketChannels[Literal["tick", "trade"]]):
    _ENDPOINT = "wss://phemex.com/ws"

    def ticker(self, symbol: str, **kwargs) -> PhemexWebsocketParameter:
        if symbol.endswith("USD") and not symbol.startswith("."):
            # https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-tick-event-for-symbol-price
            symbol = "." + symbol.replace("USD", "")
        return self.tick(symbol)

    def trades(self, symbol: str, **kwargs) -> PhemexWebsocketParameter:
        return self.trade(symbol)

    def orderbook(self, symbol: str, **kwargs) -> PhemexWebsocketParameter:
        """https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-full-orderbook"""
        return {"method": "orderbook", "params": [symbol, True]}

    def tick(self, symbol: str) -> PhemexWebsocketParameter:
        """https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-tick-event-for-symbol-price"""
        return {"method": "tick", "params": [symbol]}

    def trade(self, symbol: str) -> PhemexWebsocketParameter:
        """https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-trade"""
        return {"method": "trade", "params": [symbol]}

    def _parameter_template(self, parameter: PhemexWebsocketParameter) -> dict:
        return {
            "id": int(time.monotonic() * 10**9),
            "method": parameter["method"] + ".subscribe",
            "params": parameter["params"],
        }
