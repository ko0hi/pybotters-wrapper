from pybotters_wrapper.common import API


class BinanceAPIBase(API):
    _ORDER_ENDPOINT = None

    async def market_order(
        self, symbol: str, side: str, size: float, **kwargs
    ) -> "OrderResponse":
        return await self._create_order_impl(
            self._ORDER_ENDPOINT,
            {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": "MARKET",
                "quantity": f"{size:.8f}",
            },
            "orderId",
            **kwargs
        )

    async def limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        **kwargs,
    ) -> "OrderResponse":
        return await self._create_order_impl(
            self._ORDER_ENDPOINT,
            {
                "symbol": symbol.upper(),
                "side": side.upper(),
                "type": "LIMIT",
                "quantity": f"{size:.8f}",
                "price": f"{price:.8f}",
                "timeInForce": "GTC",
            },
            "orderId",
            **kwargs
        )

    async def cancel_order(
        self, symbol: str, order_id: str, **kwargs
    ) -> "CancelResponse":
        return await self._cancel_order_impl(
            self._ORDER_ENDPOINT,
            {"symbol": symbol.upper(), "orderId": order_id},
            order_id,
            **kwargs
        )


class BinanceSpotAPI(BinanceAPIBase):
    BASE_URL = "https://api.binance.com"
    _ORDER_ENDPOINT = "/api/v3/order"


class BinanceUSDSMAPI(BinanceAPIBase):
    BASE_URL = "https://fapi.binance.com"
    _ORDER_ENDPOINT = "/fapi/v1/order"


class BinanceCOINMAPI(BinanceAPIBase):
    BASE_URL = "https://dapi.binance.com"
    _ORDER_ENDPOINT = "/dapi/v1/order"
