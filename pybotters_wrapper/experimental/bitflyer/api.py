from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import aiohttp

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import Side

from pybotters_wrapper.core import API
from pybotters_wrapper.core.api import (
    FetchTickerResponse,
    FetchOrderbookResponse,
    FetchOrdersResponse,
    FetchPositionsResponse,
)
from pybotters_wrapper.core.store import (
    TickerItem,
    OrderbookItem,
    OrderItem,
    PositionItem,
)
from pybotters_wrapper.utils.mixins import bitflyerMixin


class bitFlyerAPI(bitflyerMixin, API):
    BASE_URL = "https://api.bitflyer.com"
    _ORDER_ENDPOINT = "/v1/me/sendchildorder"
    _CANCEL_ENDPOINT = "/v1/me/cancelchildorder"
    _FETCH_TICKER_ENDPOINT = "/v1/getticker"
    _FETCH_ORDERBOOK_ENDPOINT = "/v1/getboard"
    _FETCH_ORDERS_ENDPOINT = "/v1/me/getchildorders"
    _FETCH_POSITIONS_ENDPOINT = "/v1/me/getpositions"
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
    ) -> tuple["aiohttp.ClientResponse", None]:
        resp = await self.request("POST", endpoint, data=params_or_data, **kwargs)
        return resp, None

    def _make_fetch_ticker_parameter(self, symbol: str) -> dict:
        return {"product_code": symbol}

    def _make_fetch_orderbook_parameter(self, symbol: str) -> dict:
        return {"product_code": symbol}

    def _make_fetch_orders_parameter(self, symbol: str) -> dict:
        return {"product_code": symbol, "child_order_state": "ACTIVE"}

    def _make_fetch_positions_parameter(self, symbol: str) -> dict:
        return {"product_code": symbol}

    def _make_fetch_ticker_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict
    ) -> FetchTickerResponse:
        return FetchTickerResponse(
            TickerItem(
                symbol=resp_data["product_code"],
                price=resp_data["ltp"],
                info=resp_data,  # noqa
            ),
            resp,
            resp_data,
        )

    def _make_fetch_orderbook_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict
    ) -> FetchOrderbookResponse:
        symbol = resp.request_info.url.query["product_code"]
        asks = [
            OrderbookItem(symbol=symbol, side="SELL", price=i["price"], size=i["size"])
            for i in resp_data["asks"]
        ]
        bids = [
            OrderbookItem(symbol=symbol, side="BUY", price=i["price"], size=i["size"])
            for i in resp_data["bids"]
        ]
        return FetchOrderbookResponse({"SELL": asks, "BUY": bids}, resp, resp_data)

    def _make_fetch_orders_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict
    ) -> FetchOrdersResponse:
        orders = [
            OrderItem(
                id=i["child_order_acceptance_id"],
                symbol=i["product_code"],
                side=i["side"],
                price=i["price"],
                size=i["size"],
                type=i["child_order_type"],
                info=i,  # noqa
            )
            for i in resp_data
        ]
        return FetchOrdersResponse(orders, resp, resp_data)

    def _make_fetch_positions_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict
    ) -> FetchPositionsResponse:
        positions = [
            PositionItem(
                symbol=i["product_code"],
                side=i["side"],
                price=i["price"],
                size=i["size"],
                info=i,  # noqa
            )
            for i in resp_data
        ]
        return FetchPositionsResponse(positions, resp, resp_data)
