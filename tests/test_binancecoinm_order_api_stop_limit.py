import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def patch_price_size_precision_fetcher(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.binance.common.price_size_precisions_fetcher_binance.BinancePriceSizePrecisionsFetcher.fetch_precisions",
        return_value={"price": {"BTCUSDT": 1}, "size": {"BTCUSDT": 0}},
    )


@pytest.fixture
def tester(stop_limit_order_tester):
    return stop_limit_order_tester(
        url="https://dapi.binance.com/dapi/v1/order",
        request_method="POST",
        factory_method=BinanceCOINMWrapperFactory.create_stop_limit_order_api,
        dummy_order_parameters={
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "price": 9300,
            "size": 1,
            "trigger": 40000,
            "extra_params": {},
        },
        dummy_response={
            "orderId": 83056659328,
            "symbol": "BTCUSD_PERP",
            "pair": "BTCUSD",
            "status": "NEW",
            "clientOrderId": "IbUOOJnU65IjeeQDPwBMjB",
            "price": "9300",
            "avgPrice": "0.0",
            "origQty": "1",
            "executedQty": "0",
            "cumQty": "0",
            "cumBase": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": "BUY",
            "positionSide": "BOTH",
            "stopPrice": "40000",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "updateTime": 1681720070356,
        },
        expected_generate_endpoint="/dapi/v1/order",
        expected_translate_parameters={
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "type": "STOP",
            "price": 9300,
            "quantity": 1,
            "stopPrice": 40000,
            "timeInForce": "GTC",
        },
        expected_order_id="83056659328",
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
async def test_combined(tester, mocker: pytest_mock.MockerFixture):
    await tester.test_combined(mocker)
