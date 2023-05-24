import pytest
import pytest_mock

from pybotters_wrapper.core import WebsocketRequest
from pybotters_wrapper.bitflyer import bitFlyerWrapperFactory


@pytest.fixture
def patch_time(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)


@pytest.fixture
def public_expected() -> dict:
    return [
        {
            "method": "subscribe",
            "params": {
                "channel": "lightning_ticker_FX_BTC_JPY",
                "id": 1000000000,
            },
        },
        {
            "method": "subscribe",
            "params": {
                "channel": "lightning_executions_FX_BTC_JPY",
                "id": 1000000000,
            },
        },
        {
            "method": "subscribe",
            "params": {
                "channel": "lightning_board_FX_BTC_JPY",
                "id": 1000000000,
            },
        },
        {
            "method": "subscribe",
            "params": {
                "channel": "lightning_board_snapshot_FX_BTC_JPY",
                "id": 1000000000,
            },
        },
    ]


@pytest.fixture
def private_expected() -> dict:
    return [
        {
            "method": "subscribe",
            "params": {"channel": "child_order_events", "id": 1000000000},
        },
        {
            "method": "subscribe",
            "params": {"channel": "child_order_events", "id": 1000000000},
        },
        {
            "method": "subscribe",
            "params": {"channel": "child_order_events", "id": 1000000000},
        },
    ]


def test_public(patch_time, public_expected):
    expected = [
        WebsocketRequest(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            public_expected,
        )
    ]

    actual = (
        bitFlyerWrapperFactory.create_websocket_request_builder()
        .subscribe("public", symbol="FX_BTC_JPY")
        .get()
    )

    assert expected == actual


def test_private(patch_time, private_expected):
    expected = [
        WebsocketRequest(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            private_expected,
        )
    ]

    actual = (
        bitFlyerWrapperFactory.create_websocket_request_builder()
        .subscribe("private", symbol="FX_BTC_JPY")
        .get()
    )

    assert expected == actual


def test_all(patch_time, public_expected, private_expected):
    expected = [
        WebsocketRequest(
            "wss://ws.lightstream.bitflyer.com/json-rpc",
            public_expected + private_expected,
        )
    ]

    actual = (
        bitFlyerWrapperFactory.create_websocket_request_builder()
        .subscribe("all", symbol="FX_BTC_JPY")
        .get()
    )

    assert expected == actual
