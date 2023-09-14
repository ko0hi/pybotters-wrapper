import pytest
import pytest_mock

import pybotters_wrapper as pbw
from pybotters_wrapper.core import WebsocketRequest


@pytest.fixture
def patch_time(mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)


@pytest.fixture
def patch_token(mocker: pytest_mock.MockerFixture):
    mocker.patch(
        "pybotters_wrapper.gmocoin.token_fetcher.GMOCoinTokenFetcher.fetch",
        return_value="xxxxx",
    )


@pytest.fixture
def public_expected() -> list[dict]:
    return [
        {"command": "subscribe", "channel": "ticker", "symbol": "BTC_JPY"},
        {
            "command": "subscribe",
            "channel": "trades",
            "symbol": "BTC_JPY",
            "option": "TAKER_ONLY",
        },
        {"command": "subscribe", "channel": "orderbooks", "symbol": "BTC_JPY"},
    ]


@pytest.fixture
def private_expected() -> list[dict[str, str]]:
    return [
        {"command": "subscribe", "channel": "orderEvents"},
        {"command": "subscribe", "channel": "executionEvents"},
        {
            "command": "subscribe",
            "channel": "positionEvents",
        },
    ]


def test_public(public_expected):
    expected = [
        WebsocketRequest(
            "wss://api.coin.z.com/ws/public/v1",
            public_expected,
        )
    ]

    actual = (
        pbw.create_factory("gmocoin")
        .create_websocket_request_builder()
        .subscribe("public", symbol="BTC_JPY")
        .get()
    )

    assert expected == actual


@pytest.mark.asyncio
async def test_private(patch_token, private_expected):
    expected = [
        WebsocketRequest(
            "wss://api.coin.z.com/ws/private/v1/xxxxx",
            private_expected,
        )
    ]

    async with pbw.create_client() as client:
        factory = pbw.create_factory("gmocoin")

        actual = (
            factory.create_websocket_request_builder()
            .subscribe("private", symbol="BTC_JPY")
            .get(
                request_customizer=(
                    factory.create_websocket_request_customizer().set_client(client)
                )
            )
        )

        assert expected == actual


@pytest.mark.asyncio
async def test_all(patch_token, public_expected, private_expected):
    expected = [
        WebsocketRequest(
            "wss://api.coin.z.com/ws/public/v1",
            public_expected,
        ),
        WebsocketRequest(
            "wss://api.coin.z.com/ws/private/v1/xxxxx",
            private_expected,
        ),
    ]

    async with pbw.create_client() as client:
        factory = pbw.create_factory("gmocoin")

        actual = (
            factory.create_websocket_request_builder()
            .subscribe("all", symbol="BTC_JPY")
            .get(
                request_customizer=(
                    factory.create_websocket_request_customizer().set_client(client)
                )
            )
        )

    assert expected == actual
