import pandas as pd
import pytest

from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory


@pytest.fixture
def tester(trades_normalized_store_tester):
    dummy_data = {
        "e": "aggTrade",
        "E": 123456789,
        "s": "BTCUSDT",
        "a": 5933014,
        "p": "0.001",
        "q": "100",
        "f": 100,
        "l": 105,
        "T": 123456785,
        "m": True,
    }
    return trades_normalized_store_tester(
        builder_factory_method=BinanceUSDSMWrapperFactory.create_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "id": "5933014",
            "symbol": "BTCUSDT",
            "side": "SELL",
            "price": 0.001,
            "size": 100.0,
            "timestamp": pd.to_datetime(123456785, unit="ms", utc=True),
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
