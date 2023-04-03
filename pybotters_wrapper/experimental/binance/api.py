from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import aiohttp
import requests
from yarl import URL

if TYPE_CHECKING:
    from pybotters_wrapper._typedefs import Side, RequsetMethod

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

    def _make_fetch_ticker_parameter(self, symbol: str) -> dict:
        return {"symbol": symbol}

    def _make_fetch_orderbook_parameter(self, symbol: str) -> dict:
        return {"symbol": symbol}

    def _make_fetch_ticker_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict
    ) -> FetchTickerResponse:
        return FetchTickerResponse(
            TickerItem(
                symbol=resp_data["symbol"],
                price=float(resp_data["price"]),
                info=resp_data,  # noqa
            ),
            resp,
            resp_data,
        )

    def _make_fetch_orderbook_response(
        self, resp: aiohttp.ClientResponse, resp_data: dict
    ) -> "FetchOrderbookResponse":
        symbol = resp.request_info.url.query["symbol"]
        asks = [
            OrderbookItem(
                symbol=symbol, side="SELL", price=float(i[0]), size=float(i[1])
            )
            for i in resp_data["asks"]
        ]
        bids = [
            OrderbookItem(
                symbol=symbol, side="BUY", price=float(i[0]), size=float(i[1])
            )
            for i in resp_data["bids"]
        ]
        return FetchOrderbookResponse({"SELL": asks, "BUY": bids}, resp, resp_data)


class BinanceSpotAPI(BinanceSpotMixin, BinanceAPIBase):
    BASE_URL = "https://api.binance.com"
    _ORDER_ENDPOINT = "/api/v3/order"
    _FETCH_TICKER_ENDPOINT = "/api/v3/ticker/price"
    _FETCH_ORDERBOOK_ENDPOINT = "/api/v3/depth"
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

    async def request(
        self,
        method: RequsetMethod,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        if URL(url).path in self._PUBLIC_ENDPOINTS:
            kwargs["auth"] = None
        return await super().request(method, url, params=params, data=data, **kwargs)

    def srequest(
        self,
        method: RequsetMethod,
        url: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        if URL(url).path in self._PUBLIC_ENDPOINTS:
            kwargs["auth"] = None
        return super().srequest(method, url, params=params, data=data, **kwargs)

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


class BinanceUSDSMAPIBase(BinanceAPIBase):
    _ORDER_ENDPOINT = "/fapi/v1/order"
    _FETCH_TICKER_ENDPOINT = "/fapi/v1/ticker/price"
    _FETCH_ORDERBOOK_ENDPOINT = "/fapi/v1/depth"
    _FETCH_ORDERS_ENDPOINT = "/fapi/v1/openOrders"
    _FETCH_POSITIONS_ENDPOINT = "/fapi/v2/positionRisk"

    def _make_fetch_orders_parameter(self, symbol: str) -> dict:
        return {"symbol": symbol}

    def _make_fetch_positions_parameter(self, symbol: str) -> dict:
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
                info=i,  # noqa
            )
            for i in resp_data
        ]
        return FetchOrdersResponse(orders, resp, resp_data)

    def _make_fetch_positions_response(
        self, resp: aiohttp.ClientResponse, resp_data: list[dict]
    ) -> "FetchPositionsResponse":
        positions = [
            PositionItem(
                symbol=i["symbol"],
                side=("BUY" if float(i["positionAmt"]) > 0 else "SELL"),
                price=float(i["entryPrice"]),
                size=float(i["positionAmt"]),
                info=i,  # noqa
            )
            for i in resp_data
        ]
        return FetchPositionsResponse(positions, resp, resp_data)


class BinanceUSDSMAPI(BinanceUSDSMMixin, BinanceUSDSMAPIBase):
    BASE_URL = "https://fapi.binance.com"


class BinanceUSDSMTESTAPI(BinanceUSDSMTESTMixin, BinanceUSDSMAPI):
    BASE_URL = "https://testnet.binancefuture.com"


class BinanceCOINMAPIBase(BinanceAPIBase):
    _ORDER_ENDPOINT = "/dapi/v1/order"
    _FETCH_TICKER_ENDPOINT = "/dapi/v1/ticker/price"
    _FETCH_ORDERBOOK_ENDPOINT = "/dapi/v1/depth"
    _FETCH_ORDERS_ENDPOINT = "/dapi/v1/openOrders"
    _FETCH_POSITIONS_ENDPOINT = "/dapi/v1/positionRisk"

    def _make_fetch_orders_parameter(self, symbol: str) -> dict:
        return {"symbol": symbol}

    def _make_fetch_positions_parameter(self, symbol: str) -> dict:
        # coinmはsymbol（e.g., BNBUSD_PERP）の指定ができないので、パラメーターにこっそり忍ばせておく。
        # 一応これでも認証は通ったが、通らなくなった場合どうするかは別途考える。
        return {"pair": symbol.split("_")[0], "__symbol": symbol}

    def _make_fetch_ticker_response(
        self, resp: aiohttp.ClientResponse, resp_data: list[dict]
    ) -> FetchTickerResponse:
        # なぜかcoinmだけsymbol指定してもlistで返ってくる
        return super()._make_fetch_ticker_response(resp, resp_data[0])

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
                info=i,  # noqa
            )
            for i in resp_data
        ]
        return FetchOrdersResponse(orders, resp, resp_data)

    def _make_fetch_positions_response(
        self, resp: aiohttp.ClientResponse, resp_data: list[dict]
    ) -> "FetchPositionsResponse":
        # 忍ばせておいたsymbolを使って取得したいsymbolのポジション情報に絞る。
        symbol = resp.request_info.url.query["__symbol"]
        positions = [
            PositionItem(
                symbol=i["symbol"],
                side=("BUY" if float(i["positionAmt"]) > 0 else "SELL"),
                price=float(i["entryPrice"]),
                size=float(i["positionAmt"]),
                info=i,  # noqa
            )
            for i in resp_data
            if i["symbol"] == symbol
        ]
        return FetchPositionsResponse(positions, resp, resp_data)


class BinanceCOINMAPI(BinanceCOINMMixin, BinanceCOINMAPIBase):
    BASE_URL = "https://dapi.binance.com"


class BinanceCOINMTESTAPI(BinanceCOINMTESTMixin, BinanceCOINMAPIBase):
    BASE_URL = "https://testnet.binancefuture.com"
