import pandas as pd
import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(trades_normalized_store_tester):
    store = pybotters.bitFlyerDataStore()
    store.onmessage(
        {
            "jsonrpc": "2.0",
            "method": "channelMessage",
            "params": {
                "channel": "lightning_executions_FX_BTC_JPY",
                "message": [
                    {
                        "product_code": "FX_BTC_JPY",
                        "id": 2463530573,
                        "side": "BUY",
                        "price": 3688478.0,
                        "size": 0.002,
                        "exec_date": "2023-06-11T17:36:50.6358165Z",
                        "buy_child_order_acceptance_id": "JRF20230611-173650-139904",
                        "sell_child_order_acceptance_id": "JRF20230611-173621-142269",
                    }
                ],
            },
        },
        None,
    )
    dummy_data = store.executions.find()[0]
    return trades_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "bitflyer"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "id": "2463530573",
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "size": 0.002,
            "price": 3688478.0,
            "timestamp": pd.to_datetime("2023-06-11T17:36:50.6358165Z"),
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
