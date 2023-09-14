import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(limit_order_tester):
    return limit_order_tester(
        url="https://api.bitflyer.com/v1/me/sendchildorder",
        request_method="POST",
        factory_method=pbw.create_factory("bitflyer").create_limit_order_api,
        dummy_order_parameters={
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "price": 2000000,
            "size": 0.01,
            "extra_params": {},
        },
        dummy_response={"child_order_acceptance_id": "JRF20150707-050237-639234"},
        expected_generate_endpoint="/v1/me/sendchildorder",
        expected_translate_parameters={
            "product_code": "FX_BTC_JPY",
            "side": "BUY",
            "price": 2000000,
            "size": 0.01,
            "child_order_type": "LIMIT",
        },
        expected_order_id="JRF20150707-050237-639234",
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
