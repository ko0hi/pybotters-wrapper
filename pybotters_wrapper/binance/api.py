from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import aiohttp

from pybotters_wrapper.core.api import FetchOrdersResponse

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import Side

from pybotters_wrapper.core import API
from pybotters_wrapper.core.store import OrderItem
from pybotters_wrapper.utils.mixins import (
    BinanceCOINMMixin,
    BinanceCOINMTESTMixin,
    BinanceSpotMixin,
    BinanceUSDSMMixin,
    BinanceUSDSMTESTMixin,
)


class BinanceAPIBase(API):
    _ORDER_ENDPOINT = None
    _ORDER_ID_KEY = "orderId"

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: Side, size: float
    ) -> dict:
        return {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": "MARKET",
            "quantity": self.format_size(symbol, size),
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
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": "LIMIT",
            "quantity": self.format_size(symbol, size),
            "price": self.format_price(symbol, price),
            "timeInForce": "GTC",
        }

    def _make_stop_market_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: Side,
        size: float,
        trigger: float,
    ) -> dict:
        return {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": "STOP_MARKET",
            "quantity": self.format_size(symbol, size),
            "stopPrice": self.format_price(symbol, trigger),
        }

    def _make_stop_limit_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: Side,
        price: float,
        size: float,
        trigger: float,
    ) -> dict:
        return {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": "STOP",
            "quantity": self.format_size(symbol, size),
            "price": self.format_price(symbol, price),
            "stopPrice": self.format_price(symbol, trigger),
            "timeInForce": "GTC",  # GTC以外を指定したい場合、kwargsで上書きする。
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"symbol": symbol.upper(), "orderId": order_id}

    def _make_fetch_orders_parameter(self, symbol: str) -> Optional[dict]:
        return {"symbol": symbol}

    def _make_fetch_orders_response(
        self, resp: aiohttp.ClientResponse, resp_data: list[dict]
    ) -> FetchOrdersResponse:
        orders = [
            OrderItem(
                id=str(i["orderId"]),
                symbol=i["symbol"],
                side=i["side"],
                price=float(i["price"]),
                size=float(i["origQty"]) - float(i["executedQty"]),
                type=i["type"],
                info=i  # noqa

            ) for i in resp_data
        ]
        return FetchOrdersResponse(orders, resp, resp_data)


class BinanceSpotAPI(BinanceSpotMixin, BinanceAPIBase):
    BASE_URL = "https://api.binance.com"
    _ORDER_ENDPOINT = "/api/v3/order"
    _FETCH_ORDERS_ENDPOINT = "/api/v3/openOrders"

    # binance spotのpublic endpointはauthを付与するとエラーとなる問題の対応
    # https://binance-docs.github.io/apidocs/spot/en/#market-data-endpoints を列挙
    _PUBLIC_ENDPOINTS = {
        f"/api/v3/{e}"
        for e in [
            "ping",
            "time",
            "exchangeInfo",
            "depth",
            "trades",
            "historicalTrades",
            "aggTrades",
            "klines",
            "uiKlines",
            "ticker/24hr",
            "ticker/price",
            "ticker/bookTicker",
            "ticker",
        ]
    }

    async def stop_market_order(
        self,
        symbol: str,
        side: Side,
        size: float,
        trigger: float,
        *,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        raise RuntimeError(
            "stop_market_order is not supported for binancespot officially."
        )

    def _make_stop_limit_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: Side,
        price: float,
        size: float,
        trigger: float,
    ) -> dict:
        params = super()._make_stop_limit_order_parameter(
            endpoint, symbol, side, price, size, trigger
        )
        params["type"] = "STOP_LOSS_LIMIT"
        return params


class BinanceUSDSMAPI(BinanceUSDSMMixin, BinanceAPIBase):
    BASE_URL = "https://fapi.binance.com"
    _ORDER_ENDPOINT = "/fapi/v1/order"
    _FETCH_ORDERS_ENDPOINT = "/fapi/v1/openOrders"


class BinanceUSDSMTESTAPI(BinanceUSDSMTESTMixin, BinanceAPIBase):
    BASE_URL = "https://testnet.binancefuture.com"
    _ORDER_ENDPOINT = "/fapi/v1/order"
    _FETCH_ORDERS_ENDPOINT = "/fapi/v1/openOrders"


class BinanceCOINMAPI(BinanceCOINMMixin, BinanceAPIBase):
    BASE_URL = "https://dapi.binance.com"
    _ORDER_ENDPOINT = "/dapi/v1/order"
    _FETCH_ORDERS_ENDPOINT = "/dapi/v1/openOrders"


class BinanceCOINMTESTAPI(BinanceCOINMTESTMixin, BinanceAPIBase):
    BASE_URL = "https://testnet.binancefuture.com"
    _ORDER_ENDPOINT = "/dapi/v1/order"
    _FETCH_ORDERS_ENDPOINT = "/dapi/v1/openOrders"
