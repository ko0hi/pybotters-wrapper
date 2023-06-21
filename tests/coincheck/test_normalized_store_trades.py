import pandas as pd
import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(trades_normalized_store_tester):
    store = pybotters.CoincheckDataStore()
    store._onmessage(
        [
            [
                "1663318663",
                "2357062",
                "btc_jpy",
                "2820896.0",
                "5.0",
                "sell",
                "1193401",
                "2078767",
            ],
            [
                "1663318892",
                "2357068",
                "btc_jpy",
                "2820357.0",
                "0.7828",
                "buy",
                "4456513",
                "8046665",
            ],
        ],
        None,
    )
    dummy_data = store.trades.find()[0]
    return trades_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "coincheck"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "id": "2357062",
            "symbol": "btc_jpy",
            "side": "SELL",
            "price": 2820896.0,
            "size": 5.0,
            "timestamp": pd.to_datetime(1663318663, unit="s", utc=True)
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
