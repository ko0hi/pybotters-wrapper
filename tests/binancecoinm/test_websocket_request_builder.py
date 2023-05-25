import pytest
import pytest_mock

from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binancecoinm import BinanceCOINMWrapperFactory
from pybotters_wrapper.core import WebsocketRequest, WebSocketRequestBuilder


@pytest.fixture
def builder() -> WebSocketRequestBuilder:
    return BinanceCOINMWrapperFactory.create_websocket_request_builder()


@pytest.fixture
def customizer():
    return BinanceCOINMWrapperFactory.create_websocket_request_customizer()


def test_public(builder, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = [
        WebsocketRequest(
            "wss://dstream.binance.com/ws",
            [
                {
                    "method": "SUBSCRIBE",
                    "params": ["btcusdt@ticker"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["btcusdt@aggTrade"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["btcusdt@depth"],
                    "id": 1 * 10**9,
                },
            ],
        )
    ]
    subscribe_list = builder.subscribe("public", symbol=symbol).get()
    assert subscribe_list == expected


def test_private(builder, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = [
        WebsocketRequest(
            "wss://dstream.binance.com/ws",
            [
                {
                    "method": "SUBSCRIBE",
                    "params": ["[LISTEN_KEY]"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["[LISTEN_KEY]"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["[LISTEN_KEY]"],
                    "id": 1 * 10**9,
                },
            ],
        )
    ]
    actual = builder.subscribe("private", symbol=symbol).get()

    assert actual == expected


def test_all(builder, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = [
        WebsocketRequest(
            "wss://dstream.binance.com/ws",
            [
                {
                    "method": "SUBSCRIBE",
                    "params": ["btcusdt@ticker"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["btcusdt@aggTrade"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["btcusdt@depth"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["[LISTEN_KEY]"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["[LISTEN_KEY]"],
                    "id": 1 * 10**9,
                },
                {
                    "method": "SUBSCRIBE",
                    "params": ["[LISTEN_KEY]"],
                    "id": 1 * 10**9,
                },
            ],
        )
    ]

    actual = builder.subscribe("all", symbol=symbol).get()

    assert actual == expected


@pytest.mark.asyncio
async def test_binancecoinm_websocket_builder_with_customizer(
    builder, customizer, mocker: pytest_mock.MockerFixture
):
    mocker.patch("time.monotonic", return_value=1)
    mocker.patch(
        "pybotters_wrapper.binance.listenkey_fetcher.BinanceListenKeyFetcher.get_listenkey",
        return_value="pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1",
    )
    symbol = "BTCUSDT"
    expected = [
        WebsocketRequest(
            "wss://dstream.binance.com/ws",
            {
                "id": 1 * 10**9,
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@ticker",
                    "btcusdt@aggTrade",
                    "btcusdt@depth",
                    "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1",
                ],
            },
        )
    ]
    async with create_client() as client:
        customizer.set_client(client)
        actual = builder.subscribe("all", symbol=symbol).get(
            request_customizer=customizer
        )

        assert actual == expected
