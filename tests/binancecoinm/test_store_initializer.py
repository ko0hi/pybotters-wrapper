import pybotters
import pytest
import pytest_mock
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def store():
    return pybotters.BinanceCOINMDataStore()


@pytest.fixture
def initializer_factory():
    return BinanceCOINMWrapperFactory.create_store_initializer


@pytest.mark.asyncio
async def test_initialize_token(
    mocker: pytest_mock.MockerFixture, store, initializer_factory
):
    url = "https://dapi.binance.com/dapi/v1/listenKey"
    dummy_response = {
        "listenKey": "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1"
    }
    patch = mocker.patch(
        "pybotters.models.binance.BinanceDataStoreBase._initialize_listenkey"
    )
    async with create_client() as client:
        initializer = initializer_factory(store)
        with aioresponses() as m:
            m.post(url, payload=dummy_response)
            await initializer.initialize_token(client)
            assert patch.call_count == 1


@pytest.mark.asyncio
async def test_initialize_orderbook(store, initializer_factory):
    url = "https://dapi.binance.com/dapi/v1/depth?symbol=BTCUSDT"
    dummy_response = {
        "lastUpdateId": 2730989998908,
        "E": 1681278004853,
        "T": 1681278004830,
        "bids": [["29928.70", "15.268"], ["29928.60", "0.339"], ["29928.50", "0.636"]],
        "asks": [["29928.80", "0.783"], ["29928.90", "0.028"], ["29929.00", "0.212"]],
    }
    async with create_client() as client:
        initializer = initializer_factory(store)
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_orderbook(client, symbol="BTCUSDT")
            assert (
                len(store.orderbook) == 6
                and len(store.orderbook.find({"S": "BUY"})) == 3
                and len(store.orderbook.find({"S": "SELL"})) == 3
            )


@pytest.mark.asyncio
async def test_initialize_order(store, initializer_factory):
    url = "https://dapi.binance.com/dapi/v1/openOrders"
    dummy_response = [
        {
            "orderId": 73762142,
            "symbol": "BNBUSD_230630",
            "pair": "BNBUSD",
            "status": "NEW",
            "clientOrderId": "xpQ2DSdZ71z1fHIRmgFqld",
            "price": "333.560",
            "avgPrice": "0",
            "origQty": "10",
            "executedQty": "0",
            "cumBase": "0",
            "timeInForce": "GTX",
            "type": "LIMIT",
            "reduceOnly": False,
            "closePosition": False,
            "side": "SELL",
            "positionSide": "BOTH",
            "stopPrice": "0",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "LIMIT",
            "time": 1681571755236,
            "updateTime": 1681571755236,
        },
        {
            "orderId": 77921621,
            "symbol": "ETHUSD_230929",
            "pair": "ETHUSD",
            "status": "NEW",
            "clientOrderId": "qIdFTiN0yGLsc1YruLWLQm",
            "price": "2139.89",
            "avgPrice": "0",
            "origQty": "10",
            "executedQty": "0",
            "cumBase": "0",
            "timeInForce": "GTX",
            "type": "LIMIT",
            "reduceOnly": False,
            "closePosition": False,
            "side": "BUY",
            "positionSide": "BOTH",
            "stopPrice": "0",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "LIMIT",
            "time": 1681571796424,
            "updateTime": 1681571796424,
        },
    ]

    async with create_client() as client:
        initializer = initializer_factory(store)
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_order(client)

            assert (
                len(store.order) == 2
                and len(store.order.find({"s": "BNBUSD_230630"})) == 1
                and len(store.order.find({"s": "ETHUSD_230929"})) == 1
            )


@pytest.mark.asyncio
async def test_initialize_position(store, initializer_factory):
    url = "https://dapi.binance.com/dapi/v1/positionRisk"
    dummy_response = [
        {
            "symbol": "BTCUSD_PERP",
            "positionAmt": "84",
            "entryPrice": "29280.47758262",
            "markPrice": "30424.30000000",
            "unRealizedProfit": "0.01078547",
            "liquidationPrice": "15041.07278064",
            "leverage": "50",
            "maxQty": "20",
            "marginType": "cross",
            "isolatedMargin": "0.00000000",
            "isAutoAddMargin": "false",
            "positionSide": "BOTH",
            "notionalValue": "0.27609509",
            "isolatedWallet": "0",
            "updateTime": 1681459263664,
        },
        {
            "symbol": "ETHUSD_PERP",
            "positionAmt": "2120",
            "entryPrice": "1910.53438261",
            "markPrice": "2101.72000000",
            "unRealizedProfit": "1.00939549",
            "liquidationPrice": "1912.97514231",
            "leverage": "100",
            "maxQty": "15",
            "marginType": "cross",
            "isolatedMargin": "0.00000000",
            "isAutoAddMargin": "false",
            "positionSide": "BOTH",
            "notionalValue": "10.08697638",
            "isolatedWallet": "0",
            "updateTime": 1680698909412,
        },
    ]

    async with create_client() as client:
        initializer = initializer_factory(store)
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_position(client)

            assert (
                len(store.position) == 2
                and len(store.position.find({"s": "BTCUSD_PERP"})) == 1
                and len(store.position.find({"s": "ETHUSD_PERP"})) == 1
            )
