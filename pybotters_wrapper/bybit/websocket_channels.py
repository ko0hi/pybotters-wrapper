class BybitWebSocketChannelsMixin:
    # Override by subclass
    _PRIVATE_ENDPOINT = ""
    _PUBLIC_ENDPOINT = ""
    _ENDPOINT = ""
    _CATEGORY = ""

    def ticker(self, symbol: str, **kwargs) -> str:
        return f"tickers.{symbol}"

    def trades(self, symbol: str, **kwargs) -> str:
        return self.trade(symbol)

    def orderbook(self, symbol: str, **kwargs) -> str:
        return f"orderbook.200.{symbol}"

    def order(self, **kwargs) -> str:
        return f"order.{self._CATEGORY}"

    def execution(self, **kwargs) -> str:
        return f"execution.{self._CATEGORY}"

    def position(self, **kwargs) -> str:
        return f"position.{self._CATEGORY}"

    def trade(self, symbol: str) -> str:
        return f"publicTrade.{symbol}"

    def _get_endpoint(self, parameter: str) -> str:
        if parameter.startswith(("position", "execution", "order", "stop_order", "wallet")):
            return self._PRIVATE_ENDPOINT
        else:
            return self._PUBLIC_ENDPOINT

    def kline(self, symbol: str, interval: int | str = 1) -> str:
        return f"kline.{interval}.{symbol}"

    def liquidation(self, symbol: str) -> str:
        return f"liquidation.{symbol}"

    def _parameter_template(self, parameter: str) -> dict:
        return {"op": "subscribe", "args": parameter.split("|")}
