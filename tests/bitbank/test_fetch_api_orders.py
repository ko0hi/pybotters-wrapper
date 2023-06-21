import pandas as pd
import pytest
import pytest_mock


import pybotters_wrapper as pbw


@pytest.fixture
def tester(orders_fetch_api_tester):
    return orders_fetch_api_tester(
        symbol="btc_jpy",
        url="https://api.bitbank.cc/v1/user/spot/active_orders?pair=btc_jpy",
        factory_method=pbw.create_factory("bitbank").create_orders_fetch_api,
        dummy_response={
            "success": 1,
            "data": {
                "orders": [
                    {
                        "order_id": 29477746443,
                        "pair": "btc_jpy",
                        "side": "sell",
                        "type": "limit",
                        "start_amount": "0.0010",
                        "remaining_amount": "0.0010",
                        "executed_amount": "0.0000",
                        "price": "5000000",
                        "average_price": "0",
                        "ordered_at": 1687321937240,
                        "status": "UNFILLED",
                        "expire_at": 1702873937240,
                        "post_only": True,
                    },
                    {
                        "order_id": 29477738286,
                        "pair": "btc_jpy",
                        "side": "buy",
                        "type": "limit",
                        "start_amount": "0.0001",
                        "remaining_amount": "0.0001",
                        "executed_amount": "0.0000",
                        "price": "30000",
                        "average_price": "0",
                        "ordered_at": 1687321888552,
                        "status": "UNFILLED",
                        "expire_at": 1702873888552,
                        "post_only": True,
                    },
                ]
            },
        },
        expected_generate_endpoint="/user/spot/active_orders",
        expected_translate_parameters={"pair": "btc_jpy"},
        expected_itemize_response=[
            {
                "symbol": "btc_jpy",
                "id": "29477746443",
                "price": 5000000.0,
                "side": "SELL",
                "type": "limit",
                "size": 0.0010,
                "timestamp": pd.to_datetime(1687321937240, unit="ms", utc=True),
            },
            {
                "symbol": "btc_jpy",
                "id": "29477738286",
                "price": 30000.0,
                "side": "BUY",
                "type": "limit",
                "size": 0.0001,
                "timestamp": pd.to_datetime(1687321888552, unit="ms", utc=True),
            }
        ],
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_fetch(tester):
    resp, data = await tester.test_fetch()
    print(data)


@pytest.mark.asyncio
@pytest.mark.skip
async def test_api(tester):
    resp = await tester.test_api()
    print(resp)


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
