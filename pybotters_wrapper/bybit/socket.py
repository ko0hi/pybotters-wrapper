from __future__ import annotations

from pybotters_wrapper.common import WebsocketChannels


class BybitWebsocketChannels(WebsocketChannels):
    def _make_endpoint_and_request_pair(self, *args):
        request = {"op": "subscribe", "args": list(args)}
        return self.ENDPOINT, request

    def ticker(self, symbol: str, **kwargs) -> BybitWebsocketChannels:
        return self.instrument_info(symbol)

    def trades(self, symbol: str, **kwargs) -> BybitWebsocketChannels:
        return self.trade(symbol)

    def orderbook(self, symbol: str, **kwargs) -> BybitWebsocketChannels:
        return self.orderbook_l2_200(symbol, 100)

    def order(self, **kwargs) -> BybitWebsocketChannels:
        return self._subscribe("order")

    def execution(self, **kwargs) -> BybitWebsocketChannels:
        return self._subscribe("execution")

    def position(self, **kwargs) -> BybitWebsocketChannels:
        return self._subscribe("position")

    def instrument_info(self, symbol: str) -> BybitWebsocketChannels:
        return self._subscribe(f"instrument_info.100ms.{symbol}")

    def trade(self, symbol: str) -> BybitWebsocketChannels:
        return self._subscribe(f"trade.{symbol}")

    def orderbook_l2_200(self, symbol: str, n: int) -> BybitWebsocketChannels:
        return self._subscribe(f"orderBook_200.{n}ms.{symbol}")

    def stop_order(self) -> BybitWebsocketChannels:
        return self._subscribe("stop_order")

    def wallet(self) -> BybitWebsocketChannels:
        return self._subscribe("wallet")


class BybitUSDTWebsocketChannels(BybitWebsocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime_public"
    PUBLIC_ENDPOINT = ENDPOINT
    PRIVATE_ENDPOINT = "wss://stream.bybit.com/realtime_private"

    def candle(
        self, symbol: str, interval: int | str = 1
    ) -> BybitUSDTWebsocketChannels:
        return self._subscribe(f"candle.{interval}.{symbol}")

    def liquidation(self, symbol: str) -> BybitUSDTWebsocketChannels:
        return self._subscribe(f"liquidation.{symbol}")


class BybitInverseWebsocketChannels(BybitWebsocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime"

    def insurance(self) -> BybitInverseWebsocketChannels:
        return self._subscribe("insurance")

    def kline_v2(
        self, symbol: str, interval: int | str = 1
    ) -> BybitInverseWebsocketChannels:
        return self._subscribe(f"klineV2.{interval}.{symbol}")

    def liquidation(self) -> BybitInverseWebsocketChannels:
        return self._subscribe("liquidation")
