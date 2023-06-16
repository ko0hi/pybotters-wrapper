import pytest

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def tester(orderbook_normalized_store_tester):
    dummy_data = {"s": "BTCUSD_PERP", "S": "BUY", "p": "29516.9", "q": "181"}
    return orderbook_normalized_store_tester(
        builder_factory_method=BinanceCOINMWrapperFactory.create_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "symbol": "BTCUSD_PERP",
            "side": "BUY",
            "price": 29516.9,
            "size": 181.0,
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
