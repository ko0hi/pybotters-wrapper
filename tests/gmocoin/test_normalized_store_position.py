import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(position_normalized_store_tester):
    store = pybotters.GMOCoinDataStore()
    store._onmessage(
        {
            "channel": "positionEvents",
            "positionId": 1234567,
            "symbol": "BTC_JPY",
            "side": "BUY",
            "size": "0.22",
            "orderdSize": "0",
            "price": "876045",
            "lossGain": "14",
            "leverage": "4",
            "losscutPrice": "766540",
            "timestamp": "2019-03-19T02:15:06.094Z",
            "msgType": "OPR",
        },
        None,
    )
    dummy_data = store.positions.find()[0]
    return position_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "gmocoin"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "symbol": "BTC_JPY",
            "side": "BUY",
            "price": 876045.0,
            "size": 0.22,
            "position_id": 1234567,
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
