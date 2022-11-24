from __future__ import annotations

import uuid

import pybotters

from pybotters_wrapper.common import API


class KuCoinAPIBase(API):
    _ORDER_ENDPOINT = "/api/v1/orders"
    _ORDER_ID_KEY = "data.orderId"

    def _make_cancel_endpoint(self, symbol: str, order_id: str, **kwargs):
        return super()._make_cancel_endpoint(symbol, order_id,
                                             **kwargs) + f"/{order_id}"

    def _make_cancel_order_parameter(
            self, endpoint: str, symbol: str, order_id: str
    ) -> None:
        return None


class KuCoinSpotAPI(KuCoinAPIBase):
    BASE_URL = "https://api.kucoin.com"

    def _make_market_order_parameter(
            self, endpoint: str, symbol: str, side: str, size: float
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side.lower(),
            "type": "market",
            "clientOid": str(uuid.uuid4()),
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
            "side": side.lower(),
            "type": "limit",
            "price": price,
            "size": f"{size:.8f}",
            "clientOid": str(uuid.uuid4()),
        }


class KuCoinFuturesAPI(KuCoinAPIBase):
    BASE_URL = "https://api-futures.kucoin.com"

    def __init__(self, client: pybotters.Client, leverage=1, **kwargs):
        super(KuCoinFuturesAPI, self).__init__(client, **kwargs)
        self._leverage = leverage

    def _make_market_order_parameter(
            self, endpoint: str, symbol: str, side: str, size: float
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side.lower(),
            "type": "market",
            "clientOid": str(uuid.uuid4()),
            "leverage": self._leverage,
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
            "side": side.lower(),
            "type": "limit",
            "price": price,
            "size": f"{size:.0f}",
            "clientOid": str(uuid.uuid4()),
            "leverage": self._leverage,
        }
