from __future__ import annotations

from pybotters_wrapper.core import WebsocketChannels


class PhemexWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://phemex.com/ws"
    N = 0

    def _make_endpoint_and_request_pair(self, channel, *args, **kwargs) -> [str, dict]:
        params = {
            "id": self.N,
            "method": f"{channel}.subscribe",
            "params": list(args),
        }
        self.N += 1
        return self.ENDPOINT, params

    def ticker(self, symbol: str, **kwargs) -> PhemexWebsocketChannels:
        if symbol.endswith("USD") and not symbol.startswith("."):
            # https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md#subscribe-tick-event-for-symbol-price
            symbol = "." + symbol.replace("USD", "")

        return self.tick(symbol)

    def trades(self, symbol, **kwargs) -> PhemexWebsocketChannels:
        return self._subscribe("trade", symbol)

    def orderbook(self, symbol: str, **kwargs) -> PhemexWebsocketChannels:
        return self._subscribe("orderbook", symbol, True)

    def tick(self, symbol) -> PhemexWebsocketChannels:
        return self._subscribe("tick", symbol)

    def trade(self, symbol) -> PhemexWebsocketChannels:
        return self._subscribe("trade", symbol)
