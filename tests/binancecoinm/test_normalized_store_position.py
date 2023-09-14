import pytest

from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory


@pytest.fixture
def tester(position_normalized_store_tester):
    dummy_data = {
        "s": "ETHUSD_PERP",
        "pa": "1600",
        "ep": "1910.53",
        "cr": "0.13720477",
        "up": "0.67016326",
        "mt": "cross",
        "iw": "0",
        "ps": "BOTH",
        "ma": "ETH",
    }
    return position_normalized_store_tester(
        builder_factory_method=BinanceCOINMWrapperFactory.create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "symbol": "ETHUSD_PERP",
            "side": "BUY",
            "price": 1910.53,
            "size": 1600.0,
            "ps": "BOTH",
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
