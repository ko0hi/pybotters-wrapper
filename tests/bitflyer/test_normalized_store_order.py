import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(order_normalized_store_tester):
    dummy_data = {
        "product_code": "FX_BTC_JPY",
        "child_order_id": "JFX20230611-180201-440296F",
        "child_order_acceptance_id": "JRF20230611-180201-097176",
        "event_date": "2023-06-11T18:02:01.6573082Z",
        "event_type": "ORDER",
        "child_order_type": "LIMIT",
        "side": "BUY",
        "price": 3000000,
        "size": 0.01,
        "expire_date": "2023-07-11T18:02:01",
    }
    return order_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "bitflyer"
        ).create_normalized_store_builder,
        dummy_data_insert=dummy_data,
        dummy_data_update=dummy_data,
        dummy_data_delete=dummy_data,
        expected_item={
            "id": "JRF20230611-180201-097176",
            "symbol": "FX_BTC_JPY",
            "side": "BUY",
            "price": 3000000.0,
            "size": 0.01,
            "type": "LIMIT",
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
