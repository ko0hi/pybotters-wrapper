from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import Side

import uuid

import pybotters
from legacy.core import API
from pybotters_wrapper.utils.mixins import KuCoinFuturesMixin, KuCoinSpotMixin


class KuCoinAPIBase(API):
    _ORDER_ENDPOINT = "/api/v1/orders"
    _ORDER_ID_KEY = "data.orderId"

    def _make_cancel_endpoint(self, symbol: str, order_id: str, **kwargs) -> str:
        return (
            super()._make_cancel_endpoint(symbol, order_id, **kwargs) + f"/{order_id}"
        )

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> None:
        return None


class KuCoinSpotAPI(KuCoinSpotMixin, KuCoinAPIBase):
    BASE_URL = "https://api.kucoin.com"

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: Side, size: float
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side.lower(),
            "size": self.format_size(symbol, size),
            "type": "market",
            "clientOid": str(uuid.uuid4()),
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
            "side": side.lower(),
            "type": "limit",
            "price": self.format_price(symbol, price),
            "size": self.format_size(symbol, size),
            "clientOid": str(uuid.uuid4()),
        }


class KuCoinFuturesAPI(KuCoinFuturesMixin, KuCoinAPIBase):
    BASE_URL = "https://api-futures.kucoin.com"

    def __init__(self, client: pybotters.Client, leverage=1, **kwargs):
        super(KuCoinFuturesAPI, self).__init__(client, **kwargs)
        self._leverage = leverage

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: Side, size: float
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side.lower(),
            "size": self.format_size(symbol, size),
            "type": "market",
            "clientOid": str(uuid.uuid4()),
            "leverage": self._leverage,
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
            "side": side.lower(),
            "type": "limit",
            "price": self.format_price(symbol, price),
            "size": self.format_size(symbol, size),
            "clientOid": str(uuid.uuid4()),
            "leverage": self._leverage,
        }
