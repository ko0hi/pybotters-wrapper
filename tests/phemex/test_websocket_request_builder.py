import pytest
import pytest_mock

from pybotters_wrapper.core import WebsocketRequest
from pybotters_wrapper.phemex import PhemexWrapperFactory


@pytest.fixture
def patch_time(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)


def test_public_channels(patch_time):
    expected = [
        WebsocketRequest(
            "wss://phemex.com/ws",
            [
                {
                    "id": 1 * 10**9,
                    "method": "tick.subscribe",
                    "params": [".BTC"],
                },
                {
                    "id": 1 * 10**9,
                    "method": "trade.subscribe",
                    "params": ["BTCUSD"],
                },
                {
                    "id": 1 * 10**9,
                    "method": "orderbook.subscribe",
                    "params": ["BTCUSD", True],
                },
            ],
        )
    ]

    builder = PhemexWrapperFactory.create_websocket_request_builder()
    actual = builder.subscribe("public", symbol="BTCUSD").get()

    assert expected == actual
