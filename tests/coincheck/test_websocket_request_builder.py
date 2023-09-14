import pytest

import pybotters_wrapper as pbw
from pybotters_wrapper.core import WebsocketRequest


@pytest.fixture
def public_send() -> list[dict]:
    return [
        {"channel": "btc_jpy-trades", "type": "subscribe"},
        {"channel": "btc_jpy-trades", "type": "subscribe"},
        {"channel": "btc_jpy-orderbook", "type": "subscribe"},
    ]


def test_public(public_send):
    expected = [
        WebsocketRequest(
            "wss://ws-api.coincheck.com/",
            public_send,
        )
    ]

    actual = (
        pbw.create_factory("coincheck")
        .create_websocket_request_builder()
        .subscribe("public", symbol="btc_jpy")
        .get()
    )

    assert expected == actual


@pytest.mark.asyncio
async def test_private():
    with pytest.raises(NotImplementedError):
        (
            pbw.create_factory("coincheck")
            .create_websocket_request_builder()
            .subscribe("private", symbol="btc_jpy")
            .get()
        )


@pytest.mark.asyncio
async def test_all():
    with pytest.raises(NotImplementedError):
        (
            pbw.create_factory("coincheck")
            .create_websocket_request_builder()
            .subscribe("all", symbol="btc_jpy")
            .get()
        )
