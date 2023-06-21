import pytest
import pytest_mock


import pybotters_wrapper as pbw


@pytest.fixture
def tester(orderbook_fetch_api_tester):
    return orderbook_fetch_api_tester(
        symbol="btc_jpy",
        url="https://coincheck.com/api/order_books?pair=btc_jpy",
        factory_method=pbw.create_factory("coincheck").create_orderbook_fetch_api,
        dummy_response={
            "asks": [[27330, "2.25"], [27340, "0.45"]],
            "bids": [[27240, "1.1543"], [26800, "1.2226"]],
        },
        expected_generate_endpoint="/api/order_books",
        expected_translate_parameters={"pair": "btc_jpy"},
        expected_itemize_response={
            "SELL": [
                {"symbol": "btc_jpy", "side": "SELL", "price": 27330.0, "size": 2.25},
                {"symbol": "btc_jpy", "side": "SELL", "price": 27340.0, "size": 0.45},
            ],
            "BUY": [
                {"symbol": "btc_jpy", "side": "BUY", "price": 27240.0, "size": 1.1543},
                {"symbol": "btc_jpy", "side": "BUY", "price": 26800.0, "size": 1.2226},
            ],
        },
    )


@pytest.mark.asyncio
@pytest.mark.skip
async def test_fetch(tester):
    resp, data = await tester.test_fetch()
    print(data)


@pytest.mark.asyncio
# @pytest.mark.skip
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
