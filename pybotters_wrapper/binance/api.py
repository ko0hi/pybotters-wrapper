from pybotters_wrapper.common import API


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
            "quantity": f"{size:.8f}",
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
            "quantity": f"{size:.8f}",
            "price": f"{price:.8f}",
            "timeInForce": "GTC",
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"symbol": symbol.upper(), "orderId": order_id}


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
