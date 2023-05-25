import pytest
import pytest_mock

from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory


@pytest.fixture
def tester(positions_fetch_api_tester):
    dummy_responses = [
        {
            "symbol": "ETHBUSD",
            "positionAmt": "-0.330",
            "entryPrice": "1995.0",
            "markPrice": "1997.57780226",
            "unRealizedProfit": "-0.85067474",
            "liquidationPrice": "45498.37431442",
            "leverage": "20",
            "maxNotionalValue": "5000000",
            "marginType": "cross",
            "isolatedMargin": "0.00000000",
            "isAutoAddMargin": "false",
            "positionSide": "BOTH",
            "notional": "-659.20067474",
            "isolatedWallet": "0",
            "updateTime": 1681393911012,
        }
    ]
    return positions_fetch_api_tester(
        symbol="ETHBUSD",
        url="https://fapi.binance.com/fapi/v2/positionRisk?symbol=ETHBUSD",
        factory_method=BinanceUSDSMWrapperFactory.create_positions_fetch_api,
        dummy_response=dummy_responses,
        expected_generate_endpoint="/fapi/v2/positionRisk",
        expected_translate_parameters={"symbol": "ETHBUSD"},
        expected_itemize_response=[
            {
                "symbol": "ETHBUSD",
                "side": "SELL",
                "price": 1995.0,
                "size": -0.330,
                "info": dummy_responses[0],
            }
        ],
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
