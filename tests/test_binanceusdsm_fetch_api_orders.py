import pytest
import pytest_mock

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_fetch_orders_api,
)


@pytest.fixture
def tester(orders_fetch_api_tester):
    dummy_responses = [
        {
            "orderId": 26799019660,
            "symbol": "ETHBUSD",
            "status": "NEW",
            "clientOrderId": "VKokEwY33pRhGbs4CnFEb9",
            "price": "1978.02",
            "avgPrice": "0",
            "origQty": "0.330",
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": "SELL",
            "positionSide": "BOTH",
            "stopPrice": "1980",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "time": 1681382301047,
            "updateTime": 1681382301047,
        },
        {
            "orderId": 26807427868,
            "symbol": "ETHBUSD",
            "status": "NEW",
            "clientOrderId": "FBY2slHY1PPE04f40o6zmd",
            "price": "1988.01",
            "avgPrice": "0",
            "origQty": "0.330",
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": "SELL",
            "positionSide": "BOTH",
            "stopPrice": "1990",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "time": 1681388511335,
            "updateTime": 1681388511335,
        },
    ]

    return orders_fetch_api_tester(
        url="https://fapi.binance.com/fapi/v1/openOrders?symbol=ETHBUSD",
        symbol="ETHBUSD",
        factory_method=create_binanceusdsm_fetch_orders_api,
        dummy_response=dummy_responses,
        expected_generate_endpoint="/fapi/v1/openOrders",
        expected_translate_parameters={"symbol": "ETHBUSD"},
        expected_itemize_response=[
            {
                "id": "26799019660",
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1978.02,
                "size": 0.33,
                "type": "STOP",
                "info": dummy_responses[0],
            },
            {
                "id": "26807427868",
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1988.01,
                "size": 0.33,
                "type": "STOP",
                "info": dummy_responses[1],
            },
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
