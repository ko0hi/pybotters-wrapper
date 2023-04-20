import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def tester(orders_fetch_api_tester):
    return orders_fetch_api_tester(
        symbol="BTCUSD_PERP",
        url="https://dapi.binance.com/dapi/v1/openOrders?symbol=BTCUSD_PERP",
        factory_method=BinanceCOINMWrapperFactory.create_fetch_orders_api,
        dummy_response=[
            {
                "orderId": 83013837647,
                "symbol": "BTCUSD_PERP",
                "pair": "BTCUSD",
                "status": "NEW",
                "clientOrderId": "android_7i3K2RMWeIleJWdWzZC8",
                "price": "3000",
                "avgPrice": "0",
                "origQty": "1",
                "executedQty": "0",
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
                "time": 1681658972938,
                "updateTime": 1681658972938,
            }
        ],
        expected_generate_endpoint="/dapi/v1/openOrders",
        expected_translate_parameters={"symbol": "BTCUSD_PERP"},
        expected_itemize_response=[
            {
                "id": "83013837647",
                "symbol": "BTCUSD_PERP",
                "side": "BUY",
                "price": 3000.0,
                "size": 1.0,
                "type": "LIMIT",
                "info": {
                    "orderId": 83013837647,
                    "symbol": "BTCUSD_PERP",
                    "pair": "BTCUSD",
                    "status": "NEW",
                    "clientOrderId": "android_7i3K2RMWeIleJWdWzZC8",
                    "price": "3000",
                    "avgPrice": "0",
                    "origQty": "1",
                    "executedQty": "0",
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
                    "time": 1681658972938,
                    "updateTime": 1681658972938,
                },
            }
        ],
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_fetch(tester):
    resp, data = await tester.test_fetch()
    print(data)


@pytest.mark.asyncio
async def test_generate_endpoint(tester):
    await tester.test_generate_endpoint()


@pytest.mark.asyncio
async def test_translate_parameters(tester):
    await tester.test_translate_parameters()


@pytest.mark.asyncio
async def test_itemize_response(tester):
    await tester.test_itemize_response()


@pytest.mark.asyncio
async def test_combined(tester, mocker: pytest_mock.MockerFixture):
    await tester.test_combined(mocker)
