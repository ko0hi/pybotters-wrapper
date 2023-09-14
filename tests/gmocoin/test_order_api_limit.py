import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(limit_order_tester):
    return limit_order_tester(
        url="https://api.coin.z.com/private/v1/order",
        request_method="POST",
        factory_method=pbw.create_factory("gmocoin").create_limit_order_api,
        dummy_order_parameters={
            "symbol": "BTC_JPY",
            "side": "BUY",
            "price": 2000000,
            "size": 0.01,
            "extra_params": {},
        },
        dummy_response={
            "status": 0,
            "data": "637000",
            "responsetime": "2019-03-19T02:15:06.108Z",
        },
        expected_generate_endpoint="/private/v1/order",
        expected_translate_parameters={
            "symbol": "BTC_JPY",
            "side": "BUY",
            "price": 2000000,
            "size": 0.01,
            "executionType": "LIMIT",
        },
        expected_order_id="637000",
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
