from pybotters_wrapper.common import API


class FTXAPI(API):
    BASE_URL = "https://ftx.com"
    _ORDER_ENDPOINT = "/api/orders"

    async def market_order(
        self, symbol: str, side: str, size: float, params: dict = None, **kwargs
    ):
        params = params or {}
        data = {
            "market": symbol,
            "side": side.lower(),
            "type": "market",
            "size": size,
            **params,
        }
        return await self._new_order(self._ORDER_ENDPOINT, data=data, id_key="result.id")

    async def limit_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: float,
        params: dict = None,
        **kwargs,
    ):
        params = params or {}
        data = {
            "market": symbol,
            "side": side.lower(),
            "type": "limit",
            "size": size,
            "price": price,
            **params,
        }
        return await self._new_order(self._ORDER_ENDPOINT, data=data, id_key="result.id")

    async def cancel_order(self, order_id: str, **kwargs):
        endpoint = self._ORDER_ENDPOINT + f"/{order_id}"
        return await self._cancel_order_impl(endpoint, None, order_id, **kwargs)
