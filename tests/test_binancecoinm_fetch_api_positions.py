import pytest
import pytest_mock

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def tester(positions_fetch_api_tester):
    return positions_fetch_api_tester(
        symbol="BTCUSD_PERP",
        url="https://dapi.binance.com/dapi/v1/positionRisk?symbol=BTCUSD_PERP",
        factory_method=BinanceCOINMWrapperFactory.create_fetch_positions_api,
        dummy_response=[
            {
                "symbol": "BTCUSD_PERP",
                "positionAmt": "84",
                "entryPrice": "29280.47758262",
                "markPrice": "29974.20000000",
                "unRealizedProfit": "0.00663955",
                "liquidationPrice": "14938.53830292",
                "leverage": "50",
                "maxQty": "20",
                "marginType": "cross",
                "isolatedMargin": "0.00000000",
                "isAutoAddMargin": "false",
                "positionSide": "BOTH",
                "notionalValue": "0.28024100",
                "isolatedWallet": "0",
                "updateTime": 1681459263664,
            }
        ],
        expected_generate_endpoint="/dapi/v1/positionRisk",
        expected_translate_parameters={"symbol": "BTCUSD_PERP"},
        expected_itemize_response=[
            {
                "symbol": "BTCUSD_PERP",
                "side": "BUY",
                "price": 29280.47758262,
                "size": 84.0,
                "info": {
                    "symbol": "BTCUSD_PERP",
                    "positionAmt": "84",
                    "entryPrice": "29280.47758262",
                    "markPrice": "29974.20000000",
                    "unRealizedProfit": "0.00663955",
                    "liquidationPrice": "14938.53830292",
                    "leverage": "50",
                    "maxQty": "20",
                    "marginType": "cross",
                    "isolatedMargin": "0.00000000",
                    "isAutoAddMargin": "false",
                    "positionSide": "BOTH",
                    "notionalValue": "0.28024100",
                    "isolatedWallet": "0",
                    "updateTime": 1681459263664,
                },
            }
        ],
    )


@pytest.mark.asyncio
# @pytest.mark.skip
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
