import pandas as pd
import pytest
import pytest_mock
import pybotters
from pybotters.store import StoreChange

import pybotters_wrapper as pbw


@pytest.fixture
def tester(execution_normalized_store_tester):
    store = pybotters.bitFlyerDataStore()
    store.onmessage(
        {
            "jsonrpc": "2.0",
            "method": "channelMessage",
            "params": {
                "channel": "child_order_events",
                "message": [
                    {
                        "child_order_acceptance_id": "JRF20220809-131731-061756",
                        "child_order_id": "JFX20220809-131731-449862F",
                        "commission": 0,
                        "event_date": "2022-08-09T13:17:31.3350519Z",
                        "event_type": "EXECUTION",
                        "exec_id": 2373644588,
                        "outstanding_size": 0,
                        "price": 3133605,
                        "product_code": "FX_BTC_JPY",
                        "sfd": 0,
                        "side": "BUY",
                        "size": 0.01,
                    },
                ],
            },
        },
        None,
    )
    dummy_data = store.childorderevents.find()[0]
    return execution_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "bitflyer"
        ).create_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "id": "JRF20220809-131731-061756",
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "price": 3133605.0,
            "size": 0.01,
            "timestamp": pd.to_datetime("2022-08-09T13:17:31.3350519Z"),
        },
    )


def test_insert(tester):
    tester.test_insert()


def test_update(tester):
    tester.test_update()


def test_delete(tester):
    tester.test_delete()


def test_item(tester):
    tester.test_item()


@pytest.mark.parametrize(
    "dummy_data",
    [
        {
            "child_order_acceptance_id": "JRF20220809-131731-061756",
            "child_order_id": "JFX20220809-131731-449862F",
            "child_order_type": "MARKET",
            "event_date": "2022-08-09T13:17:31.3350519Z",
            "event_type": "ORDER",
            "expire_date": "2022-09-08T13:17:31",
            "price": 0,
            "product_code": "FX_BTC_JPY",
            "side": "BUY",
            "size": 0.01,
        },
        {
            "child_order_acceptance_id": "JRF20220809-131731-061756",
            "child_order_id": "JFX20220809-131731-449862F",
            "child_order_type": "MARKET",
            "event_date": "2022-08-09T13:17:31.3350519Z",
            "event_type": "ORDER",
            "expire_date": "2022-09-08T13:17:31",
            "price": 0,
            "product_code": "FX_BTC_JPY",
            "side": "BUY",
            "size": 0.01,
        },
    ],
)
def test_ignore_non_execution_event(
    mocker: pytest_mock.MockerFixture, dummy_data: dict
):
    store = pbw.create_factory("bitflyer").create_normalized_store_builder().execution()

    spy_get_operation = mocker.spy(store, "_get_operation")
    spy_normalize = mocker.spy(store, "_normalize")
    store._on_watch(StoreChange(store._base_store, "insert", {}, dummy_data))

    assert len(store) == 0
    assert spy_get_operation.spy_return is None
    spy_get_operation.assert_called_once()
    spy_normalize.assert_not_called()
