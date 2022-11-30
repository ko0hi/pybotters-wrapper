from __future__ import annotations

import uuid

from pybotters_wrapper.core import WebsocketChannels


class bitFlyerWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.lightstream.bitflyer.com/json-rpc"

    def _make_endpoint_and_request_pair(self, channel, **kwargs) -> dict:
        params = {
            "method": "subscribe",
            "params": {"channel": channel, "id": str(uuid.uuid4())},
        }
        params.update(kwargs)
        return self.ENDPOINT, params

    # common channel methods
    def ticker(self, symbol, **kwargs) -> bitFlyerWebsocketChannels:
        return self.lightning_ticker(symbol)

    def orderbook(self, symbol, **kwargs) -> bitFlyerWebsocketChannels:
        return [self.lightning_board(symbol), self.lightning_board_snapshot(symbol)]

    def trades(self, symbol, **kwargs) -> bitFlyerWebsocketChannels:
        return self.lightning_executions(symbol)

    def order(self, **kwargs) -> bitFlyerWebsocketChannels:
        return self.child_order_events()

    def execution(self, **kwargs) -> bitFlyerWebsocketChannels:
        return self.child_order_events()

    def position(self, **kwargs) -> bitFlyerWebsocketChannels:
        return self.child_order_events()

    # exchange channel methods
    def lightning_ticker(self, symbol: str) -> bitFlyerWebsocketChannels:
        return self._subscribe(f"lightning_ticker_{symbol}")

    def lightning_board(self, symbol) -> bitFlyerWebsocketChannels:
        return self._subscribe(f"lightning_board_{symbol}")

    def lightning_board_snapshot(self, symbol) -> bitFlyerWebsocketChannels:
        return self._subscribe(f"lightning_board_snapshot_{symbol}")

    def lightning_executions(self, symbol) -> bitFlyerWebsocketChannels:
        return self._subscribe(f"lightning_executions_{symbol}")

    def child_order_events(self) -> bitFlyerWebsocketChannels:
        return self._subscribe("child_order_events")

    def parent_order_events(self) -> bitFlyerWebsocketChannels:
        return self._subscribe("parent_order_events")
