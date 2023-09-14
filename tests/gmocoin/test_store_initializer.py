import pybotters
import pytest
from aioresponses import aioresponses

import pybotters_wrapper as pbw
from pybotters_wrapper.core import StoreInitializer


@pytest.fixture
def initializer() -> StoreInitializer:
    return pbw.create_factory("gmocoin").create_store_initializer(
        pybotters.GMOCoinDataStore()
    )


@pytest.mark.asyncio
@pytest.mark.skip(reason="Require mock")
async def test_initialize_token(initializer: StoreInitializer) -> None:
    url = "https://api.coin.z.com/private/v1/ws-auth"
    dummy_response = {
        "status": 0,
        "data": "xxxxxxxxxxxxxxxxxxxx",
        "responsetime": "2019-03-19T02:15:06.102Z",
    }
    async with pbw.create_client() as client:
        with aioresponses() as m:
            m.post(url, payload=dummy_response)
            await initializer.initialize_token(client)
            assert "xxxxxxxxxxxxxxxxxxxx" == initializer._store.token


@pytest.mark.asyncio
async def test_initialize_order(initializer: StoreInitializer) -> None:
    url = "https://api.coin.z.com/private/v1/activeOrders?symbol=BTC_JPY"
    dummy_response = {
        "status": 0,
        "data": {
            "pagination": {"currentPage": 1, "count": 30},
            "list": [
                {
                    "rootOrderId": 123456789,
                    "orderId": 123456789,
                    "symbol": "BTC",
                    "side": "BUY",
                    "orderType": "NORMAL",
                    "executionType": "LIMIT",
                    "settleType": "OPEN",
                    "size": "1",
                    "executedSize": "0",
                    "price": "840000",
                    "losscutPrice": "0",
                    "status": "ORDERED",
                    "timeInForce": "FAS",
                    "timestamp": "2019-03-19T01:07:24.217Z",
                }
            ],
        },
        "responsetime": "2019-03-19T01:07:24.217Z",
    }

    async with pbw.create_client() as client:
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_order(client, symbol="BTC_JPY")
            assert 1 == len(initializer._store.orders)
            assert 123456789 == initializer._store.orders.find()[0]["order_id"]


@pytest.mark.asyncio
async def test_initialize_position(initializer: StoreInitializer) -> None:
    url = "https://api.coin.z.com/private/v1/openPositions?symbol=BTC_JPY"
    dummy_response = {
        "status": 0,
        "data": {
            "pagination": {"currentPage": 1, "count": 30},
            "list": [
                {
                    "positionId": 1234567,
                    "symbol": "BTC_JPY",
                    "side": "BUY",
                    "size": "0.22",
                    "orderdSize": "0",
                    "price": "876045",
                    "lossGain": "14",
                    "leverage": "4",
                    "losscutPrice": "766540",
                    "timestamp": "2019-03-19T02:15:06.094Z",
                }
            ],
        },
        "responsetime": "2019-03-19T02:15:06.095Z",
    }

    async with pbw.create_client() as client:
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_position(client, symbol="BTC_JPY")

            assert 1 == len(initializer._store.positions)
            assert 1234567 == initializer._store.positions.find()[0]["position_id"]
