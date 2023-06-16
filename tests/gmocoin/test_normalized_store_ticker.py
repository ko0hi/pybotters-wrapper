import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(ticker_normalized_store_tester):
    store = pybotters.GMOCoinDataStore()
    store._onmessage(
        {
            "channel": "ticker",
            "ask": "750760",
            "bid": "750600",
            "high": "762302",
            "last": "756662",
            "low": "704874",
            "symbol": "BTC",
            "timestamp": "2018-03-30T12:34:56.789Z",
            "volume": "194785.8484",
        },
        None,
    )
    dummy_data = store.ticker.find()[0]
    return ticker_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "gmocoin"
        ).create_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "symbol": "BTC",
            "price": 756662.0,
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
