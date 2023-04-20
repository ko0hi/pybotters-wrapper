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
def socket_msg() -> dict:
    return {
        "e": "ACCOUNT_UPDATE",
        "E": 1564745798939,
        "T": 1564745798938,
        "a": {
            "m": "ORDER",
            "B": [
                {
                    "a": "USDT",
                    "wb": "122624.12345678",
                    "cw": "100.12345678",
                    "bc": "50.12345678",
                },
                {
                    "a": "BUSD",
                    "wb": "1.00000000",
                    "cw": "0.00000000",
                    "bc": "-49.12345678",
                },
            ],
            "P": [
                {
                    "s": "BTCUSDT",
                    "pa": "0.5",
                    "ep": "20000",
                    "cr": "200",
                    "up": "0",
                    "mt": "isolated",
                    "iw": "0.00000000",
                    "ps": "BOTH",
                },
                {
                    "s": "BTCUSDT",
                    "pa": "20",
                    "ep": "6563.66500",
                    "cr": "0",
                    "up": "2850.21200",
                    "mt": "isolated",
                    "iw": "13200.70726908",
                    "ps": "LONG",
                },
                {
                    "s": "BTCUSDT",
                    "pa": "-10",
                    "ep": "6563.86000",
                    "cr": "-45.04000000",
                    "up": "-1423.15600",
                    "mt": "isolated",
                    "iw": "6570.42511771",
                    "ps": "SHORT",
                },
            ],
        },
    }


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
