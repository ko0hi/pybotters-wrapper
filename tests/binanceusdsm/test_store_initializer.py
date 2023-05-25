import pybotters
import pytest
import pytest_mock
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory


@pytest.fixture
def store():
    return pybotters.BinanceUSDSMDataStore()


@pytest.fixture
def initializer_factory():
    return BinanceUSDSMWrapperFactory.create_store_initializer


@pytest.mark.asyncio
async def test_initialize_token(
    mocker: pytest_mock.MockerFixture, store, initializer_factory
):
    url = "https://fapi.binance.com/fapi/v1/listenKey"
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
    url = "https://fapi.binance.com/fapi/v1/depth?symbol=BTCUSDT"
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
    url = "https://fapi.binance.com/fapi/v1/openOrders"
    dummy_response = [
        {
            "orderId": 33952047156,
            "symbol": "BTCBUSD",
            "status": "NEW",
            "clientOrderId": "mcY2OVsa6U0Lb1xOqKkMVP",
            "price": "30230.2",
            "avgPrice": "0",
            "origQty": "0.100",
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": "BUY",
            "positionSide": "BOTH",
            "stopPrice": "30200",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "time": 1681265461299,
            "updateTime": 1681265461299,
        },
        {
            "orderId": 26663922405,
            "symbol": "ETHBUSD",
            "status": "NEW",
            "clientOrderId": "nCFMBpQ2CDC4uofIBNmjZG",
            "price": "1848.15",
            "avgPrice": "0",
            "origQty": "0.330",
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": "SELL",
            "positionSide": "BOTH",
            "stopPrice": "1850",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "time": 1681264051908,
            "updateTime": 1681264051908,
        },
    ]

    async with create_client() as client:
        initializer = initializer_factory(store)
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_order(client)

            assert (
                len(store.order) == 2
                and len(store.order.find({"s": "BTCBUSD"})) == 1
                and len(store.order.find({"s": "ETHBUSD"})) == 1
            )


@pytest.mark.asyncio
async def test_initialize_position(store, initializer_factory):
    url = "https://fapi.binance.com/fapi/v2/positionRisk"
    dummy_response = [
        {
            "symbol": "BTCBUSD",
            "positionAmt": "0.100",
            "entryPrice": "29951.6",
            "markPrice": "29957.30000000",
            "unRealizedProfit": "0.57000000",
            "liquidationPrice": "0",
            "leverage": "11",
            "maxNotionalValue": "7500000",
            "marginType": "cross",
            "isolatedMargin": "0.00000000",
            "isAutoAddMargin": "false",
            "positionSide": "BOTH",
            "notional": "2995.73000000",
            "isolatedWallet": "0",
            "updateTime": 1681271869878,
        },
        {
            "symbol": "ETHBUSD",
            "positionAmt": "0.330",
            "entryPrice": "1865.0",
            "markPrice": "1865.76000000",
            "unRealizedProfit": "0.25080000",
            "liquidationPrice": "0",
            "leverage": "20",
            "maxNotionalValue": "5000000",
            "marginType": "cross",
            "isolatedMargin": "0.00000000",
            "isAutoAddMargin": "false",
            "positionSide": "BOTH",
            "notional": "615.70080000",
            "isolatedWallet": "0",
            "updateTime": 1681266148117,
        },
    ]

    async with create_client() as client:
        initializer = initializer_factory(store)
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_position(client)

            assert (
                len(store.position) == 2
                and len(store.position.find({"s": "BTCBUSD"})) == 1
                and len(store.position.find({"s": "ETHBUSD"})) == 1
            )
