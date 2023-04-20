import pytest
import pytest_mock

from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory


@pytest.fixture
def tester(ticker_fetch_api_tester):
    return ticker_fetch_api_tester(
        symbol="BTCUSDT",
        url="https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT",
        factory_method=BinanceUSDSMWrapperFactory.create_fetch_ticker_api,
        dummy_response={
            "symbol": "BTCUSDT",
            "price": "6000.01",
            "time": 1589437530011,
        },
        expected_generate_endpoint="/fapi/v1/ticker/price",
        expected_translate_parameters={"symbol": "BTCUSDT"},
        expected_itemize_response={"symbol": "BTCUSDT", "price": 6000.01},
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

