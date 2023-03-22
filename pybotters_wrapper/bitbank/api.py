from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import Side

from pybotters_wrapper.core import API
from pybotters_wrapper.utils.mixins import bitbankMixin


class bitbankAPI(bitbankMixin, API):
    # https://github.com/bitbankinc/bitbank-api-docs/blob/master/rest-api_JP.md
    _PRIVATE_ENDPOINTS = {
        "/user/assets",
        "/user/spot/order",
        "/user/spot/cancel_order",
        "/user/spot/cancel_orders",
        "/user/spot/orders_info",
        "/user/spot/active_orders",
        "/user/spot/trade_history",
        "/user/withdrawal_account",
        "/user/request_withdrawal",
        "/spot/status",
        "/spot/pairs",
    }
    _ORDER_ENDPOINT = "/user/spot/order"
    _CANCEL_ENDPOINT = "/user/spot/cancel_order"
    _CANCEL_REQUEST_METHOD = "POST"
    _ORDER_ID_KEY = "data.order_id"

    def _get_base_url(self, url: str):
        if url is not None and url in self._PRIVATE_ENDPOINTS:
            return "https://api.bitbank.cc/v1"
        else:
            return "https://public.bitbank.cc"

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: Side, size: float
    ) -> dict:
        return {
            "pair": symbol,
            "side": side.lower(),
            "amount": size,
            "type": "market",
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
            "pair": symbol,
            "side": side.lower(),
            "amount": size,
            "price": price,
            "type": "limit",
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"pair": symbol, "order_id": order_id}
