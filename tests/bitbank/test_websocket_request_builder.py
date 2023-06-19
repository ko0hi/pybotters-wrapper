import pytest

import pybotters_wrapper as pbw
from pybotters_wrapper.core import WebsocketRequest


@pytest.fixture
def public_send() -> list[str]:
    return [
        '42["join-room","ticker_btc_jpy"]',
        '42["join-room","transactions_btc_jpy"]',
        '42["join-room","depth_whole_btc_jpy"]',
    ]


def test_public(public_send):
    expected = [
        WebsocketRequest(
            "wss://stream.bitbank.cc/socket.io/?EIO=2&transport=websocket",
            public_send,
        )
    ]

    actual = (
        pbw.create_factory("bitbank")
        .create_websocket_request_builder()
        .subscribe("public", symbol="btc_jpy")
        .get()
    )

    assert expected == actual


@pytest.mark.asyncio
async def test_private():
    with pytest.raises(NotImplementedError):
        (
            pbw.create_factory("bitbank")
            .create_websocket_request_builder()
            .subscribe("private", symbol="btc_jpy")
            .get()
        )


@pytest.mark.asyncio
async def test_all():
    with pytest.raises(NotImplementedError):
        (
            pbw.create_factory("bitbank")
            .create_websocket_request_builder()
            .subscribe("all", symbol="btc_jpy")
            .get()
        )
