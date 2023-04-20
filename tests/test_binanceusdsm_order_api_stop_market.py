import pytest
import pytest_mock

from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory


@pytest.fixture
def patch_price_size_precision_fetcher(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.binance.common.price_size_precisions_fetcher_binance.BinancePriceSizePrecisionsFetcher.fetch_precisions",
        return_value={"price": {"BTCUSDT": 1}, "size": {"BTCUSDT": 3}},
    )


@pytest.fixture
def tester(stop_market_order_tester):
    return stop_market_order_tester(
        url="https://fapi.binance.com/fapi/v1/order",
        request_method="POST",
        factory_method=BinanceUSDSMWrapperFactory.create_stop_market_order_api,
        dummy_order_parameters={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "size": 0.01,
            "trigger": 40000,
            "extra_params": {},
        },
        dummy_response={
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
        },
        expected_generate_endpoint="/fapi/v1/order",
        expected_translate_parameters={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "STOP_MARKET",
            "quantity": 0.01,
            "stopPrice": 40000,
        },
        expected_order_id="139845524717",
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
