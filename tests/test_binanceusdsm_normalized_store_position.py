import pytest

from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_normalized_store_builder,
)


@pytest.fixture
def tester(position_normalized_store_tester):
    dummy_data = {
        "s": "BTCUSDT",
        "pa": "0.5",
        "ep": "20000",
        "cr": "200",
        "up": "0",
        "mt": "isolated",
        "iw": "0.00000000",
        "ps": "BOTH",
    }
    return position_normalized_store_tester(
        builder_factory_method=create_binanceusdsm_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": 20000.0,
            "size": 0.5,
            "ps": "BOTH",
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
