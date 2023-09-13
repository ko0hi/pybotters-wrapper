import time
from typing import Literal

from ..core import WebSocketChannels


class bitFlyerWebsocketChannels(
    WebSocketChannels[
        Literal[
            "lightning_ticker",
            "lightning_board",
            "lightning_board_snapshot",
            "lightning_executions",
            "child_order_events",
            "parent_order_events",
        ],
        str,
        dict,
    ]
):
    _ENDPOINT = "wss://ws.lightstream.bitflyer.com/json-rpc"

    def ticker(self, symbol: str, **kwargs) -> str:
        return self.lightning_ticker(symbol)

    def orderbook(self, symbol: str, **kwargs) -> list[str]:  # type: ignore
        return [self.lightning_board(symbol), self.lightning_board_snapshot(symbol)]

    def trades(self, symbol: str, **kwargs) -> str:
        return self.lightning_executions(symbol)

    def order(self, **kwargs) -> str:
        return self.child_order_events()

    def execution(self, **kwargs) -> str:
        return self.child_order_events()

    def position(self, **kwargs) -> str:
        return self.child_order_events()

    def lightning_ticker(self, symbol: str) -> str:
        return f"lightning_ticker_{symbol}"

    def lightning_board(self, symbol: str) -> str:
        return f"lightning_board_{symbol}"

    def lightning_board_snapshot(self, symbol: str) -> str:
        return f"lightning_board_snapshot_{symbol}"

    def lightning_executions(self, symbol: str) -> str:
        return f"lightning_executions_{symbol}"

    def child_order_events(self) -> str:
        return "child_order_events"

    def parent_order_events(self) -> str:
        return "parent_order_events"

    def _parameter_template(self, parameter: str) -> dict:
        return {
            "method": "subscribe",
            "params": {"channel": parameter, "id": int(time.monotonic() * 10**9)},
        }
