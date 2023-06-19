import pytest

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def tester(order_normalized_store_tester):
    dummy_data = {
        "s": "ETHUSD_230630",
        "c": "cSHy1KWSVtXLqk3F7AjuUC",
        "S": "BUY",
        "o": "LIMIT",
        "f": "GTC",
        "q": "1000",
        "p": "2099.21",
        "ap": "0",
        "sp": "0",
        "x": "NEW",
        "X": "NEW",
        "i": 614846957,
        "l": "0",
        "z": "0",
        "L": "0",
        "T": 1681734583165,
        "t": 0,
        "b": "4.76369681",
        "a": "0",
        "m": False,
        "R": False,
        "wt": "CONTRACT_PRICE",
        "ot": "LIMIT",
        "ps": "BOTH",
        "cp": False,
        "ma": "ETH",
        "rp": "0",
        "pP": False,
        "si": 0,
        "ss": 0,
    }
    return order_normalized_store_tester(
        builder_factory_method=BinanceCOINMWrapperFactory.create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "id": "614846957",
            "symbol": "ETHUSD_230630",
            "side": "BUY",
            "price": 2099.21,
            "size": 1000.0,
            "type": "LIMIT",
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
