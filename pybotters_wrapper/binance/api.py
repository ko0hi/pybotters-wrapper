from pybotters_wrapper.common import API
from .resources import (
    SPOT_PRICE_PRECISIONS,
    SPOT_SIZE_PRECISIONS,
    USDSM_PRICE_PRECISIONS,
    USDSM_SIZE_PRECISIONS,
    COINM_PRICE_PRECISIONS,
    COINM_SIZE_PRECISIONS,
)


class BinanceAPIBase(API):
    _ORDER_ENDPOINT = None
    _ORDER_ID_KEY = "orderId"

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: str, size: float
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
        side: str,
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

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"symbol": symbol.upper(), "orderId": order_id}

    def format_precision(self, value: float, precision: int):
        str_value = f"{value:.10f}"
        return str_value[: -(10 - precision)]

    def format_price(self, symbol: str, price: float):
        return self.format_precision(price, self._get_price_precision(symbol))

    def format_size(self, symbol: str, size: float):
        return self.format_precision(size, self._get_size_precision(symbol))

    def _get_price_precision(self, symbol: str):
        if isinstance(self, BinanceSpotAPI):
            return SPOT_PRICE_PRECISIONS[symbol]
        elif isinstance(self, BinanceUSDSMAPI):
            return USDSM_PRICE_PRECISIONS[symbol]
        elif isinstance(self, COINM_PRICE_PRECISIONS):
            return COINM_PRICE_PRECISIONS[symbol]

    def _get_size_precision(self, symbol: str):
        if isinstance(self, BinanceSpotAPI):
            return SPOT_SIZE_PRECISIONS[symbol]
        elif isinstance(self, BinanceUSDSMAPI):
            return USDSM_SIZE_PRECISIONS[symbol]
        elif isinstance(self, COINM_PRICE_PRECISIONS):
            return COINM_SIZE_PRECISIONS[symbol]


class BinanceSpotAPI(BinanceAPIBase):
    BASE_URL = "https://api.binance.com"
    _ORDER_ENDPOINT = "/api/v3/order"

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


class BinanceUSDSMAPI(BinanceAPIBase):
    BASE_URL = "https://fapi.binance.com"
    _ORDER_ENDPOINT = "/fapi/v1/order"


class BinanceCOINMAPI(BinanceAPIBase):
    BASE_URL = "https://dapi.binance.com"
    _ORDER_ENDPOINT = "/dapi/v1/order"
