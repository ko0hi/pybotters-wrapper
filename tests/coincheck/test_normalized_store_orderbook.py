import pandas as pd
import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(orderbook_normalized_store_tester):
    store = pybotters.CoincheckDataStore()
    store._onmessage(
        [
            "btc_jpy",
            {
                "bids": [["148634.0", "0.12"], ["148633.0", "0.0574"]],
                "asks": [["148834.0", "0.0812"], ["148833.0", "1.0581"]],
                "last_update_at": "1659321701",
            },
        ],
        None,
    )
    dummy_data = store.orderbook.find({"side":"bids"})[0]
    return orderbook_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "coincheck"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "symbol": "btc_jpy",
            "side": "BUY",
            "price": 148634.0,
            "size": 0.12,
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
