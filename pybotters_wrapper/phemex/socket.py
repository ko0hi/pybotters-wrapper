from __future__ import annotations

import time
from pybotters_wrapper.core import WebsocketChannels


class PhemexWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://phemex.com/ws"

    def subscribe(self, channel: str, *args, **kwargs) -> PhemexWebsocketChannels:
        return super().subscribe(channel, *args, **kwargs)

    def make_subscribe_request(self, channel: str, *args, **kwargs) -> dict:
        return {
            "id": int(time.monotonic() * 10**9),
            "method": f"{channel}.subscribe",
            "params": list(args),
        }


    def ticker(self, symbol: str, **kwargs) -> PhemexWebsocketChannels:
        if symbol.endswith("USD") and not symbol.startswith("."):
            # https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-tick-event-for-symbol-price
            symbol = "." + symbol.replace("USD", "")

        return self.tick(symbol)

    def trades(self, symbol, **kwargs) -> PhemexWebsocketChannels:
        return self.subscribe("trade", symbol)

    def orderbook(self, symbol: str, **kwargs) -> PhemexWebsocketChannels:
        return self.subscribe("orderbook", symbol, True)

    def tick(self, symbol) -> PhemexWebsocketChannels:
        return self.subscribe("tick", symbol)

    def trade(self, symbol) -> PhemexWebsocketChannels:
        return self.subscribe("trade", symbol)
