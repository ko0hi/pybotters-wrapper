class BybitWebSocketChannelsMixin:
    def ticker(self, symbol: str, **kwargs) -> str:
        return self.instrument_info(symbol)

    def trades(self, symbol: str, **kwargs) -> str:
        return self.trade(symbol)

    def orderbook(self, symbol: str, **kwargs) -> str:
        return self.orderbook_l2_200(symbol, 100)

    def order(self, **kwargs) -> str:
        return "order|stop_order"

    def execution(self, **kwargs) -> str:
        return "execution"

    def position(self, **kwargs) -> str:
        return "position"

    def trade(self, symbol: str) -> str:
        return f"trade.{symbol}"

    def instrument_info(self, symbol: str) -> str:
        return f"instrument_info.100ms.{symbol}"

    def orderbook_l2_200(self, symbol: str, n: int) -> str:
        return f"orderBook_200.{n}ms.{symbol}"

    def stop_order(self) -> str:
        return "stop_order"

    def wallet(self) -> str:
        return "wallet"

    def _parameter_template(self, parameter: str) -> dict:
        return {"op": "subscribe", "args": parameter.split("|")}
