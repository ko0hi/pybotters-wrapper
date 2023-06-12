import pytest
import pytest_mock


import pybotters_wrapper as pbw


@pytest.fixture
def tester(ticker_fetch_api_tester):
    return ticker_fetch_api_tester(
        symbol="FX_BTC_JPY",
        url="https://api.bitflyer.com/v1/getticker?product_code=FX_BTC_JPY",
        factory_method=pbw.create_factory("bitflyer").create_ticker_fetch_api,
        dummy_response={
            "product_code": "FX_BTC_JPY",
            "state": "RUNNING",
            "timestamp": "2015-07-08T02:50:59.97",
            "tick_id": 3579,
            "best_bid": 30000,
            "best_ask": 36640,
            "best_bid_size": 0.1,
            "best_ask_size": 5,
            "total_bid_depth": 15.13,
            "total_ask_depth": 20,
            "market_bid_size": 0,
            "market_ask_size": 0,
            "ltp": 31690,
            "volume": 16819.26,
            "volume_by_product": 6819.26,
        },
        expected_generate_endpoint="/v1/getticker",
        expected_translate_parameters={"product_code": "FX_BTC_JPY"},
        expected_itemize_response={"symbol": "FX_BTC_JPY", "price": 31690.0},
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_fetch(tester):
    resp, data = await tester.test_fetch()
    print(data)


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
