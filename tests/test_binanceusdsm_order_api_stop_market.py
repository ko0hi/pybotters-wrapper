import pytest
import pytest_mock
from aioresponses import aioresponses

from conftest import MockAsyncResponse
from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_stop_market_order_api,
)
from pybotters_wrapper.core.api_order_stop_market import StopMarketOrderAPI


class TestOrderApiStopLimitBinanceUSDSM:
    URL = "https://fapi.binance.com/fapi/v1/order"
    SYMBOL = "BTCUSDT"
    SIDE = "BUY"
    SIZE = 0.01
    TRIGGER = 40000
    DUMMY_RESPONSE = {
        "orderId": 139845524717,
        "symbol": "BTCUSDT",
        "status": "NEW",
        "clientOrderId": "KVMxIQlwV3cZtN901DDKEg",
        "price": "0",
        "avgPrice": "0.00000",
        "origQty": "0.010",
        "executedQty": "0",
        "cumQty": "0",
        "cumQuote": "0",
        "timeInForce": "GTC",
        "type": "STOP_MARKET",
        "reduceOnly": False,
        "closePosition": False,
        "side": "BUY",
        "positionSide": "BOTH",
        "stopPrice": "40000",
        "workingType": "CONTRACT_PRICE",
        "priceProtect": False,
        "origType": "STOP_MARKET",
        "updateTime": 1681376713489,
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

        async with create_client() as client:
            api = create_binanceusdsm_stop_market_order_api(client, verbose=True)

            actual = api._generate_endpoint(
                {
                    "symbol": self.SYMBOL,
                    "side": self.SIDE,
                    "size": self.SIZE,
                    "trigger": self.TRIGGER,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self, patch_price_size_precision_fetcher):
        expected = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "STOP_MARKET",
            "quantity": 0.01,
            "stopPrice": 40000,
        }

        async with create_client() as client:
            api = create_binanceusdsm_stop_market_order_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/order",
                    "symbol": self.SYMBOL,
                    "side": self.SIDE,
                    "size": self.SIZE,
                    "trigger": self.TRIGGER,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_extract_order_id(self, patch_price_size_precision_fetcher):
        expected = "139845524717"

        async with create_client() as client:
            api = create_binanceusdsm_stop_market_order_api(client, verbose=True)
            actual = api._extract_order_id(
                MockAsyncResponse(self.DUMMY_RESPONSE, 200), self.DUMMY_RESPONSE  # noqa
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(
        self, patch_price_size_precision_fetcher, mocker: pytest_mock.MockerFixture
    ):
        url = "https://fapi.binance.com/fapi/v1/order"
        spy_generate_endpoint = mocker.spy(StopMarketOrderAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(
            StopMarketOrderAPI, "_translate_parameters"
        )
        spy_wrap_response = mocker.spy(StopMarketOrderAPI, "_wrap_response")

        async with create_client() as client:
            api = create_binanceusdsm_stop_market_order_api(client, verbose=True)
            with aioresponses() as m:
                m.post(url, payload=self.DUMMY_RESPONSE)
                await api.stop_market_order(
                    self.SYMBOL, self.SIDE, self.SIZE, self.TRIGGER
                )

                assert spy_generate_endpoint.spy_return == "/fapi/v1/order"
                assert spy_translate_parameters.spy_return == {
                    "symbol": "BTCUSDT",
                    "side": "BUY",
                    "type": "STOP_MARKET",
                    "quantity": 0.01,
                    "stopPrice": 40000,
                }
                assert spy_wrap_response.spy_return.order_id == "139845524717"
