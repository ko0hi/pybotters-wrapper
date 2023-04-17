import pandas as pd
import pytest

from pybotters_wrapper.binance.binancecoinm import (
    create_binancecoinm_normalized_store_builder,
)


@pytest.fixture
def tester(trades_normalized_store_tester):
    dummy_data = {
        "e": "aggTrade",
        "E": 1681734078394,
        "a": 252492189,
        "s": "BTCUSD_PERP",
        "p": "29503.4",
        "q": "23",
        "f": 616957754,
        "l": 616957754,
        "T": 1681734078230,
        "m": True,
    }
    return trades_normalized_store_tester(
        builder_factory_method=create_binancecoinm_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "id": "252492189",
            "symbol": "BTCUSD_PERP",
            "side": "SELL",
            "price": 29503.4,
            "size": 23.0,
            "timestamp": pd.to_datetime(1681734078230, unit="ms", utc=True),
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
