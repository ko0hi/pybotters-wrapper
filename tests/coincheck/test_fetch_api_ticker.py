import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(ticker_fetch_api_tester):
    return ticker_fetch_api_tester(
        symbol="btc_jpy",
        url="https://coincheck.com/api/ticker?pair=btc_jpy",
        factory_method=pbw.create_factory("coincheck").create_ticker_fetch_api,
        dummy_response={
            "last": 27390,
            "bid": 26900,
            "ask": 27390,
            "high": 27659,
            "low": 26400,
            "volume": "50.29627103",
            "timestamp": 1423377841,
        },
        expected_generate_endpoint="/api/ticker",
        expected_translate_parameters={"pair": "btc_jpy"},
        expected_itemize_response={"symbol": "btc_jpy", "price": 27390.0},
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
