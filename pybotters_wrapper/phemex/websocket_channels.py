import time
from typing import Literal, TypedDict

from ..core import WebSocketChannels


class PhemexWebsocketParameter(TypedDict):
    method: str
    params: list[str]


class PhemexWebsocketChannels(
    WebSocketChannels[Literal["tick", "trade"], PhemexWebsocketParameter, dict]
):
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
        return {"method": "orderbook", "params": [symbol, True]}  # type: ignore

    def order(self, **kwargs) -> PhemexWebsocketParameter:
        return self.aop()

    def position(self, **kwargs) -> PhemexWebsocketParameter:
        return self.aop()

    def execution(self, **kwargs) -> PhemexWebsocketParameter:
        return self.aop()

    def tick(self, symbol: str) -> PhemexWebsocketParameter:
        """https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-tick-event-for-symbol-price"""
        return {"method": "tick", "params": [symbol]}

    def trade(self, symbol: str) -> PhemexWebsocketParameter:
        """https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-trade"""
        return {"method": "trade", "params": [symbol]}

    def kline(self, symbol: str, interval: int) -> PhemexWebsocketParameter:
        supported_intervals = [
            60,
            300,
            900,
            1800,
            3600,
            14400,
            86400,
            604800,
            2592000,
            7776000,
            31104000,
        ]
        if interval not in supported_intervals:
            raise ValueError(
                f"Unsupported interval: {interval} (supported: {supported_intervals})"
            )
        return {"method": "kline", "params": [symbol, interval]}  # type: ignore

    def aop(self) -> PhemexWebsocketParameter:
        return {"method": "aop", "params": []}

    def _parameter_template(self, parameter: PhemexWebsocketParameter) -> dict:
        return {
            "id": int(time.monotonic() * 10**9),
            "method": parameter["method"] + ".subscribe",
            "params": parameter["params"],
        }
