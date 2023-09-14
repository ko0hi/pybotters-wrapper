import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(ticker_normalized_store_tester):
    store = pybotters.bitbankDataStore()
    store._onmessage(
        """42["message",{"room_name":"ticker_btc_jpy","message":{"data":{"sell":"3788372","buy":"3787616","open":"3747147","high":"3832258","low":"3725036","last":"3787616","vol":"296.9391","timestamp":1687210959113}}}]""",
        None,
    )
    dummy_data = store.ticker.find()[0]
    return ticker_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "bitbank"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "symbol": "btc_jpy",
            "price": 3787616.0,
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
