import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(cancel_order_tester):
    return cancel_order_tester(
        url="https://api.coin.z.com/private/v1/cancelOrder",
        request_method="POST",
        factory_method=pbw.create_factory("gmocoin").create_cancel_order_api,
        dummy_order_parameters={
            "symbol": "BTC_JPY",
            "order_id": "0",
            "extra_params": {},
        },
        dummy_response={"status": 0, "responsetime": "2019-03-19T01:07:24.557Z"},
        expected_generate_endpoint="/private/v1/cancelOrder",
        expected_translate_parameters={
            "orderId": 0
        },
        expected_order_id="0",
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
@pytest.mark.skip(reason="GMOCoin API does not return order id for canceling order")
async def test_extract_order_id(tester):
    await tester.test_extract_order_id()


@pytest.mark.asyncio
async def test_combined(tester, mocker: pytest_mock.MockerFixture):
    await tester.test_combined(mocker)
