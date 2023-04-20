import pytest

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)


@pytest.fixture
def tester(ticker_normalized_store_tester):
    dummy_data = {
        "e": "24hrTicker",
        "E": 123456789,
        "s": "BTCUSDT",
        "p": "0.0015",
        "P": "250.00",
        "w": "0.0018",
        "c": "0.0025",
        "Q": "10",
        "o": "0.0010",
        "h": "0.0025",
        "l": "0.0010",
        "v": "10000",
        "q": "18",
        "O": 0,
        "C": 86400000,
        "F": 0,
        "L": 18150,
        "n": 18151,
    }
    return ticker_normalized_store_tester(
        builder_factory_method=create_binanceusdsm_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "symbol": "BTCUSDT",
            "price": 0.0025,
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
