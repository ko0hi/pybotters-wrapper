import pytest
from pybotters.store import StoreChange

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)
from pybotters_wrapper.core import PositionStore


@pytest.fixture
def position_store() -> PositionStore:
    return create_binanceusdsm_normalized_store_builder().get("position")


@pytest.fixture
def socket_msg(resource_loader) -> dict:
    return resource_loader("binanceusdsm_account_update.json")


@pytest.fixture
def dummy_change_BOTH(socket_msg) -> StoreChange:
    return StoreChange(
        None,
        "update",
        {},
        socket_msg["a"]["P"][0],
    )


@pytest.fixture
def dummy_change_LONG(socket_msg) -> StoreChange:
    return StoreChange(
        None,
        "update",
        {},
        socket_msg["a"]["P"][1],
    )


@pytest.fixture
def dummy_change_SHORT(socket_msg) -> StoreChange:
    return StoreChange(
        None,
        "update",
        {},
        socket_msg["a"]["P"][2],
    )


def test_on_watch_BOTH(position_store, dummy_change_BOTH):
    position_store._on_watch(dummy_change_BOTH)
    assert len(position_store) == 1
    assert position_store.find()[0] == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "price": 20000.0,
        "size": 0.5,
        "ps": "BOTH",
        "info": {"data": dummy_change_BOTH.data, "source": {}},
    }


def test_on_watch_LONG(position_store, dummy_change_LONG):
    position_store._on_watch(dummy_change_LONG)
    assert len(position_store) == 1
    assert position_store.find()[0] == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "price": 6563.66500,
        "size": 20.0,
        "ps": "LONG",
        "info": {"data": dummy_change_LONG.data, "source": {}},
    }


def test_on_watch_SHORT(position_store, dummy_change_SHORT):
    position_store._on_watch(dummy_change_SHORT)
    assert len(position_store) == 1
    assert position_store.find()[0] == {
        "symbol": "BTCUSDT",
        "side": "SELL",
        "price": 6563.86000,
        "size": 10,
        "ps": "SHORT",
        "info": {"data": dummy_change_SHORT.data, "source": {}},
    }
