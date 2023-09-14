import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(cancel_order_tester):
    return cancel_order_tester(
        url="https://coincheck.com/api/exchange/orders/12345",
        request_method="DELETE",
        factory_method=pbw.create_factory("coincheck").create_cancel_order_api,
        dummy_order_parameters={
            "symbol": "btc_jpy",
            "order_id": "12345",
            "extra_params": {},
        },
        dummy_response={"success": True, "id": 12345},
        expected_generate_endpoint="/api/exchange/orders/12345",
        expected_translate_parameters={},
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
