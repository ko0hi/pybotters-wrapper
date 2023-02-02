from __future__ import annotations

from pybotters_wrapper.core.api import API, OrderResponse
from pybotters_wrapper.utils.mixins import GMOCoinMixin


class GMOCoinAPI(GMOCoinMixin, API):
    BASE_URL = "https://api.coin.z.com"
    _ORDER_ENDPOINT = "/private/v1/order"
    _CANCEL_ENDPOINT = "/private/v1/cancelOrder"
    _CANCEL_REQUEST_METHOD = "POST"
    _ORDER_ID_KEY = "data"

    # close引数をsignatureに追加
    async def market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        close: bool = False,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        return await super().market_order(
            symbol, side, size, request_params, order_id_key, close=close
        )

    async def limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        close: bool = False,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        return await super().limit_order(
            symbol, side, price, size, request_params, order_id_key, close=close
        )

    async def close_order(
        self,
        symbol: str,
        side: str,
        size: float,
        position_id: int,
        execution_type: str,
        *,
        time_in_force: str = "FAK",
        price: float = None,
        cancel_before: bool = False,
    ):
        params = {
            "symbol": symbol,
            "side": side,
            "executionType": execution_type,
            "settlePosition": [{"positionId": position_id, "size": size}],
            "timeInForce": time_in_force,
            "cancelBefore": cancel_before,
        }

        if execution_type == "LIMIT":
            params["price"] = price

        return await self.post("/private/v1/closeOrder", data=params)

    async def close_market_order(
        self,
        symbol: str,
        side: str,
        size: float,
        position_id: int,
        time_in_force: str = "FAK",
        cancel_before: bool = False,
    ):
        return await self.close_order(
            symbol,
            side,
            size,
            position_id,
            "MARKET",
            time_in_force=time_in_force,
            cancel_before=cancel_before,
        )

    async def close_limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        position_id: int,
        time_in_force: str = "FAS",
        cancel_before: bool = False,
    ):
        return await self.close_order(
            symbol,
            side,
            size,
            position_id,
            "LIMIT",
            price=price,
            time_in_force=time_in_force,
            cancel_before=cancel_before,
        )

    def _make_order_endpoint(self, close: bool = False) -> str:
        return "/private/v1/closeBulkOrder" if close else self._ORDER_ENDPOINT

    def _make_market_endpoint(
        self, symbol: str, side: str, size: float, close: bool = False
    ) -> str:
        return self._make_order_endpoint(close)

    def _make_limit_endpoint(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        close: bool = False,
        **kwargs,
    ) -> str:
        return self._make_order_endpoint(close)

    def _make_market_order_parameter(
        self, endpoint: str, symbol: str, side: str, size: float
    ) -> dict:
        return {
            "symbol": symbol,
            "side": side,
            "executionType": "MARKET",
            "size": self.format_size(symbol, size),
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
            "symbol": symbol,
            "side": side,
            "executionType": "LIMIT",
            "price": self.format_price(symbol, price),
            "size": self.format_size(symbol, size),
        }

    def _make_stop_market_order_parameter(
        self,
        endpoint: str,
        symbol: str,
        side: str,
        size: float,
        trigger: float,
    ) -> dict:
        return {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "executionType": "STOP",
            "size": self.format_size(symbol, size),
            "price": self.format_price(symbol, trigger),
            "timeInForce": "FAK",  # FAS:約定しなかった注文を残す, FOK:全約定しないと全キャンセル
        }

    def _make_cancel_order_parameter(
        self, endpoint: str, symbol: str, order_id: str
    ) -> dict:
        return {"orderId": order_id}

    async def stop_limit_order(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        trigger: float,
        request_params: dict = None,
        order_id_key: str = None,
        **kwargs,
    ) -> "OrderResponse":
        raise RuntimeError(
            "stop_limit_order is not supported for gmocoin officially."
        )