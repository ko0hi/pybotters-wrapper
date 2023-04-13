import pytest
import pytest_mock
from aioresponses import aioresponses
from conftest import MockAsyncResponse

from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binanceusdsm import create_binanceusdsm_cancel_order_api
from pybotters_wrapper.core.api_order_cancel import CancelOrderAPI


class TestOrderApiLimitBinanceUSDSM:
    URL = "https://fapi.binance.com/fapi/v1/order"
    SYMBOL = "BTCUSDT"
    ORDER_ID = "283194212"
    DUMMY_RESPONSE = {
        "clientOrderId": "myOrder1",
        "cumQty": "0",
        "cumQuote": "0",
        "executedQty": "0",
        "orderId": 283194212,
        "origQty": "11",
        "origType": "TRAILING_STOP_MARKET",
        "price": "0",
        "reduceOnly": False,
        "side": "BUY",
        "positionSide": "SHORT",
        "status": "CANCELED",
        "stopPrice": "9300",
        "closePosition": False,
        "symbol": "BTCUSDT",
        "timeInForce": "GTC",
        "type": "TRAILING_STOP_MARKET",
        "activatePrice": "9020",
        "priceRate": "0.3",
        "updateTime": 1571110484038,
        "workingType": "CONTRACT_PRICE",
        "priceProtect": False,
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
            api = create_binanceusdsm_cancel_order_api(client, verbose=True)
            actual = api._generate_endpoint(
                {"symbol": self.SYMBOL, "order_id": self.ORDER_ID, "extra_params": {}}
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_translate_parameters(self, patch_price_size_precision_fetcher):
        expected = {
            "symbol": "BTCUSDT",
            "orderId": self.ORDER_ID,
        }

        async with create_client() as client:
            api = create_binanceusdsm_cancel_order_api(client, verbose=True)
            actual = api._translate_parameters(
                {
                    "endpoint": "/fapi/v1/order",
                    "symbol": self.SYMBOL,
                    "order_id": self.ORDER_ID,
                    "extra_params": {},
                }
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_extract_order_id(self, patch_price_size_precision_fetcher):
        expected = "283194212"

        async with create_client() as client:
            api = create_binanceusdsm_cancel_order_api(client, verbose=True)
            actual = api._extract_order_id(
                MockAsyncResponse(self.DUMMY_RESPONSE, 200), self.DUMMY_RESPONSE  # noqa
            )

            assert actual == expected

    @pytest.mark.asyncio
    async def test_combined(
        self, patch_price_size_precision_fetcher, mocker: pytest_mock.MockerFixture
    ):
        url = "https://fapi.binance.com/fapi/v1/order"
        spy_generate_endpoint = mocker.spy(CancelOrderAPI, "_generate_endpoint")
        spy_translate_parameters = mocker.spy(CancelOrderAPI, "_translate_parameters")
        spy_wrap_response = mocker.spy(CancelOrderAPI, "_wrap_response")

        async with create_client() as client:
            api = create_binanceusdsm_cancel_order_api(client, verbose=True)
            with aioresponses() as m:
                m.delete(url, payload=self.DUMMY_RESPONSE)
                await api.cancel_order(self.SYMBOL, self.ORDER_ID)

                assert spy_generate_endpoint.spy_return == "/fapi/v1/order"
                assert spy_translate_parameters.spy_return == {
                    "symbol": self.SYMBOL,
                    "orderId": self.ORDER_ID,
                }
                assert spy_wrap_response.spy_return.order_id == "283194212"
