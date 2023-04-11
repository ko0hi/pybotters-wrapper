from __future__ import annotations

from legacy.core import WebsocketChannels


class BitgetWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://ws.bitget.com/mix/v1/stream"

    def subscribe(self, channel: str, *args, **kwargs) -> dict:
        return super().subscribe(channel, *args, **kwargs)

    def make_subscribe_request(self, channel: str, *args, **kwargs) -> dict:
        kwargs["instType"] = kwargs.get("instType", "mc")
        return {"op": "subscribe", "args": [{"channel": channel, **kwargs}]}

    def ticker(self, symbol: str, **kwargs) -> BitgetWebsocketChannels:
        return self.subscribe("ticker", instId=symbol)

    def trades(self, symbol, **kwargs) -> BitgetWebsocketChannels:
        return self.subscribe("trade", instId=symbol)

    def orderbook(self, symbol: str, **kwargs) -> BitgetWebsocketChannels:
        return self.books(symbol)

    def books(self, symbol: str) -> BitgetWebsocketChannels:
        return self.subscribe("books", instId=symbol)

    def candlesticks(
        self, symbol: str, interval: str = "1m"
    ) -> BitgetWebsocketChannels:
        assert interval == "1m", "only '1m' interval is supported"
        return self.subscribe(f"candle{interval}", instId=symbol)

    def account_inverse(self) -> BitgetWebsocketChannels:
        return self.subscribe("account", instId="default", instType="DMCBL")

    def account_linear(self) -> BitgetWebsocketChannels:
        return self.subscribe("account", instId="default", instType="UMCBL")

    def positions_inverse(self) -> BitgetWebsocketChannels:
        return self.subscribe("positions", instId="default", instType="UMCBL")

    def positions_linear(self) -> BitgetWebsocketChannels:
        return self.subscribe("positions", instId="default", instType="UMCBL")

    def orders_inverse(self) -> BitgetWebsocketChannels:
        return self.subscribe("orders", instId="default", instType="UMCBL")

    def orders_linear(self) -> BitgetWebsocketChannels:
        return self.subscribe("orders", instId="default", instType="UMCBL")
