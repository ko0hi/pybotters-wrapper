import pandas as pd
import pytest

from pybotters.store import StoreChange
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)
from pybotters_wrapper.core import ExecutionStore


@pytest.fixture
def order_store() -> ExecutionStore:
    return create_binanceusdsm_normalized_store_builder().get("order")


@pytest.fixture
def dummy_change_insert() -> StoreChange:
    return StoreChange(
        None,
        "insert",
        {},
        {
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
        },
    )


@pytest.fixture
def dummy_change_delete() -> StoreChange:
    return StoreChange(
        None,
        "delete",
        {
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
        },
        {
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
        },
    )


def test_on_watch_insert(
    order_store, dummy_change_insert
):
    order_store._on_watch(dummy_change_insert)
    assert len(order_store) == 1
    assert order_store.find()[0] == {
        "id": "8389765592161480505",
        "symbol": "ETHUSDT",
        "side": "BUY",
        "price": 1500.0,
        "size": 1.0,
        "type": "LIMIT",
        "info": {
            "data": dummy_change_insert.data,
            "source": dummy_change_insert.source,
        },
    }


def test_on_watch_insert_and_delete(
    order_store, dummy_change_insert, dummy_change_delete
):
    order_store._on_watch(dummy_change_insert)
    order_store._on_watch(dummy_change_delete)
    assert len(order_store) == 0
