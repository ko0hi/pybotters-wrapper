from __future__ import annotations

from pybotters_wrapper.common.api import API, OrderResponse
from pybotters_wrapper.utils.mixins import GMOCoinMixin


class GMOCoinAPI(GMOCoinMixin, API):
    BASE_URL = "https://api.coin.z.com"
    _ORDER_ENDPOINT = "/private/v1/order"
    _CANCEL_ENDPOINT = "/private/v1/cancelOrder"
    _CANCEL_REQUEST_METHOD = "POST"
    _ORDER_ID_KEY = "data"

    # close引数をsignatureに追加
    def market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        close: bool = False,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        return super().market_order(
            symbol, side, size, request_params, order_id_key, close=close
        )

    def limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        close: bool = False,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        return super().limit_order(
            symbol, side, price, size, request_params, order_id_key, close=close
        )

    def _make_order_endpoint(self, close: bool = False) -> str:
        return "/private/v1/closeBulkOrder" if close else self._ORDER_ENDPOINT

    def _make_market_endpoint(
        self, symbol: str, side: str, size: float, close: bool = False
    ) -> str:
        return self._make_order_endpoint(close)

    def _make_limit_endpoint(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        close: bool = False,
        **kwargs,
    ) -> str:
        return self._make_order_endpoint(close)

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: str, size: float
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side,
            "executionType": "MARKET",
            "size": self.format_price(symbol, size),
        }

    def _make_limit_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: str,
        price: float,
        size: float,
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side,
            "executionType": "LIMIT",
            "price": self.format_price(symbol, price),
            "size": self.format_price(symbol, size),
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"orderId": order_id}
