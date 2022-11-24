from __future__ import annotations

from pybotters_wrapper.common import WebsocketChannels


class BybitWebsocketChannels(WebsocketChannels):
    def _make_endpoint_and_request_pair(self, *args):
        request = {"op": "subscribe", "args": list(args)}
        return self.ENDPOINT, request

    def ticker(self, symbol: str, **kwargs):
        return self.instrument(symbol, **kwargs)

    def trades(self, symbol: str, **kwargs):
        return self.trade(symbol)

    def orderbook(self, symbol: str, **kwargs):
        return self.orderbook_l2_200(symbol, 100)

    def instrument(self, symbol: str):
        return self._subscribe(f"instrument_info.100ms.{symbol}")

    def trade(self, symbol: str):
        return self._subscribe(f"trade.{symbol}")

    def orderbook_l2_200(self, symbol: str, n: int):
        return self._subscribe(f"orderBook_200.{n}ms.{symbol}")


class BybitUSDTWebsocketChannels(BybitWebsocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime_public"
    PUBLIC_ENDPOINT = ENDPOINT
    PRIVATE_ENDPOINT = "wss://stream.bybit.com/realtime_private"


class BybitInverseWebsocketChannels(BybitWebsocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime"
