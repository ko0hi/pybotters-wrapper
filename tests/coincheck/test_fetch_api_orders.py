import pandas as pd
import pytest
import pytest_mock


import pybotters_wrapper as pbw


@pytest.fixture
def tester(orders_fetch_api_tester):
    return orders_fetch_api_tester(
        symbol="btc_jpy",
        url="https://coincheck.com/api/exchange/orders/opens",
        factory_method=pbw.create_factory("coincheck").create_orders_fetch_api,
        dummy_response={
            "success": True,
            "orders": [
                {
                    "id": 202835,
                    "order_type": "buy",
                    "rate": 26890,
                    "pair": "btc_jpy",
                    "pending_amount": "0.5527",
                    "pending_market_buy_amount": None,
                    "stop_loss_rate": None,
                    "created_at": "2015-01-10T05:55:38.000Z",
                },
                {
                    "id": 202836,
                    "order_type": "sell",
                    "rate": 26990,
                    "pair": "btc_jpy",
                    "pending_amount": "0.77",
                    "pending_market_buy_amount": None,
                    "stop_loss_rate": None,
                    "created_at": "2015-01-10T05:55:38.000Z",
                },
                {
                    "id": 38632107,
                    "order_type": "buy",
                    "rate": None,
                    "pair": "btc_jpy",
                    "pending_amount": None,
                    "pending_market_buy_amount": "10000.0",
                    "stop_loss_rate": "50000.0",
                    "created_at": "2016-02-23T12:14:50.000Z",
                },
            ],
        },
        expected_generate_endpoint="/api/exchange/orders/opens",
        expected_translate_parameters={},
        expected_itemize_response=[
            {
                "id": "202835",
                "symbol": "btc_jpy",
                "side": "BUY",
                "price": 26890.0,
                "size": 0.5527,
                "type": "limit",
                "timestamp": pd.to_datetime("2015-01-10 05:55:38+0000"),
            },
            {
                "id": "202836",
                "symbol": "btc_jpy",
                "side": "SELL",
                "price": 26990.0,
                "size": 0.77,
                "type": "limit",
                "timestamp": pd.to_datetime("2015-01-10 05:55:38+0000"),
            },
            {
                "id": "38632107",
                "symbol": "btc_jpy",
                "side": "BUY",
                "price": 50000.0,
                "size": 10000.0,
                "type": "stop_market",
                "timestamp": pd.to_datetime("2016-02-23 12:14:50+0000"),
            },
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
