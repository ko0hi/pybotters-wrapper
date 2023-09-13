import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(market_order_tester):
    return market_order_tester(
        url="https://coincheck.com/api/exchange/orders",
        request_method="POST",
        factory_method=pbw.create_factory("coincheck").create_market_order_api,
        dummy_order_parameters={
            "symbol": "btc_jpy",
            "side": "BUY",
            "size": 5000,
            "extra_params": {},
        },
        dummy_response={
            "success": True,
            "id": 12345,
            "rate": "2000000",
            "amount": "0.01",
            "order_type": "buy",
            "time_in_force": "good_til_cancelled",
            "stop_loss_rate": None,
            "pair": "btc_jpy",
            "created_at": "2015-01-10T05:55:38.000Z",
        },
        expected_generate_endpoint="/api/exchange/orders",
        expected_translate_parameters={
            "pair": "btc_jpy",
            "order_type": "market_buy",
            "market_buy_amount": 5000,
        },
        expected_order_id="12345",
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_order(tester):
    resp = await tester.test_order()
    print(resp)


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
async def test_extract_order_id(tester):
    await tester.test_extract_order_id()


@pytest.mark.asyncio
async def test_combined(tester, mocker: pytest_mock.MockerFixture):
    await tester.test_combined(mocker)
