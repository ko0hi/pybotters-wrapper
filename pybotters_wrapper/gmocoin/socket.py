from __future__ import annotations

from pybotters_wrapper.common import WebsocketChannels


class GMOWebsocketChannels(WebsocketChannels):
    PUBLIC_ENDPOINT = "wss://api.coin.z.com/ws/public/v1"
    PRIVATE_ENDPOINT = "wss://api.coin.z.com/ws/private/v1"
    ENDPOINT = PUBLIC_ENDPOINT

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
        return self._subscribe("ticker", symbol=symbol)

    def trades(self, symbol, option="TAKER_ONLY", **kwargs) -> GMOWebsocketChannels:
        return self._subscribe("trades", symbol=symbol, option=option)

    def orderbook(self, symbol, **kwargs) -> GMOWebsocketChannels:
        return self.orderbooks(symbol)

    def orderbooks(self, symbol) -> GMOWebsocketChannels:
        return self._subscribe("orderbooks", symbol=symbol)

    def execution_events(self) -> GMOWebsocketChannels:
        return self._subscribe("executionEvents")

    def order_events(self) -> GMOWebsocketChannels:
        return self._subscribe("orderEvents")

    def position_events(self) -> GMOWebsocketChannels:
        return self._subscribe("positionEvents")

    def position_summary_events(self) -> GMOWebsocketChannels:
        return self._subscribe("positionSummaryEvents")
