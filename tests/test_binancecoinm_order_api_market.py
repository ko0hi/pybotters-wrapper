import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import create_binancecoinm_market_order_api


@pytest.fixture
def patch_price_size_precision_fetcher(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.binance.common.price_size_precisions_fetcher_binance.BinancePriceSizePrecisionsFetcher.fetch_precisions",
        return_value={"price": {"BNBUSD_230929": 2}, "size": {"BNBUSD_230929": 0}},
    )


@pytest.fixture
def tester(market_order_tester):
    return market_order_tester(
        url="https://dapi.binance.com/dapi/v1/order",
        request_method="POST",
        factory_method=create_binancecoinm_market_order_api,
        dummy_order_parameters={
            "symbol": "BNBUSD_230929",
            "side": "SELL",
            "size": 1,
            "extra_params": {},
        },
        dummy_response={
            "orderId": 14784080,
            "symbol": "BNBUSD_230929",
            "pair": "BNBUSD",
            "status": "NEW",
            "clientOrderId": "RC5b3D1qpzVX1yibUONTKE",
            "price": "0",
            "avgPrice": "0.000",
            "origQty": "1",
            "executedQty": "0",
            "cumQty": "0",
            "cumBase": "0",
            "timeInForce": "GTC",
            "type": "MARKET",
            "reduceOnly": False,
            "closePosition": False,
            "side": "SELL",
            "positionSide": "BOTH",
            "stopPrice": "0",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "MARKET",
            "updateTime": 1681719797538,
        },
        expected_generate_endpoint="/dapi/v1/order",
        expected_translate_parameters={
            "symbol": "BNBUSD_230929",
            "side": "SELL",
            "type": "MARKET",
            "quantity": 1,
        },
        expected_order_id="14784080",
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_order(tester, patch_price_size_precision_fetcher):
    resp = await tester.test_order()
    print(resp)


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
