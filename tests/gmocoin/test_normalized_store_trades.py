import pandas as pd
import pybotters
import pytest
import pytest_mock

import pybotters_wrapper as pbw


@pytest.fixture
def tester(trades_normalized_store_tester, mocker: pytest_mock.MockerFixture):
    mocker.patch("uuid.uuid4", return_value="uuid")
    store = pybotters.GMOCoinDataStore()
    store._onmessage(
        {
            "channel": "trades",
            "price": "750760",
            "side": "BUY",
            "size": "0.1",
            "timestamp": "2018-03-30T12:34:56.789Z",
            "symbol": "BTC",
        },
        None,
    )
    dummy_data = store.trades.find()[0]
    return trades_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "gmocoin"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "id": "uuid",
            "symbol": "BTC",
            "side": "BUY",
            "price": 750760.0,
            "size": 0.1,
            "timestamp": pd.to_datetime("2018-03-30T12:34:56.789Z"),
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
