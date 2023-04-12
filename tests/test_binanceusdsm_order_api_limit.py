import pytest
import pytest_mock
from aioresponses import aioresponses
from conftest import MockAsyncResponse

import pybotters_wrapper as pbw
from pybotters_wrapper.core.api_order_limit import LimitOrderAPI


class TestOrderApiLimitBinanceUSDSM:
    URL = "https://fapi.binance.com/fapi/v1/order"
    SYMBOL = "BTCUSDT"
    SIDE = "BUY"
    PRICE = 20000
    SIZE = 0.01
    DUMMY_RESPONSE = {
        "orderId": 139634730353,
        "symbol": "BTCUSDT",
        "status": "NEW",
        "clientOrderId": "VHYUxzKJP0kNk6SLCFI7bQ",
        "price": "20000",
        "avgPrice": "0.00000",
        "origQty": "0.010",
        "executedQty": "0",
        "cumQty": "0",
        "cumQuote": "0",
        "timeInForce": "GTC",
        "type": "LIMIT",
        "reduceOnly": False,
        "closePosition": False,
        "side": "BUY",
        "positionSide": "BOTH",
        "stopPrice": "0",
        "workingType": "CONTRACT_PRICE",
        "priceProtect": False,
        "origType": "LIMIT",
        "updateTime": 1681314780371,
    }

    @pytest.fixture(scope="function")
    def patch_price_size_precision_fetcher(self, mocker: pytest_mock.MockerFixture):
        mocker.patch(
            "pybotters_wrapper.binance.common.price_size_precisions_fetcher_binance.BinancePriceSizePrecisionsFetcher.fetch_precisions",
            return_value={"price": {"BTCUSDT": 1}, "size": {"BTCUSDT": 3}},
        )

    @pytest.mark.asyncio
    async def test_generate_endpoint(self, patch_price_size_precision_fetcher):
        expected = "/fapi/v1/order"

        async with pbw.create_client() as client:
            api = pbw.create_binanceusdsm_limit_order_api(client, verbose=True)
            actual = api._generate_endpoint(
                {
                    "symbol": self.SYMBOL,
                    "side": self.SIDE,
                    "price": self.PRICE,
                    "size": self.SIZE,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self, patch_price_size_precision_fetcher):
        expected = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "price": 20000,
            "quantity": 0.01,
            "timeInForce": "GTC",
        }

        async with pbw.create_client() as client:
            api = pbw.create_binanceusdsm_limit_order_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/order",
                    "symbol": self.SYMBOL,
                    "side": self.SIDE,
                    "price": self.PRICE,
                    "size": self.SIZE,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_extract_order_id(self, patch_price_size_precision_fetcher):
        expected = "139634730353"

        async with pbw.create_client() as client:
            api = pbw.create_binanceusdsm_limit_order_api(client, verbose=True)
            actual = api._extract_order_id(
                MockAsyncResponse(self.DUMMY_RESPONSE, 200), self.DUMMY_RESPONSE  # noqa
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(
        self, patch_price_size_precision_fetcher, mocker: pytest_mock.MockerFixture
    ):
        url = "https://fapi.binance.com/fapi/v1/order"
        spy_generate_endpoint = mocker.spy(LimitOrderAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(LimitOrderAPI, "_translate_parameters")
        spy_wrap_response = mocker.spy(LimitOrderAPI, "_wrap_response")

        async with pbw.create_client() as client:
            api = pbw.create_binanceusdsm_limit_order_api(client, verbose=True)
            with aioresponses() as m:
                m.post(url, payload=self.DUMMY_RESPONSE)
                await api.limit_order(self.SYMBOL, self.SIDE, self.PRICE, self.SIZE)

                assert spy_generate_endpoint.spy_return == "/fapi/v1/order"
                assert spy_translate_parameters.spy_return == {
                    "symbol": "BTCUSDT",
                    "side": "BUY",
                    "type": "LIMIT",
                    "price": 20000,
                    "quantity": 0.01,
                    "timeInForce": "GTC",
                }
                assert spy_wrap_response.spy_return.order_id == "139634730353"
