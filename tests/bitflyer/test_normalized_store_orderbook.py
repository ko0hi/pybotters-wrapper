import pandas as pd
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(orderbook_normalized_store_tester):
    dummy_data = {
        "price": 3682693.0,
        "product_code": "FX_BTC_JPY",
        "side": "BUY",
        "size": 0.04,
    }
    return orderbook_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "bitflyer"
        ).create_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "price": 3682693.0,
            "size": 0.04,
            "info": {"data": dummy_data, "source": {}},
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
