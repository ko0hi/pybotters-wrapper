import pandas as pd
import pytest

from pybotters_wrapper.binance.binancecoinm import (
    create_binancecoinm_normalized_store_builder,
)
from pybotters_wrapper.core import ExecutionStore


@pytest.fixture
def execution_store() -> ExecutionStore:
    return create_binancecoinm_normalized_store_builder().get("execution")


@pytest.fixture
def dummy_filled_msg() -> dict:
    return {
        "e": "ORDER_TRADE_UPDATE",
        "T": 1676463834343,
        "E": 1676463834350,
        "i": "FzoCmYuXfWXqAufW",
        "o": {
            "s": "BTCUSD_PERP",
            "c": "3CdYy9VxMrpchymRKfuCKg",
            "S": "SELL",
            "o": "MARKET",
            "f": "GTC",
            "q": "3",
            "p": "0",
            "ap": "22910.8",
            "sp": "0",
            "x": "TRADE",
            "X": "FILLED",
            "i": 79264893095,
            "l": "3",
            "z": "3",
            "L": "22910.8",
            "n": "0.00000589",
            "N": "BTC",
            "T": 1676463834343,
            "t": 586130831,
            "b": "0",
            "a": "0",
            "m": False,
            "R": False,
            "wt": "CONTRACT_PRICE",
            "ot": "MARKET",
            "ps": "BOTH",
            "cp": False,
            "ma": "BTC",
            "rp": "0.00033105",
            "pP": False,
            "si": 0,
            "ss": 0,
        },
    }


@pytest.fixture
def dummy_partially_filled_msg() -> dict:
    return {
        "e": "ORDER_TRADE_UPDATE",
        "T": 1675430899714,
        "E": 1675430899722,
        "i": "FzoCmYuXfWXqAufW",
        "o": {
            "s": "ADAUSD_230630",
            "c": "XvT99wnzjQ9p3WOkBy6vB4",
            "S": "SELL",
            "o": "LIMIT",
            "f": "GTC",
            "q": "405",
            "p": "0.40409",
            "ap": "0.40409",
            "sp": "0",
            "x": "TRADE",
            "X": "PARTIALLY_FILLED",
            "i": 31817514,
            "l": "50",
            "z": "50",
            "L": "0.40409",
            "n": "0.09898784",
            "N": "ADA",
            "T": 1675430899714,
            "t": 107533,
            "b": "0",
            "a": "11600.47303030",
            "m": True,
            "R": False,
            "wt": "CONTRACT_PRICE",
            "ot": "LIMIT",
            "ps": "BOTH",
            "cp": False,
            "ma": "ADA",
            "rp": "0",
            "pP": False,
            "si": 0,
            "ss": 0,
        },
    }


def test_on_msg_filled(execution_store, dummy_filled_msg):
    execution_store._on_msg(dummy_filled_msg)
    assert len(execution_store) == 1
    assert execution_store.find()[0] == {
        "id": "79264893095",
        "symbol": "BTCUSD_PERP",
        "side": "SELL",
        "price": 22910.8,
        "size": 3.0,
        "timestamp": pd.to_datetime(1676463834343, unit="ms", utc=True),
        "info": {"data": dummy_filled_msg, "source": None},
    }


def test_on_msg_partially_filled(execution_store, dummy_partially_filled_msg):
    execution_store._on_msg(dummy_partially_filled_msg)
    assert len(execution_store) == 1
    assert execution_store.find()[0] == {
        "id": "31817514",
        "symbol": "ADAUSD_230630",
        "side": "SELL",
        "price": 0.40409,
        "size": 50.0,
        "timestamp": pd.to_datetime(1675430899714, unit="ms", utc=True),
        "info": {"data": dummy_partially_filled_msg, "source": None},
    }
