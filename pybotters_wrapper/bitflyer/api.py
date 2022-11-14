from pybotters_wrapper.common import API


class BitflyerAPI(API):
    BASE_URL = "https://api.bitflyer.com"

    async def market_order(
        self, symbol: str, side: str, size: float, *, params: dict = None, **kwargs
    ) -> "OrderResponse":
        return await self._new_order(
            "/v1/me/sendchildorder",
            {
                "product_code": symbol,
                "side": side,
                "size": f"{size:.8f}",
                "child_order_type": "MARKET",
            },
            "child_order_acceptance_id",
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
        return await self._new_order(
            "/v1/me/sendchildorder",
            {
                "product_code": symbol,
                "side": side,
                "size": f"{size:.8f}",
                "child_order_type": "LIMIT",
                "price": int(price),
            },
            "child_order_acceptance_id",
            params,
        )

    async def cancel_order(
        self, symbol: str, order_id: str, *, params: dict = None, **kwargs
    ) -> "CancelResponse":
        return await self._cancel_order_impl(
            "/v1/me/cancelchildorder",
            {"product_code": symbol, "child_order_acceptance_id": order_id},
            order_id,
            params,
            "POST",
        )

    async def _to_response_data_cancel(self, resp: "aiohttp.ClientResponse") -> None:
        return None
