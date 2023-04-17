import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import create_binancecoinm_cancel_order_api


@pytest.fixture
def tester(cancel_order_tester):
    return cancel_order_tester(
        url="https://dapi.binance.com/dapi/v1/order",
        request_method="DELETE",
        factory_method=create_binancecoinm_cancel_order_api,
        dummy_order_parameters={
            "symbol": "BTCUSD_PERP",
            "order_id": "83055510190",
            "extra_params": {},
        },
        dummy_response={
            "orderId": 83055510190,
            "symbol": "BTCUSD_PERP",
            "pair": "BTCUSD",
            "status": "CANCELED",
            "clientOrderId": "GqtkK8zCBhW6zU0jKqn1vV",
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
            "updateTime": 1681718419425,
        },
        expected_generate_endpoint="/dapi/v1/order",
        expected_translate_parameters={
            "symbol": "BTCUSD_PERP",
            "orderId": "83055510190",
        },
        expected_order_id="83055510190",
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_order(tester):
    resp = await tester.test_order()
    print(resp)


@pytest.mark.asyncio
async def test_generate_endpoint(tester):
    await tester.test_generate_endpoint()


@pytest.mark.asyncio
async def test_translate_parameters(tester):
    await tester.test_translate_parameters()


@pytest.mark.asyncio
async def test_extract_order_id(tester):
    await tester.test_extract_order_id()


@pytest.mark.asyncio
async def test_combined(tester, mocker: pytest_mock.MockerFixture):
    await tester.test_combined(mocker)
