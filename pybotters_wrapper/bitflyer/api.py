from pybotters_wrapper.common import API


class bitFlyerAPI(API):
    BASE_URL = "https://api.bitflyer.com"

    async def market_order(
        self, symbol: str, side: str, size: float, **kwargs
    ) -> "OrderResponse":
        return await self._create_order_impl(
            "/v1/me/sendchildorder",
            {
                "product_code": symbol,
                "side": side,
                "size": f"{size:.8f}",
                "child_order_type": "MARKET",
            },
            "child_order_acceptance_id",
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
            "/v1/me/sendchildorder",
            {
                "product_code": symbol,
                "side": side,
                "size": f"{size:.8f}",
                "child_order_type": "LIMIT",
                "price": int(price),
            },
            "child_order_acceptance_id",
            **kwargs
        )

    async def cancel_order(
        self, symbol: str, order_id: str, **kwargs
    ) -> "CancelResponse":
        return await self._cancel_order_impl(
            "/v1/me/cancelchildorder",
            {"product_code": symbol, "child_order_acceptance_id": order_id},
            order_id,
            "POST",
            **kwargs
        )

    async def _to_response_data_cancel(self, resp: "aiohttp.ClientResponse") -> None:
        return None
