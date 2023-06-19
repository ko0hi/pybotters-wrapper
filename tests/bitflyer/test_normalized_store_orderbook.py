import pandas as pd
import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(orderbook_normalized_store_tester):
    # Boardストアの処理を実行させるのが面倒なのでwatchで流れてくるものをコピペ
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
        dummy_data=dummy_data,
        expected_item={
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "price": 3682693.0,
            "size": 0.04,
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
