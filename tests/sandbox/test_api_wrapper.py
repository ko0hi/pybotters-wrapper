from typing import AsyncGenerator

import pytest
import pytest_asyncio
import pytest_mock

import pybotters_wrapper as pbw
from pybotters_wrapper.sandbox import SandboxEngine

EXCHANGE = "binanceusdsm"
SYMBOL = "BTCUSDT"


@pytest_asyncio.fixture(autouse=True)
async def engine() -> AsyncGenerator[SandboxEngine, None]:
    async with pbw.create_client() as client:
        store, api = pbw.create_sandbox(EXCHANGE, client)
        yield store._engine


@pytest.mark.asyncio
async def test_api_limit_order(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")

    api = engine._api
    store = engine._store

    resp = await api.limit_order(SYMBOL, "BUY", 10, 1)
    assert "uuid" == resp.order_id
    assert 200 == resp.resp.status
    assert 1 == len(store.order.find({"id": resp.order_id}))


@pytest.mark.asyncio
async def test_api_market_order(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )
    api = engine._api
    store = engine._store

    resp = await api.market_order(SYMBOL, "BUY", 1)

    assert "uuid" == resp.order_id
    assert 200 == resp.resp.status
    assert 0 == len(store.order.find({"id": resp.order_id}))
    assert 1 == len(store.execution.find({"id": resp.order_id}))
    assert 1 == len(store.position.find({"side": "BUY"}))
    assert 10 == store.position.find()[0]["price"]


@pytest.mark.asyncio
async def test_api_stop_limit_order(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")

    api = engine._api
    store = engine._store

    resp = await api.stop_limit_order(SYMBOL, "BUY", 10, 1, 10)
    assert "uuid" == resp.order_id
    assert 200 == resp.resp.status
    assert 1 == len(store.order.find({"id": resp.order_id, "trigger": 10}))


@pytest.mark.asyncio
async def test_api_stop_market_order(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )

    api = engine._api
    store = engine._store

    resp = await api.stop_market_order(SYMBOL, "BUY", 10, 1)
    assert "uuid" == resp.order_id
    assert 200 == resp.resp.status
    assert 1 == len(store.order.find({"id": resp.order_id}))
    assert 0 == len(store.execution.find({"id": resp.order_id}))
    assert 0 == len(store.position.find({"side": "BUY"}))


@pytest.mark.asyncio
async def test_api_cancel_order_200(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")

    api = engine._api
    store = engine._store

    order_resp = await api.limit_order(SYMBOL, "BUY", 10, 1)
    cancel_resp = await api.cancel_order(SYMBOL, order_resp.order_id)

    assert "uuid" == cancel_resp.order_id
    assert 200 == cancel_resp.resp.status
    assert 0 == len(store.order.find({"id": cancel_resp.order_id}))


@pytest.mark.asyncio
async def test_api_cancel_order_500(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )

    api = engine._api
    store = engine._store

    order_resp = await api.market_order(SYMBOL, "BUY", 10)
    cancel_resp = await api.cancel_order(SYMBOL, order_resp.order_id)

    assert "uuid" == cancel_resp.order_id
    assert 500 == cancel_resp.resp.status
    assert 0 == len(store.order.find({"id": cancel_resp.order_id}))


@pytest.mark.asyncio
async def test_store_position(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )

    store = engine._store
    api = engine._api

    await api.market_order(SYMBOL, "BUY", 10)

    assert 1 == len(store.position)

    await api.market_order(SYMBOL, "SELL", 10)

    assert 0 == len(store.position)


@pytest.mark.asyncio
async def test_store_position_with_multiple_symbols(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )

    api = engine._api
    store = engine._store

    await api.market_order("A", "BUY", 10)
    assert 1 == len(store.position)

    await api.market_order("B", "BUY", 10)
    assert 2 == len(store.position)

    await api.market_order("A", "SELL", 10)
    assert 1 == len(store.position)
    assert "BUY" == store.position.find()[0]["side"]
