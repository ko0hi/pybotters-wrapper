import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import create_binancecoinm_limit_order_api


@pytest.fixture
def patch_price_size_precision_fetcher(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.binance.common.price_size_precisions_fetcher_binance.BinancePriceSizePrecisionsFetcher.fetch_precisions",
        return_value={"price": {"BTCUSDT": 1}, "size": {"BTCUSDT": 0}},
    )


@pytest.fixture
def tester(limit_order_tester):
    return limit_order_tester(
        url="https://dapi.binance.com/dapi/v1/order",
        request_method="POST",
        factory_method=create_binancecoinm_limit_order_api,
        dummy_order_parameters={
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "price": 9300,
            "size": 1,
            "extra_params": {},
        },
        dummy_response={
            "orderId": 83055494779,
            "symbol": "BTCUSD_PERP",
            "pair": "BTCUSD",
            "status": "NEW",
            "clientOrderId": "OszK4e1FUulCao5bQdq2C3",
            "price": "9300",
            "avgPrice": "0.0",
            "origQty": "1",
            "executedQty": "0",
            "cumQty": "0",
            "cumBase": "0",
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
            "updateTime": 1681718315989,
        },
        expected_generate_endpoint="/dapi/v1/order",
        expected_translate_parameters={
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "type": "LIMIT",
            "price": 9300,
            "quantity": 1,
            "timeInForce": "GTC",
        },
        expected_order_id="83055494779",
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
