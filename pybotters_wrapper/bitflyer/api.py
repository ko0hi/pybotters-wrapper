from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import Side, RequsetMethod

from pybotters_wrapper.core import API
from pybotters_wrapper.utils.mixins import bitflyerMixin


class bitFlyerAPI(bitflyerMixin, API):
    BASE_URL = "https://api.bitflyer.com"
    _ORDER_ENDPOINT = "/v1/me/sendchildorder"
    _CANCEL_ENDPOINT = "/v1/me/cancelchildorder"
    _ORDER_ID_KEY = "child_order_acceptance_id"
    _CANCEL_REQUEST_METHOD = "POST"

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: Side, size: float
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
        side: Side,
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

    async def _make_cancel_request(
        self, endpoint: str, params_or_data=Optional[dict], **kwargs
    ):
        resp = await self.request("POST", endpoint, data=params_or_data, **kwargs)
        return resp, None
