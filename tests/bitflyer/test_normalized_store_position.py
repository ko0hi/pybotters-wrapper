import pandas as pd
import pytest_mock
from pybotters.store import StoreChange

import pybotters_wrapper as pbw


def test_ignore_non_execution_event(mocker: pytest_mock.MockerFixture):
    # positionストアは特殊なので
    store = pbw.create_factory("bitflyer").create_normalized_store_builder().position()

    dummy_data1 = {
        "product_code": "FX_BTC_JPY",
        "side": "BUY",
        "size": 0.01,
        "price": 3000000,
        "timestamp": pd.to_datetime("2022-08-09T13:17:31.3350519Z"),
        "commission": 0,
        "sfd": 0,
    }
    dummy_data2 = {
        "product_code": "FX_BTC_JPY",
        "side": "BUY",
        "size": 0.01,
        "price": 2000000,
        "timestamp": pd.to_datetime("2022-08-09T13:17:31.3350519Z"),
        "commission": 0,
        "sfd": 0,
    }
    expected = [
        {
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "price": 3000000.0,
            "size": 0.01,
            "product_code": "FX_BTC_JPY",
            "commission": 0,
            "sfd": 0,
            "info": {"data": dummy_data1, "source": {}},
        },
        {
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "price": 2000000.0,
            "size": 0.01,
            "product_code": "FX_BTC_JPY",
            "commission": 0,
            "sfd": 0,
            "info": {"data": dummy_data2, "source": {}},
        },
    ]
    mocker.patch(
        "pybotters.models.bitflyer.Positions.find",
        return_value=[dummy_data1, dummy_data2],
    )

    store._on_watch(StoreChange(store._base_store, "insert", {}, {}))

    assert len(store) == 2
    assert store.find() == expected
