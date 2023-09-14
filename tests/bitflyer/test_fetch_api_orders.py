import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(orders_fetch_api_tester):
    return orders_fetch_api_tester(
        symbol="FX_BTC_JPY",
        url="https://api.bitflyer.com/v1/me/getchildorders?product_code=FX_BTC_JPY&child_order_state=ACTIVE",
        factory_method=pbw.create_factory("bitflyer").create_orders_fetch_api,
        dummy_response=[
            {
                "id": 0,
                "child_order_id": "JFX20230612-131109-881677F",
                "product_code": "FX_BTC_JPY",
                "side": "SELL",
                "child_order_type": "LIMIT",
                "price": 5000000.0,
                "average_price": 0.0,
                "size": 0.01,
                "child_order_state": "ACTIVE",
                "expire_date": "2023-07-12T13:11:09",
                "child_order_date": "2023-06-12T13:11:09",
                "child_order_acceptance_id": "JRF20230612-131109-089984",
                "outstanding_size": 0.01,
                "cancel_size": 0.0,
                "executed_size": 0.0,
                "total_commission": 0.0,
                "time_in_force": "GTC",
            },
            {
                "id": 0,
                "child_order_id": "JFX20230612-130028-746901F",
                "product_code": "FX_BTC_JPY",
                "side": "BUY",
                "child_order_type": "LIMIT",
                "price": 3000000.0,
                "average_price": 0.0,
                "size": 0.01,
                "child_order_state": "ACTIVE",
                "expire_date": "2023-07-12T13:00:28",
                "child_order_date": "2023-06-12T13:00:28",
                "child_order_acceptance_id": "JRF20230612-130028-097351",
                "outstanding_size": 0.01,
                "cancel_size": 0.0,
                "executed_size": 0.0,
                "total_commission": 0.0,
                "time_in_force": "GTC",
            },
        ],
        expected_generate_endpoint="/v1/me/getchildorders",
        expected_translate_parameters={
            "product_code": "FX_BTC_JPY",
            "child_order_state": "ACTIVE",
        },
        expected_itemize_response=[
            {
                "id": "JRF20230612-131109-089984",
                "price": 5000000.0,
                "side": "SELL",
                "size": 0.01,
                "symbol": "FX_BTC_JPY",
                "type": "LIMIT",
            },
            {
                "id": "JRF20230612-130028-097351",
                "price": 3000000.0,
                "side": "BUY",
                "size": 0.01,
                "symbol": "FX_BTC_JPY",
                "type": "LIMIT",
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
