from __future__ import annotations

from pybotters_wrapper.common import API
from pybotters_wrapper.utils.mixins import BybitInverseMixin, BybitUSDTMixin


class BybitAPI(API):
    BASE_URL = "https://api.bybit.com"
    _ORDER_ID_KEY = "result.order_id"
    _CANCEL_REQUEST_METHOD = "POST"

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: str, size: float
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side.capitalize(),
            "order_type": "Market",
            "qty": self.format_size(symbol, size),
            "time_in_force": "GoodTillCancel",
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
            "side": side.capitalize(),
            "order_type": "Limit",
            "price": self.format_price(symbol, price),
            "qty": self.format_size(symbol, size),
            "time_in_force": "GoodTillCancel",
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"symbol": symbol, "order_id": order_id}


class BybitUSDTAPI(BybitUSDTMixin, BybitAPI):
    _ORDER_ENDPOINT = "/private/linear/order/create"
    _CANCEL_ENDPOINT = "/private/linear/order/cancel"


class BybitInverseAPI(BybitInverseMixin, BybitAPI):
    _ORDER_ENDPOINT = "/v2/private/order/create"
    _CANCEL_ENDPOINT = "/v2/private/order/cancel"
