import pytest

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)


@pytest.fixture
def tester(order_normalized_store_tester):
    dummy_data = {
        "s": "ETHUSDT",
        "c": "android_GxRRwCOJ8yCxYuwdZjhW",
        "S": "BUY",
        "o": "LIMIT",
        "f": "GTC",
        "q": "1",
        "p": "1500",
        "ap": "0",
        "sp": "0",
        "x": "NEW",
        "X": "NEW",
        "i": 8389765592161480505,
        "l": "0",
        "z": "0",
        "L": "0",
        "n": "0",
        "N": "USDT",
        "T": 1681472450078,
        "t": 0,
        "b": "1500",
        "a": "0",
        "m": False,
        "R": False,
        "wt": "CONTRACT_PRICE",
        "ot": "LIMIT",
        "ps": "BOTH",
        "cp": False,
        "rp": "0",
        "pP": False,
        "si": 0,
        "ss": 0,
    }
    return order_normalized_store_tester(
        builder_factory_method=create_binanceusdsm_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "id": "8389765592161480505",
            "symbol": "ETHUSDT",
            "side": "BUY",
            "price": 1500.0,
            "size": 1.0,
            "type": "LIMIT",
            "info": {
                "data": dummy_data,
                "source": {},
            },
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
