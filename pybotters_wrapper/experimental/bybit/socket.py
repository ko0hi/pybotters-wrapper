from __future__ import annotations

from pybotters_wrapper.core import WebsocketChannels


class BybitWebsocketChannels(WebsocketChannels):
    def subscribe(self, topic: str, *args, **kwargs) -> BybitWebsocketChannels:
        return super().subscribe(topic, *args, **kwargs)

    def make_subscribe_request(self, topic: str, *args, **kwargs) -> dict:
        return {"op": "subscribe", "args": [topic]}

    def ticker(self, symbol: str, **kwargs) -> BybitWebsocketChannels:
        return self.instrument_info(symbol)

    def trades(self, symbol: str, **kwargs) -> BybitWebsocketChannels:
        return self.trade(symbol)

    def orderbook(self, symbol: str, **kwargs) -> BybitWebsocketChannels:
        return self.orderbook_l2_200(symbol, 100)

    def order(self, **kwargs) -> BybitWebsocketChannels:
        return self.stop_order().subscribe("order")

    def execution(self, **kwargs) -> BybitWebsocketChannels:
        return self.subscribe("execution")

    def position(self, **kwargs) -> BybitWebsocketChannels:
        return self.subscribe("position")

    def instrument_info(self, symbol: str) -> BybitWebsocketChannels:
        return self.subscribe(f"instrument_info.100ms.{symbol}")

    def trade(self, symbol: str) -> BybitWebsocketChannels:
        return self.subscribe(f"trade.{symbol}")

    def orderbook_l2_200(self, symbol: str, n: int) -> BybitWebsocketChannels:
        return self.subscribe(f"orderBook_200.{n}ms.{symbol}")

    def stop_order(self) -> BybitWebsocketChannels:
        return self.subscribe("stop_order")

    def wallet(self) -> BybitWebsocketChannels:
        return self.subscribe("wallet")


class BybitUSDTWebsocketChannels(BybitWebsocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime_public"
    PUBLIC_ENDPOINT = ENDPOINT
    PRIVATE_ENDPOINT = "wss://stream.bybit.com/realtime_private"

    def subscribe(self, topic: str, *args, **kwargs) -> BybitUSDTWebsocketChannels:
        return super().subscribe(topic, *args, **kwargs)

    def make_subscribe_endpoint(self, topic: str, *args, **kwargs) -> str:
        if topic in ("position", "execution", "order", "stop_order", "wallet"):
            return self.PRIVATE_ENDPOINT
        else:
            return self.PUBLIC_ENDPOINT

    def candle(
        self, symbol: str, interval: int | str = 1
    ) -> BybitUSDTWebsocketChannels:
        return self.subscribe(f"candle.{interval}.{symbol}")

    def liquidation(self, symbol: str) -> BybitUSDTWebsocketChannels:
        return self.subscribe(f"liquidation.{symbol}")


class BybitInverseWebsocketChannels(BybitWebsocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime"

    def subscribe(self, topic: str, *args, **kwargs) -> BybitInverseWebsocketChannels:
        return super().subscribe(topic, *args, **kwargs)

    def insurance(self) -> BybitInverseWebsocketChannels:
        return self.subscribe("insurance")

    def kline_v2(
        self, symbol: str, interval: int | str = 1
    ) -> BybitInverseWebsocketChannels:
        return self.subscribe(f"klineV2.{interval}.{symbol}")

    def liquidation(self) -> BybitInverseWebsocketChannels:
        return self.subscribe("liquidation")
