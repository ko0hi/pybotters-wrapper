import pandas as pd
import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(order_normalized_store_tester):
    store = pybotters.GMOCoinDataStore()
    store._onmessage(
        {
            "channel": "orderEvents",
            "orderId": 123456789,
            "symbol": "BTC_JPY",
            "settleType": "OPEN",
            "executionType": "LIMIT",
            "side": "BUY",
            "orderStatus": "ORDERED",
            "orderTimestamp": "2019-03-19T02:15:06.081Z",
            "orderPrice": "876045",
            "orderSize": "0.8",
            "orderExecutedSize": "0",
            "losscutPrice": "0",
            "timeInForce": "FAS",
            "msgType": "NOR",
        },
        None,
    )
    dummy_data = store.orders.find()[0]
    return order_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "gmocoin"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "id": "123456789",
            "symbol": "BTC_JPY",
            "side": "BUY",
            "price": 876045.0,
            "size": 0.8,
            "type": "LIMIT",
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
