from __future__ import annotations

import time

from legacy.core import WebsocketChannels


class bitFlyerWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.lightstream.bitflyer.com/json-rpc"

    def subscribe(self, channel: str, *args, **kwargs) -> "TWebsocketChannels":
        return super().subscribe(channel)

    def make_subscribe_request(self, channel: str, *args, **kwargs) -> dict:
        return {
            "method": "subscribe",
            "params": {"channel": channel, "id": int(time.monotonic() * 10**9)},
        }

    # common channel methods
    def ticker(self, symbol, **kwargs) -> bitFlyerWebsocketChannels:
        return self.lightning_ticker(symbol)

    def orderbook(self, symbol, **kwargs) -> bitFlyerWebsocketChannels:
        self.lightning_board(symbol)
        self.lightning_board_snapshot(symbol)
        return self

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
        return self.subscribe(f"lightning_ticker_{symbol}")

    def lightning_board(self, symbol) -> bitFlyerWebsocketChannels:
        return self.subscribe(f"lightning_board_{symbol}")

    def lightning_board_snapshot(self, symbol) -> bitFlyerWebsocketChannels:
        return self.subscribe(f"lightning_board_snapshot_{symbol}")

    def lightning_executions(self, symbol) -> bitFlyerWebsocketChannels:
        return self.subscribe(f"lightning_executions_{symbol}")

    def child_order_events(self) -> bitFlyerWebsocketChannels:
        return self.subscribe("child_order_events")

    def parent_order_events(self) -> bitFlyerWebsocketChannels:
        return self.subscribe("parent_order_events")
