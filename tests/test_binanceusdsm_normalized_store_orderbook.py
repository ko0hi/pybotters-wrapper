import pytest
from pybotters.store import StoreChange

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)
from pybotters_wrapper.core import OrderbookStore


@pytest.fixture
def orderbook_store() -> OrderbookStore:
    return create_binanceusdsm_normalized_store_builder().get("orderbook")


@pytest.fixture
def dummy_change_update_btc() -> StoreChange:
    return StoreChange(
        None,
        "update",
        {},
        {"s": "BTCUSDT", "S": "SELL", "p": "30895.10", "q": "0.015"},
    )


@pytest.fixture
def dummy_change_delete_btc() -> StoreChange:
    return StoreChange(
        None,
        "delete",
        {},
        {"s": "BTCUSDT", "S": "SELL", "p": "30895.10", "q": "0.015"},
    )


def test_normalized_store_ticker_binanceusdsm_on_watch_update(
    orderbook_store, dummy_change_update_btc
):
    orderbook_store._on_watch(dummy_change_update_btc)
    assert len(orderbook_store) == 1
    assert orderbook_store.find()[0] == {
        "symbol": "BTCUSDT",
        "side": "SELL",
        "price": 30895.1,
        "size": 0.015,
        "info": {"data": dummy_change_update_btc.data, "source": {}},
    }


def test_normalized_store_ticker_binanceusdsm_on_watch_delete(
    orderbook_store, dummy_change_update_btc, dummy_change_delete_btc
):
    orderbook_store._on_watch(dummy_change_update_btc)
    orderbook_store._on_watch(dummy_change_delete_btc)
    assert len(orderbook_store) == 0
