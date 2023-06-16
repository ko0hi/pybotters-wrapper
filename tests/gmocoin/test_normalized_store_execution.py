import pandas as pd
import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(execution_normalized_store_tester):
    store = pybotters.GMOCoinDataStore()
    store._onmessage(
        {
            "channel": "executionEvents",
            "orderId": 123456789,
            "executionId": 72123911,
            "symbol": "BTC_JPY",
            "settleType": "OPEN",
            "executionType": "LIMIT",
            "side": "BUY",
            "executionPrice": "877404",
            "executionSize": "0.5",
            "positionId": 123456789,
            "orderTimestamp": "2019-03-19T02:15:06.081Z",
            "executionTimestamp": "2019-03-19T02:15:06.081Z",
            "lossGain": "0",
            "fee": "323",
            "orderPrice": "877200",
            "orderSize": "0.8",
            "orderExecutedSize": "0.7",
            "timeInForce": "FAS",
            "msgType": "ER",
        },
        None,
    )
    dummy_data = store.executions.find()[0]
    return execution_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "gmocoin"
        ).create_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "id": "123456789",
            "symbol": "BTC_JPY",
            "side": "BUY",
            "price": 877404,
            "size": 0.5,
            "timestamp": pd.to_datetime("2019-03-19T02:15:06.081Z"),
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


