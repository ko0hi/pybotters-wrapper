from pybotters_wrapper.common import WebsocketChannels


class BybitUSDTWebsocketChannels(WebsocketChannels):
    ENDPOINT = "wss://stream.bybit.com/realtime_public"

    def _make_endpoint_and_request_pair(self, *args):
        reequest = {"op": "subscribe", "args": list(args)}
        return self.ENDPOINT, reequest

    def ticker(self, symbol: str, **kwargs):
        return self.instrument(symbol, **kwargs)

    def trades(self, symbol: str, **kwargs):
        return self._subscribe(f"trade.{symbol}")

    def orderbook(self, symbol: str, **kwargs):
        return self._subscribe(f"orderBook_200.100ms.{symbol}")


    def instrument(self, symbol: str, **kwargs):
        return self._subscribe(f"instrument_info.100ms.{symbol}")
