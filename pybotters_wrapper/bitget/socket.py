from __future__ import annotations

from pybotters_wrapper.common import WebsocketChannels


class BitgetWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.bitget.com/mix/v1/stream"

    def _make_endpoint_and_request_pair(
        self, channel: str, params: dict, inst_type: str = "mc", **kwargs
    ) -> [str, dict]:
        return self.ENDPOINT, {
            "op": "subscribe",
            "args": [{"channel": channel, "instType": inst_type, **params}],
        }

    def ticker(self, symbol: str, **kwargs) -> BitgetWebsocketChannels:
        return self._subscribe("ticker", {"instId": symbol})

    def trades(self, symbol, **kwargs) -> BitgetWebsocketChannels:
        return self._subscribe("trade", {"instId": symbol})

    def orderbook(self, symbol: str, **kwargs) -> BitgetWebsocketChannels:
        return self.books(symbol)

    def books(self, symbol: str) -> BitgetWebsocketChannels:
        return self._subscribe("books", {"instId": symbol})

    def candlesticks(
        self, symbol: str, interval: str = "1m"
    ) -> BitgetWebsocketChannels:
        assert interval == "1m", "only '1m' interval is supported"
        return self._subscribe(f"candle{interval}", {"instId": symbol})

    def account_inverse(self) -> BitgetWebsocketChannels:
        return self._subscribe("account", {"instId": "default"}, "DMCBL")

    def account_linear(self) -> BitgetWebsocketChannels:
        return self._subscribe("account", {"instId": "default"}, "UMCBL")

    def positions_inverse(self) -> BitgetWebsocketChannels:
        return self._subscribe("positions", {"instId": "default"}, "DMCBL")

    def positions_linear(self) -> BitgetWebsocketChannels:
        return self._subscribe("positions", {"instId": "default"}, "UMCBL")

    def orders_inverse(self) -> BitgetWebsocketChannels:
        return self._subscribe("orders", {"instId": "default"}, "DMCBL")

    def orders_linear(self) -> BitgetWebsocketChannels:
        return self._subscribe("orders", {"instId": "default"}, "UMCBL")
