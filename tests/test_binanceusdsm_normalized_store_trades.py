import pandas as pd
import pytest
from pybotters.store import StoreChange

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)
from pybotters_wrapper.core import TradesStore


@pytest.fixture
def trades_store() -> TradesStore:
    return create_binanceusdsm_normalized_store_builder().get("trades")


@pytest.fixture
def dummy_change() -> StoreChange:
    return StoreChange(
        None,
        "insert",
        {},
        {
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
        },
    )


@pytest.fixture
def dummy_change2() -> StoreChange:
    return StoreChange(
        None,
        "insert",
        {},
        {
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
        },
    )


def test_normalized_store_ticker_binanceusdsm_on_watch(trades_store, dummy_change):
    trades_store._on_watch(dummy_change)

    assert len(trades_store) == 1
    assert trades_store.find()[0] == {
        "id": "5933014",
        "symbol": "BTCUSDT",
        "side": "SELL",
        "price": 0.001,
        "size": 100.0,
        "timestamp": pd.to_datetime(123456785, unit="ms", utc=True),
        "info": {"data": dummy_change.data, "source": {}},
    }


def test_normalized_store_ticker_binanceusdsm_keys_duplicated(
    trades_store, dummy_change
):
    trades_store._on_watch(dummy_change)
    trades_store._on_watch(dummy_change)
    assert len(trades_store) == 1


def test_normalized_store_ticker_binanceusdsm_keys_different(
    trades_store, dummy_change
):
    trades_store._on_watch(dummy_change)
    eth_dummy_change = StoreChange(
        None,
        "insert",
        {},
        {
            **dummy_change.data,
            "s": "ETHUSDT"
        },
    )
    trades_store._on_watch(eth_dummy_change)
    assert len(trades_store) == 2
