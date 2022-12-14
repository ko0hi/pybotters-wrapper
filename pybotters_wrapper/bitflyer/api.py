from __future__ import annotations

from pybotters_wrapper.core import API
from pybotters_wrapper.utils.mixins import bitflyerMixin


class bitFlyerAPI(bitflyerMixin, API):
    BASE_URL = "https://api.bitflyer.com"
    _ORDER_ENDPOINT = "/v1/me/sendchildorder"
    _CANCEL_ENDPOINT = "/v1/me/cancelchildorder"
    _ORDER_ID_KEY = "child_order_acceptance_id"
    _CANCEL_REQUEST_METHOD = "POST"

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: str, size: float
    ) -> dict:
        return {
            "product_code": symbol,
            "side": side,
            "size": self.format_size(symbol, size),
            "child_order_type": "MARKET",
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
            "product_code": symbol,
            "side": side,
            "size": self.format_size(symbol, size),
            "child_order_type": "LIMIT",
            "price": self.format_price(symbol, price),
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"product_code": symbol, "child_order_acceptance_id": order_id}

    async def _make_cancel_request(self, endpoint: str, data=dict, **kwargs):
        resp = await self.request(
            self._CANCEL_REQUEST_METHOD, endpoint, data=data, **kwargs
        )
        return resp, None
