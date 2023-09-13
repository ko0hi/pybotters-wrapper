import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(ticker_fetch_api_tester):
    return ticker_fetch_api_tester(
        symbol="btc_jpy",
        url="https://public.bitbank.cc/btc_jpy/ticker",
        factory_method=pbw.create_factory("bitbank").create_ticker_fetch_api,
        dummy_response={
            "data": {
                "buy": "4031998",
                "high": "4085800",
                "last": "4031999",
                "low": "3781999",
                "open": "3817465",
                "sell": "4031999",
                "timestamp": 1687320253211,
                "vol": "702.0243",
            },
            "success": 1,
        },
        expected_generate_endpoint="/btc_jpy/ticker",
        expected_translate_parameters={},
        expected_itemize_response={"symbol": "btc_jpy", "price": 4031999.0},
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
