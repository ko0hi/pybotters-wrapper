import pytest

from pybotters_wrapper.core import PositionStore


@pytest.fixture
def store():
    return PositionStore(None)


@pytest.fixture
def multiposition_store():
    return PositionStore(None, keys=[])


def test_one_symbol_one_position(store):
    store._insert(
        [
            {"symbol": "BTCUSDT", "price": 20000, "size": 0.1, "side": "BUY"},
            {"symbol": "BTCUSDT", "price": 30000, "size": 0.1, "side": "BUY"},
        ]
    )
    assert len(store) == 1


def test_size(store):
    store._insert(
        [
            {"symbol": "BTCUSDT", "price": 20000, "size": 0.1, "side": "BUY"},
            {"symbol": "ETHUSDT", "price": 2000, "size": 10, "side": "SELL"},
        ]
    )

    assert store.size("BTCUSDT", "BUY") == 0.1
    assert store.size("ETHUSDT", "SELL") == 10
    assert store.size("BTCUSDT") == 0.1
    assert store.size("ETHUSDT") == -10


def test_summary(store):
    store._insert(
        [
            {"symbol": "BTCUSDT", "price": 20000, "size": 0.1, "side": "BUY"},
            {"symbol": "ETHUSDT", "price": 2000, "size": 10, "side": "SELL"},
        ]
    )
    assert store.summary("BTCUSDT") == {
        "BUY_price": 20000,
        "BUY_size": 0.1,
        "SELL_price": 0,
        "SELL_size": 0,
        "side": "BUY",
        "size": 0.1,
    }


def test_one_symbol_multiple_positions(multiposition_store):
    multiposition_store._insert(
        [
            {"symbol": "BTCUSDT", "price": 20000, "size": 0.1, "side": "BUY"},
            {"symbol": "BTCUSDT", "price": 30000, "size": 0.1, "side": "BUY"},
        ]
    )
    assert len(multiposition_store) == 1
