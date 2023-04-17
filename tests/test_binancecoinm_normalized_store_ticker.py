import pytest

from pybotters_wrapper.binance.binancecoinm import (
    create_binancecoinm_normalized_store_builder,
)


@pytest.fixture
def tester(ticker_normalized_store_tester):
    dummy_data = {
        "e": "24hrTicker",
        "E": 1681732620091,
        "s": "BTCUSD_PERP",
        "ps": "BTCUSD",
        "p": "-669.8",
        "P": "-2.213",
        "w": "30009.15252615",
        "c": "29595.1",
        "Q": "53",
        "o": "30264.9",
        "h": "30575.0",
        "l": "29290.0",
        "v": "15949868",
        "q": "53150.01143768",
        "O": 1681646220000,
        "C": 1681732620082,
        "F": 616648586,
        "L": 616948705,
        "n": 300035,
    }
    return ticker_normalized_store_tester(
        builder_factory_method=create_binancecoinm_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "symbol": "BTCUSD_PERP",
            "price": 29595.1,
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
