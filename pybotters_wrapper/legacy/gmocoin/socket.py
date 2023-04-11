from __future__ import annotations

from legacy.core import WebsocketChannels


class GMOWebsocketChannels(WebsocketChannels):
    PUBLIC_ENDPOINT = "wss://api.coin.z.com/ws/public/v1"
    PRIVATE_ENDPOINT = "wss://api.coin.z.com/ws/private/v1"
    ENDPOINT = PUBLIC_ENDPOINT

    def subscribe(
        self, channel: str, **kwargs
    ) -> GMOWebsocketChannels:
        return super().subscribe(channel, **kwargs)

    def make_subscribe_request(
        self, channel: str, **kwargs
    ) -> dict:

        return {"command": "subscribe", "channel": channel, **kwargs}

    def make_subscribe_endpoint(
        self, channel: str, **kwargs
    ) -> str:
        return self.PRIVATE_ENDPOINT if channel.endswith("Events") else self.PUBLIC_ENDPOINT

    def _make_endpoint_and_request_pair(self, channel, **kwargs):
        params = {"command": "subscribe", "channel": channel}
        params.update(kwargs)

        endpoint = (
            self.PRIVATE_ENDPOINT
            if channel.endswith("Events")
            else self.PUBLIC_ENDPOINT
        )

        return endpoint, params

    def ticker(self, symbol, **kwargs) -> GMOWebsocketChannels:
        return self.subscribe("ticker", symbol=symbol)

    def trades(self, symbol, option="TAKER_ONLY", **kwargs) -> GMOWebsocketChannels:
        return self.subscribe("trades", symbol=symbol, option=option)

    def orderbook(self, symbol, **kwargs) -> GMOWebsocketChannels:
        return self.orderbooks(symbol)

    def order(self, **kwargs) -> GMOWebsocketChannels:
        return self.order_events()

    def execution(self, **kwargs) -> GMOWebsocketChannels:
        return self.execution_events()

    def position(self, **kwargs) -> GMOWebsocketChannels:
        return self.position_events()

    def orderbooks(self, symbol) -> GMOWebsocketChannels:
        return self.subscribe("orderbooks", symbol=symbol)

    def execution_events(self) -> GMOWebsocketChannels:
        return self.subscribe("executionEvents")

    def order_events(self) -> GMOWebsocketChannels:
        return self.subscribe("orderEvents")

    def position_events(self) -> GMOWebsocketChannels:
        return self.subscribe("positionEvents")

    def position_summary_events(self) -> GMOWebsocketChannels:
        return self.subscribe("positionSummaryEvents")
