import pytest
from pybotters.store import StoreChange

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)
from pybotters_wrapper.core import TickerStore


@pytest.fixture
def trades_store() -> TickerStore:
    return create_binanceusdsm_normalized_store_builder().get("ticker")


@pytest.fixture
def dummy_change() -> StoreChange:
    return StoreChange(
        None,
        "insert",
        {},
        {
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
        },
    )


def test_normalized_store_ticker_binanceusdsm_on_watch(trades_store, dummy_change):
    trades_store._on_watch(dummy_change)

    assert len(trades_store) == 1
    assert trades_store.find()[0] == {
        "symbol": "BTCUSDT",
        "price": 0.0025,
        "info": {"data": dummy_change.data, "source": {}},
    }


def test_normalized_store_ticker_binanceusdsm_single_item_per_symbol1(
        trades_store, dummy_change
):
    trades_store._on_watch(dummy_change)
    trades_store._on_watch(dummy_change)
    assert len(trades_store) == 1


def test_normalized_store_ticker_binanceusdsm_single_item_per_symbol2(
        trades_store, dummy_change
):
    trades_store._on_watch(dummy_change)
    eth_dummy_change = StoreChange(
        None,
        "insert",
        {},
        {
            "e": "24hrTicker",
            "E": 123456789,
            "s": "ETHUSDT",
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
        },
    )
    trades_store._on_watch(eth_dummy_change)
    assert len(trades_store) == 2
