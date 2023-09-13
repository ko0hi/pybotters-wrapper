import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(orderbook_fetch_api_tester):
    return orderbook_fetch_api_tester(
        symbol="FX_BTC_JPY",
        url="https://api.bitflyer.com/v1/getboard?product_code=FX_BTC_JPY",
        factory_method=pbw.create_factory("bitflyer").create_orderbook_fetch_api,
        dummy_response={
            "mid_price": 33320,
            "bids": [{"price": 30000, "size": 0.1}, {"price": 25570, "size": 3}],
            "asks": [{"price": 36640, "size": 5}, {"price": 36700, "size": 1.2}],
        },
        expected_generate_endpoint="/v1/getboard",
        expected_translate_parameters={"product_code": "FX_BTC_JPY"},
        expected_itemize_response={
            "SELL": [
                {
                    "symbol": "FX_BTC_JPY",
                    "price": 36640,
                    "size": 5,
                    "side": "SELL",
                },
                {"symbol": "FX_BTC_JPY", "price": 36700, "size": 1.2, "side": "SELL"},
            ],
            "BUY": [
                {"symbol": "FX_BTC_JPY", "price": 30000, "size": 0.1, "side": "BUY"},
                {"symbol": "FX_BTC_JPY", "price": 25570, "size": 3, "side": "BUY"},
            ],
        },
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
