import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def tester(orderbook_fetch_api_tester):
    return orderbook_fetch_api_tester(
        symbol="BTCUSD_PERP",
        url="https://dapi.binance.com/dapi/v1/depth?symbol=BTCUSD_PERP",
        factory_method=BinanceCOINMWrapperFactory.create_orderbook_fetch_api,
        dummy_response={
            "lastUpdateId": 1027024,
            "E": 1589436922972,
            "T": 1589436922959,
            "bids": [["4.00000000", "431.00000000"]],
            "asks": [["4.00000200", "12.00000000"]],
        },
        expected_generate_endpoint="/dapi/v1/depth",
        expected_translate_parameters={"symbol": "BTCUSD_PERP"},
        expected_itemize_response={
            "BUY": [
                {"price": 4.0, "side": "BUY", "size": 431.0, "symbol": "BTCUSD_PERP"}
            ],
            "SELL": [
                {
                    "price": 4.000002,
                    "side": "SELL",
                    "size": 12.0,
                    "symbol": "BTCUSD_PERP",
                }
            ],
        },
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
