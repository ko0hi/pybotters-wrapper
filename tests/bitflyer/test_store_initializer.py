import pybotters
import pytest
from aioresponses import aioresponses

import pybotters_wrapper as pbw
from pybotters_wrapper.core import StoreInitializer


@pytest.fixture
def initializer() -> StoreInitializer:
    return pbw.create_factory("bitflyer").create_store_initializer(
        pybotters.bitFlyerDataStore()
    )


@pytest.mark.asyncio
async def test_initialize_order(initializer: StoreInitializer) -> None:
    url = "https://api.bitflyer.com/v1/me/getchildorders?product_code=FX_BTC_JPY"
    dummy_response = [
        {
            "id": 0,
            "child_order_id": "JFX20230525-080246-033442F",
            "product_code": "FX_BTC_JPY",
            "side": "BUY",
            "child_order_type": "LIMIT",
            "price": 3000000.0,
            "average_price": 0.0,
            "size": 0.01,
            "child_order_state": "ACTIVE",
            "expire_date": "2023-06-24T08:02:46",
            "child_order_date": "2023-05-25T08:02:46",
            "child_order_acceptance_id": "JRF20230525-080246-059340",
            "outstanding_size": 0.01,
            "cancel_size": 0.0,
            "executed_size": 0.0,
            "total_commission": 0.0,
            "time_in_force": "GTC",
        },
        {
            "id": 0,
            "child_order_id": "JFX20230524-153027-665380F",
            "product_code": "FX_BTC_JPY",
            "side": "SELL",
            "child_order_type": "LIMIT",
            "price": 4100000.0,
            "average_price": 0.0,
            "size": 0.01,
            "child_order_state": "ACTIVE",
            "expire_date": "2023-06-23T15:30:27",
            "child_order_date": "2023-05-24T15:30:27",
            "child_order_acceptance_id": "JRF20230524-153027-054566",
            "outstanding_size": 0.01,
            "cancel_size": 0.0,
            "executed_size": 0.0,
            "total_commission": 0.0,
            "time_in_force": "GTC",
        },
        {
            "id": 2792230669,
            "child_order_id": "JFX20230411-152035-303765F",
            "product_code": "FX_BTC_JPY",
            "side": "BUY",
            "child_order_type": "MARKET",
            "price": 0.0,
            "average_price": 4461622.0,
            "size": 0.03,
            "child_order_state": "COMPLETED",
            "expire_date": "2023-05-11T15:20:35",
            "child_order_date": "2023-04-11T15:20:35",
            "child_order_acceptance_id": "JRF20230411-152035-090461",
            "outstanding_size": 0.0,
            "cancel_size": 0.0,
            "executed_size": 0.03,
            "total_commission": 0.0,
            "time_in_force": "GTC",
        },
    ]

    async with pbw.create_client() as client:
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_order(client, product_code="FX_BTC_JPY")

            assert 2 == len(initializer._store.childorders)
            assert (
                dummy_response[0]
                == initializer._store.childorders.find({"side": "BUY"})[0]
            )
            assert (
                dummy_response[1]
                == initializer._store.childorders.find({"side": "SELL"})[0]
            )


@pytest.mark.asyncio
async def test_initialize_position(initializer: StoreInitializer) -> None:
    url = "https://api.bitflyer.com/v1/me/getpositions?product_code=FX_BTC_JPY"
    dummy_response = [
        {
            "product_code": "FX_BTC_JPY",
            "side": "BUY",
            "price": 36000,
            "size": 10,
            "commission": 0,
            "swap_point_accumulate": -35,
            "require_collateral": 120000,
            "open_date": "2015-11-03T10:04:45.011",
            "leverage": 3,
            "pnl": 965,
            "sfd": -0.5,
        }
    ]

    async with pbw.create_client() as client:
        with aioresponses() as m:
            m.get(url, payload=dummy_response)
            await initializer.initialize_position(client, product_code="FX_BTC_JPY")

            assert 1 == len(initializer._store.positions)
            assert {
                "product_code": "FX_BTC_JPY",
                "side": "BUY",
                "price": 36000,
                "size": 10,
                "commission": 0,
                "sfd": -0.5,
            } == initializer._store.positions.find()[0]
