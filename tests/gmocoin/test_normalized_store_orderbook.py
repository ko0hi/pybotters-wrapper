import pandas as pd
import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(orderbook_normalized_store_tester):
    store = pybotters.GMOCoinDataStore()
    store._onmessage(
        {
            "channel": "orderbooks",
            "asks": [
                {"price": "455659", "size": "0.1"},
                {"price": "455658", "size": "0.2"},
            ],
            "bids": [
                {"price": "455665", "size": "0.1"},
                {"price": "455655", "size": "0.3"},
            ],
            "symbol": "BTC",
            "timestamp": "2018-03-30T12:34:56.789Z",
        },
        None,
    )
    # best bid
    dummy_data = next(iter(store.orderbooks.sorted().values()))[0]
    return orderbook_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "gmocoin"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "symbol": "BTC",
            "side": "BUY",
            "price": 455665.0,
            "size": 0.1,
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
