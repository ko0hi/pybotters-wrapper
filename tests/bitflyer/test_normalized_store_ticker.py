import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.fixture
def tester(ticker_normalized_store_tester):
    store = pybotters.bitFlyerDataStore()
    store.onmessage(
        {
            "jsonrpc": "2.0",
            "method": "channelMessage",
            "params": {
                "channel": "lightning_ticker_FX_BTC_JPY",
                "message": {
                    "product_code": "FX_BTC_JPY",
                    "state": "RUNNING",
                    "timestamp": "2023-06-11T17:33:32.0083477Z",
                    "tick_id": 75652844,
                    "best_bid": 3688135.0,
                    "best_ask": 3689125.0,
                    "best_bid_size": 0.01,
                    "best_ask_size": 0.02,
                    "total_bid_depth": 273.2022358,
                    "total_ask_depth": 187.22649895,
                    "market_bid_size": 0.0,
                    "market_ask_size": 0.0,
                    "ltp": 3688335.0,
                    "volume": 1212.90516703,
                    "volume_by_product": 1212.90516703,
                    "preopen_end": None,
                    "circuit_break_end": None,
                },
            },
        },
        None,
    )
    dummy_data = store.ticker.find()[0]

    return ticker_normalized_store_tester(
        builder_factory_method=pbw.create_factory(
            "bitflyer"
        ).create_normalized_store_builder,
        dummy_data=dummy_data,
        expected_item={
            "symbol": "FX_BTC_JPY",
            "price": 3688335.0,
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
