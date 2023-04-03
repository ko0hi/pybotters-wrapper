from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import Side

import pybotters

from pybotters_wrapper.core import API
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
            "reduce_only": False,
            "close_on_trigger": False,
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
            "symbol": symbol,
            "side": side.capitalize(),
            "order_type": "Limit",
            "price": self.format_price(symbol, price),
            "qty": self.format_size(symbol, size),
            "time_in_force": "GoodTillCancel",
            "reduce_only": False,
            "close_on_trigger": False,
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"symbol": symbol, "order_id": order_id}


class BybitUSDTAPI(BybitUSDTMixin, BybitAPI):
    _ORDER_ENDPOINT = "/private/linear/order/create"
    _CANCEL_ENDPOINT = "/private/linear/order/cancel"

    def __init__(
        self, client: pybotters.Client, verbose: bool = False, oneway=True, **kwargs
    ):
        super(BybitUSDTAPI, self).__init__(client, verbose, **kwargs)
        self._oneway = oneway

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: Side, size: float
    ) -> dict:
        return self._add_position_idx(
            super()._make_market_order_parameter(endpoint, symbol, side, size)
        )

    def _make_limit_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: Side,
        price: float,
        size: float,
    ) -> dict:
        return self._add_position_idx(
            super()._make_limit_order_parameter(endpoint, symbol, side, price, size)
        )

    def _add_position_idx(self, p):
        if self._oneway:
            p["position_idx"] = 0
        return p


class BybitInverseAPI(BybitInverseMixin, BybitAPI):
    _ORDER_ENDPOINT = "/v2/private/order/create"
    _CANCEL_ENDPOINT = "/v2/private/order/cancel"

