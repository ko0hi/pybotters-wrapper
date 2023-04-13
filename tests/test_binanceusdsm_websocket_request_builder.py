import pytest
import pytest_mock
from aioresponses import aioresponses

from pybotters_wrapper import create_client
from pybotters_wrapper.binance.binanceusdsm import (
    create_binanceusdsm_websocket_request_builder,
    create_binanceusdsm_websocket_request_customizer,
)
from pybotters_wrapper.core import WebSocketRequestBuilder


@pytest.fixture()
def builder() -> WebSocketRequestBuilder:
    return create_binanceusdsm_websocket_request_builder()


def test_binanceusdsm_websocket_request_builder_public(
    builder, mocker: pytest_mock.MockerFixture
):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = {
        "wss://fstream.binance.com/ws": [
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
        ]
    }
    subscribe_list = builder.subscribe("public", symbol=symbol).get()
    assert subscribe_list == expected


def test_binanceusdsm_websocket_request_builder_private(
    builder, mocker: pytest_mock.MockerFixture
):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = {
        "wss://fstream.binance.com/ws": [
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
        ]
    }
    actual = builder.subscribe("private", symbol=symbol).get()

    assert actual == expected


def test_binanceusdsm_websocket_request_builder_all(
    builder, mocker: pytest_mock.MockerFixture
):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = {
        "wss://fstream.binance.com/ws": [
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
        ]
    }

    actual = builder.subscribe("all", symbol=symbol).get()

    assert actual == expected


@pytest.mark.asyncio
async def test_binanceusdsm_websocket_builder_with_customizer(
    builder, mocker: pytest_mock.MockerFixture
):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    listen_key_url = "https://fapi.binance.com/fapi/v1/listenKey"
    listenkey_dummy_response = {
        "listenKey": "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1"
    }
    expected = {
        "wss://fstream.binance.com/ws": {
            "id": 1 * 10**9,
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@ticker",
                "btcusdt@aggTrade",
                "btcusdt@depth",
                "qgQWucD254wiYJQAyJIH0v54rNq77IG1szMjSfNelibNoOYwFHSolsNqLVdiubQX",
            ],
        },
    }
    async with create_client() as client:
        customizer = create_binanceusdsm_websocket_request_customizer()
        customizer.set_client(client)
        with aioresponses() as m:
            m.post(listen_key_url, payload=listenkey_dummy_response)

            actual = builder.subscribe("all", symbol=symbol).get(
                request_customizer=customizer
            )

            assert actual == expected
