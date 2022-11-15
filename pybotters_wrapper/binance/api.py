from pybotters_wrapper.common import API


class BinanceSpotAPI(API):
    BASE_URL = "https://api.binance.com"

    _ORDER_ENDPOINT = "/api/v3/order"

    async def market_order(
        self, symbol: str, side: str, size: float, *, params: dict = None, **kwargs
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
            params,
        )

    async def limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        *,
        params: dict = None,
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
            params,
        )

    async def cancel_order(
        self, symbol: str, order_id: str, *, params: dict = None, **kwargs
    ) -> "CancelResponse":
        return await self._cancel_order_impl(
            self._ORDER_ENDPOINT,
            {"symbol": symbol.upper(), "orderId": order_id},
            order_id,
            params,
        )
