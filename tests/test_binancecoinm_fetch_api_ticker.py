import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def tester(ticker_fetch_api_tester):
    return ticker_fetch_api_tester(
        symbol="BTCUSD_PERP",
        url="https://dapi.binance.com/dapi/v1/ticker/price?symbol=BTCUSD_PERP",
        factory_method=BinanceCOINMWrapperFactory.create_fetch_ticker_api,
        dummy_response={
            "symbol": "BTCUSD_PERP",
            "price": "6000.01",
            "time": 1589437530011,
        },
        expected_generate_endpoint="/dapi/v1/ticker/price",
        expected_translate_parameters={"symbol": "BTCUSD_PERP"},
        expected_itemize_response={"symbol": "BTCUSD_PERP", "price": 6000.01},
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
