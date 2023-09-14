import pandas as pd
import pytest

from pybotters_wrapper.binance.binanceusdsm import BinanceUSDSMWrapperFactory
from pybotters_wrapper.core import ExecutionStore


@pytest.fixture
def execution_store() -> ExecutionStore:
    return BinanceUSDSMWrapperFactory.create_normalized_store_builder().get("execution")


@pytest.fixture
def dummy_filled_msg() -> dict:
    return {
        "e": "ORDER_TRADE_UPDATE",
        "T": 1680184493444,
        "E": 1680184493451,
        "o": {
            "s": "APTBUSD",
            "c": "UoYDzWlCzOLQNuCTWziSHn",
            "S": "BUY",
            "o": "LIMIT",
            "f": "GTC",
            "q": "40",
            "p": "11.22400",
            "ap": "11.213975",
            "sp": "11.21200",
            "x": "TRADE",
            "X": "FILLED",
            "i": 1402203845,
            "l": "36.3",
            "z": "40",
            "L": "11.21400",
            "n": "0.12212046",
            "N": "BUSD",
            "T": 1680184493444,
            "t": 29329913,
            "b": "0",
            "a": "0",
            "m": False,
            "R": False,
            "wt": "CONTRACT_PRICE",
            "ot": "STOP",
            "ps": "BOTH",
            "cp": False,
            "rp": "-0.66789250",
            "pP": False,
            "si": 0,
            "ss": 0,
        },
    }


@pytest.fixture
def dummy_partially_filled_msg() -> dict:
    return {
        "e": "ORDER_TRADE_UPDATE",
        "T": 1680184493444,
        "E": 1680184493451,
        "o": {
            "s": "APTBUSD",
            "c": "UoYDzWlCzOLQNuCTWziSHn",
            "S": "BUY",
            "o": "LIMIT",
            "f": "GTC",
            "q": "40",
            "p": "11.22400",
            "ap": "11.213730",
            "sp": "11.21200",
            "x": "TRADE",
            "X": "PARTIALLY_FILLED",
            "i": 1402203845,
            "l": "2.7",
            "z": "3.7",
            "L": "11.21400",
            "n": "0.00908334",
            "N": "BUSD",
            "T": 1680184493444,
            "t": 29329912,
            "b": "407.431200",
            "a": "0",
            "m": False,
            "R": False,
            "wt": "CONTRACT_PRICE",
            "ot": "STOP",
            "ps": "BOTH",
            "cp": False,
            "rp": "-0.11063250",
            "pP": False,
            "si": 0,
            "ss": 0,
        },
    }


def test_on_msg_filled(execution_store, dummy_filled_msg):
    execution_store._on_msg(dummy_filled_msg)
    assert len(execution_store) == 1
    assert execution_store.find()[0] == {
        "id": "1402203845",
        "symbol": "APTBUSD",
        "side": "BUY",
        "price": 11.21400,
        "size": 36.3,
        "timestamp": pd.to_datetime(1680184493444, unit="ms", utc=True),
        "info": {"data": dummy_filled_msg, "source": None},
    }


def test_on_msg_partially_filled(execution_store, dummy_partially_filled_msg):
    execution_store._on_msg(dummy_partially_filled_msg)
    assert len(execution_store) == 1
    assert execution_store.find()[0] == {
        "id": "1402203845",
        "symbol": "APTBUSD",
        "side": "BUY",
        "price": 11.21400,
        "size": 2.7,
        "timestamp": pd.to_datetime(1680184493444, unit="ms", utc=True),
        "info": {"data": dummy_partially_filled_msg, "source": None},
    }
