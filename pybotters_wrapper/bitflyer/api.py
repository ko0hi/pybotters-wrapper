from pybotters_wrapper.common import API


class BitflyerAPI(API):
    BASE_URL = "https://api.bitflyer.com"

    async def market_order(self, symbol, side, size, **kwargs):
        res = await self.post(
            "/v1/me/sendchildorder",
            data={
                "product_code": symbol,
                "side": side,
                "size": f"{size:.8f}",
                "child_order_type": "MARKET",
            },
        )

        data = await res.json()

        if res.status != 200:
            raise RuntimeError(f"Invalid request: {data}")
        else:
            return data["child_order_acceptance_id"]

    async def limit_order(
        self, symbol, side, size, price, time_in_force="GTC", **kwargs
    ):
        res = await self.post(
            f"{self.BASE_URL}/v1/me/sendchildorder",
            data={
                "product_code": symbol,
                "side": side,
                "size": f"{size:.8f}",
                "child_order_type": "LIMIT",
                "price": int(price),
                "time_in_force": time_in_force,
            },
        )

        data = await res.json()

        if res.status != 200:
            raise RuntimeError(f"Invalid request: {data}", res)
        else:
            return data["child_order_acceptance_id"]

    async def cancel_order(self, symbol, order_id, **kwargs):
        order_id_key = "child_order_id"
        if order_id.startswith("JRF"):
            order_id_key = order_id_key.replace("_id", "_acceptance_id")

        res = await self.post(
            "/v1/me/cancelchildorder",
            data={"product_code": symbol, order_id_key: order_id},
        )
        return res.status == 200
