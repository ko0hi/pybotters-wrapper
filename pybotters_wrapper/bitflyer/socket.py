import uuid

from pybotters_wrapper.common import WebsocketChannels


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
    def ticker(self, symbol, **kwargs):
        return self._subscribe(f"lightning_ticker_{symbol}")

    def orderbook(self, symbol, **kwargs):
        return [self.board(symbol), self.board_snapshot(symbol)]

    def trades(self, symbol, **kwargs):
        return self.executions(symbol)

    # exchange channel methods
    def board(self, symbol):
        return self._subscribe(f"lightning_board_{symbol}")

    def board_snapshot(self, symbol):
        return self._subscribe(f"lightning_board_snapshot_{symbol}")

    def executions(self, symbol):
        return self._subscribe(f"lightning_executions_{symbol}")

    def child_order(self):
        return self._subscribe("child_order_events")

    def parent_order(self):
        return self._subscribe("parent_order_envets")

    def public(self, symbol):
        return [
            self.ticker(symbol),
            self.board(symbol),
            self.board_snapshot(symbol),
            self.executions(symbol),
        ]

    def private_channels(self):
        return [self.child_order(), self.parent_order()]

    def all_channels(self, symbol):
        return self.public(symbol) + self.private()
