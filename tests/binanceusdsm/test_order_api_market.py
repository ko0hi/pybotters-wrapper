import pytest
import pytest_mock

from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory


@pytest.fixture
def patch_price_size_precision_fetcher(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.binance.price_size_precision_fetcher.BinancePriceSizePrecisionFetcher.fetch_precisions",
        return_value={"price": {"BTCUSDT": 1}, "size": {"BTCUSDT": 3}},
    )


@pytest.fixture
def tester(market_order_tester):
    return market_order_tester(
        url="https://fapi.binance.com/fapi/v1/order",
        request_method="POST",
        factory_method=BinanceUSDSMWrapperFactory.create_market_order_api,
        dummy_order_parameters={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "size": 0.01,
            "extra_params": {},
        },
        dummy_response={
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
        },
        expected_generate_endpoint="/fapi/v1/order",
        expected_translate_parameters={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "type": "MARKET",
            "quantity": 0.01,
        },
        expected_order_id="139634730353",
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
