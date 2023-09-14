import pandas as pd
import pybotters
import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(trades_normalized_store_tester, mocker: pytest_mock.MockerFixture):
    store = pybotters.bitbankDataStore()
    store._onmessage(
        """42["message",{"room_name":"transactions_btc_jpy","message":{"data":{"transactions":[{"transaction_id":1138669992,"side":"buy","price":"3760955","amount":"0.0005","executed_at":1687098591164}]}}}]""",
        None,
    )
    dummy_data = store.transactions.find()[0]
    return trades_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "bitbank"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "id": "1138669992",
            "symbol": "btc_jpy",
            "side": "BUY",
            "price": 3760955.0,
            "size": 0.0005,
            "timestamp": pd.to_datetime(1687098591164, unit="ms", utc=True),
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
