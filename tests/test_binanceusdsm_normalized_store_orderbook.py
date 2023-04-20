import pytest
from pybotters.store import StoreChange

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)
from pybotters_wrapper.core import OrderbookStore


@pytest.fixture
def tester(orderbook_normalized_store_tester):
    dummy_data = {"s": "BTCUSDT", "S": "SELL", "p": "30895.10", "q": "0.015"}
    return orderbook_normalized_store_tester(
        builder_factory_method=create_binanceusdsm_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "symbol": "BTCUSDT",
            "side": "SELL",
            "price": 30895.10,
            "size": 0.015,
            "info": {"data": dummy_data, "source": {}},
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
