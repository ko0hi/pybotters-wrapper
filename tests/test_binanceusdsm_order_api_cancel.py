import pytest
import pytest_mock

from pybotters_wrapper.binance.binanceusdsm import create_binanceusdsm_cancel_order_api


@pytest.fixture
def patch_price_size_precision_fetcher(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.binance.common.price_size_precisions_fetcher_binance.BinancePriceSizePrecisionsFetcher.fetch_precisions",
        return_value={"price": {"BTCUSDT": 1}, "size": {"BTCUSDT": 3}},
    )


@pytest.fixture
def tester(cancel_order_tester):
    return cancel_order_tester(
        url="https://fapi.binance.com/fapi/v1/order",
        request_method="DELETE",
        factory_method=create_binanceusdsm_cancel_order_api,
        dummy_order_parameters={
            "symbol": "BTCUSDT",
            "order_id": "283194212",
            "extra_params": {}
        },
        dummy_response={
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
        },
        expected_generate_endpoint="/fapi/v1/order",
        expected_translate_parameters={
            "symbol": "BTCUSDT",
            "orderId": "283194212",
        },
        expected_order_id="283194212",
    )


@pytest.mark.asyncio
async def test_generate_endpoint(tester, patch_price_size_precision_fetcher):
    await tester.test_generate_endpoint()


@pytest.mark.asyncio
async def test_translate_parameters(tester, patch_price_size_precision_fetcher):
    await tester.test_translate_parameters()


@pytest.mark.asyncio
async def test_extract_order_id(tester, patch_price_size_precision_fetcher):
    await tester.test_extract_order_id()


@pytest.mark.asyncio
async def test_combined(
    tester, patch_price_size_precision_fetcher, mocker: pytest_mock.MockerFixture
):
    await tester.test_combined(mocker)
