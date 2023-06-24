# mypy: ignore-errors
from typing import AsyncGenerator

import pytest
import pytest_asyncio
import pytest_mock

import pybotters
import pybotters_wrapper as pbw

from pybotters_wrapper.sandbox import SandboxEngine

EXCHANGE = "bitflyer"
SYMBOL = "FX_BTC_JPY"


@pytest.fixture
@pytest.mark.asyncio
async def client() -> pybotters.Client:
    return pbw.create_client()


@pytest_asyncio.fixture(autouse=True)
async def engine() -> AsyncGenerator[SandboxEngine, None]:
    async with pbw.create_client() as client:
        store, api = pbw.create_sandbox("bitflyer", client)
        yield store._engine


class TestCreateOrderItem:
    @pytest.fixture(autouse=True)
    def patch(self, mocker: pytest_mock.MockerFixture):
        mocker.patch("uuid.uuid4", return_value="uuid")
        mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:22")

    async def test_limit(self, engine: SandboxEngine):
        item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "LIMIT")
        assert {
            "id": "uuid",
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 10,
            "size": 1,
            "type": "LIMIT",
            "timestamp": "2022-02-22 02:22:22",
        } == item

    def test_market(self, engine: SandboxEngine):
        item = engine._create_order_item(SYMBOL, "BUY", 0, 1, "MARKET")
        assert {
            "id": "uuid",
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 0,
            "size": 1,
            "type": "MARKET",
            "timestamp": "2022-02-22 02:22:22",
        } == item

    def test_stop_limit(self, engine: SandboxEngine):
        item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "STOP_LIMIT", trigger=10)
        assert {
            "id": "uuid",
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 10,
            "size": 1,
            "type": "STOP_LIMIT",
            "timestamp": "2022-02-22 02:22:22",
            "trigger": 10,
        } == item

    def test_stop_market(self, engine: SandboxEngine):
        item = engine._create_order_item(SYMBOL, "BUY", 0, 1, "STOP_MARKET", trigger=10)
        assert {
            "id": "uuid",
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 0,
            "size": 1,
            "type": "STOP_MARKET",
            "timestamp": "2022-02-22 02:22:22",
            "trigger": 10,
        } == item

    def test_value_error_stop_limit_without_trigger(self, engine: SandboxEngine):
        with pytest.raises(ValueError):
            engine._create_order_item(SYMBOL, "BUY", 10, 1, "STOP_LIMIT")

    def test_value_error_stop_market_without_trigger(self, engine: SandboxEngine):
        with pytest.raises(ValueError):
            engine._create_order_item(SYMBOL, "BUY", 0, 1, "STOP_MARKET")


class TestCreateExecutionItem:
    @pytest.fixture(autouse=True)
    def patch(self, mocker: pytest_mock.MockerFixture):
        mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:23")
        mocker.patch(
            "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
            return_value=100,
        )

    def test_limit(self, engine: SandboxEngine):
        order_item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "LIMIT")
        execution_item = engine._create_execution_item(order_item)

        assert {
            "id": order_item["id"],
            "symbol": order_item["symbol"],
            "side": order_item["side"],
            "price": order_item["price"],
            "size": order_item["size"],
            "timestamp": "2022-02-22 02:22:23",
        } == execution_item

    def test_market(self, engine: SandboxEngine):
        order_item = engine._create_order_item(SYMBOL, "BUY", None, 1, "MARKET")
        execution_item = engine._create_execution_item(order_item)
        assert {
            "id": order_item["id"],
            "symbol": order_item["symbol"],
            "side": order_item["side"],
            "price": 100,
            "size": order_item["size"],
            "timestamp": "2022-02-22 02:22:23",
        } == execution_item

    def test_raise_value_error_with_stop_limit(self, engine: SandboxEngine):
        """Trigger時にLimitとして注文されるべき"""
        order_item = engine._create_order_item(
            SYMBOL, "BUY", 10, 1, "STOP_LIMIT", trigger=10
        )
        with pytest.raises(ValueError):
            engine._create_execution_item(order_item)

    def test_raise_value_error_with_stop_market(self, engine: SandboxEngine):
        """Trigger時にMarketとして注文されるべき"""
        order_item = engine._create_order_item(
            SYMBOL, "BUY", None, 1, "STOP_MARKET", trigger=10
        )
        with pytest.raises(ValueError):
            engine._create_execution_item(order_item)


class TestCreatePosition:
    def test_entry_long(self, engine: SandboxEngine):
        order_item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "LIMIT")
        execution_item = engine._create_execution_item(order_item)
        position_item = engine._create_position_item(execution_item)
        assert {
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 10,
            "size": 1.0,
        } == position_item

    def test_entry_short(self, engine: SandboxEngine):
        order_item = engine._create_order_item(SYMBOL, "SELL", 10, 1, "LIMIT")
        execution_item = engine._create_execution_item(order_item)
        position_item = engine._create_position_item(execution_item)
        assert {
            "symbol": SYMBOL,
            "side": "SELL",
            "price": 10,
            "size": 1.0,
        } == position_item


class TestComputePositionSideSizePrice:
    def _actual(self, engine: SandboxEngine, current_position, execution):
        side, size, price = engine._compute_position_side_size_price(
            current_position, execution
        )
        if side is not None:
            size = float(f"{size:.3f}")
            price = float(f"{price:.3f}")
        return side, size, price

    def test_add_long(self, engine: SandboxEngine):
        assert ("BUY", 2.000, 10.000) == self._actual(
            engine,
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 1.0, "price": 10.0},
        )

    def test_add_short(self, engine: SandboxEngine):
        assert ("SELL", 2.000, 10.000) == self._actual(
            engine,
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 1.0, "price": 10.0},
        )

    def test_add_long_with_different_price(self, engine: SandboxEngine):
        assert ("BUY", 2.000, 7.500) == self._actual(
            engine,
            {"side": "BUY", "size": 1.0, "price": 5.0},
            {"side": "BUY", "size": 1.0, "price": 10.0},
        )

    def test_add_short_with_different_price(self, engine: SandboxEngine):
        assert ("SELL", 2.000, 7.500) == self._actual(
            engine,
            {"side": "SELL", "size": 1.0, "price": 5.0},
            {"side": "SELL", "size": 1.0, "price": 10.0},
        )

    def test_add_long_with_different_size(self, engine: SandboxEngine):
        assert ("BUY", 1.500, 10.000) == self._actual(
            engine,
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 0.5, "price": 10.0},
        )

    def test_add_short_with_different_size(self, engine: SandboxEngine):
        assert ("SELL", 1.500, 10.000) == self._actual(
            engine,
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 0.5, "price": 10.0},
        )

    def test_add_long_with_different_price_and_size(self, engine: SandboxEngine):
        assert ("BUY", 1.500, 8.333) == self._actual(
            engine,
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 0.5, "price": 5.0},
        )

    def test_add_short_with_different_price_and_size(self, engine: SandboxEngine):
        assert ("SELL", 1.500, 8.333) == self._actual(
            engine,
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 0.5, "price": 5.0},
        )

    def test_reduce_long(self, engine: SandboxEngine):
        assert ("BUY", 0.500, 10.000) == self._actual(
            engine,
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 0.5, "price": 15.0},
        )

    def test_reduce_short(self, engine: SandboxEngine):
        assert ("SELL", 0.500, 10.000) == self._actual(
            engine,
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 0.5, "price": 15.0},
        )

    def test_clear_long(self, engine: SandboxEngine):
        assert (None, None, None) == self._actual(
            engine,
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 1.0, "price": 15.0},
        )

    def test_clear_short(self, engine: SandboxEngine):
        assert (None, None, None) == self._actual(
            engine,
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 1.0, "price": 15.0},
        )

    def test_reverse_long(self, engine: SandboxEngine):
        assert ("SELL", 0.5, 15.000) == self._actual(
            engine,
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 1.5, "price": 15.0},
        )

    def test_reverse_short(self, engine: SandboxEngine):
        assert ("BUY", 0.5, 15.000) == self._actual(
            engine,
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 1.5, "price": 15.0},
        )


def test_insert_limit_order(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    id = engine.insert_order(SYMBOL, "BUY", 10, 1, "LIMIT")
    assert "uuid" == id
    assert 1 == len(
        engine._store.order.find(
            {
                "id": "uuid",
                "symbol": SYMBOL,
                "side": "BUY",
                "price": 10,
                "size": 1,
                "type": "LIMIT",
            }
        )
    )


def test_delete_order(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    id = engine.insert_order(SYMBOL, "BUY", 10, 1, "LIMIT")
    assert 1 == len(engine._store.order.find({"id": id}))
    engine.delete_order(SYMBOL, id)
    assert 0 == len(engine._store.order.find({"id": id}))


class TestIsExecuted:
    def test_buy(self, engine: SandboxEngine):
        order_item = {"symbol": "a", "price": 10, "side": "BUY"}
        assert engine._is_executed(order_item, {"symbol": "a", "price": 9})
        assert engine._is_executed(order_item, {"symbol": "a", "price": 10})
        assert not engine._is_executed(order_item, {"symbol": "a", "price": 11})
        assert not engine._is_executed(order_item, {"symbol": "b", "price": 9})

    def test_sell(self, engine: SandboxEngine):
        order_item = {"symbol": "a", "price": 10, "side": "SELL"}
        assert not engine._is_executed(order_item, {"symbol": "a", "price": 9})
        assert engine._is_executed(order_item, {"symbol": "a", "price": 10})
        assert engine._is_executed(order_item, {"symbol": "a", "price": 11})
        assert not engine._is_executed(order_item, {"symbol": "b", "price": 11})


class TestIsTriggered:
    def test_buy(self, engine: SandboxEngine):
        order_item = {
            "symbol": "a",
            "price": 10,
            "side": "BUY",
            "trigger": 10,
            "type": "STOP_LIMIT",
        }
        assert not engine._is_triggered(order_item, {"symbol": "a", "price": 9})
        assert engine._is_triggered(order_item, {"symbol": "a", "price": 10})
        assert engine._is_triggered(order_item, {"symbol": "a", "price": 11})
        assert not engine._is_triggered(order_item, {"symbol": "b", "price": 11})

    def test_sell(self, engine: SandboxEngine):
        order_item = {
            "symbol": "a",
            "price": 10,
            "side": "SELL",
            "trigger": 10,
            "type": "STOP_LIMIT",
        }
        assert not engine._is_triggered(order_item, {"symbol": "a", "price": 11})
        assert engine._is_triggered(order_item, {"symbol": "a", "price": 10})
        assert engine._is_triggered(order_item, {"symbol": "a", "price": 9})
        assert not engine._is_triggered(order_item, {"symbol": "b", "price": 9})


def test__handle_execution(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:23")

    store = engine._store
    order_id = engine.insert_order(SYMBOL, "BUY", 10, 1, "LIMIT")

    assert 1 == len(store.order)

    order_item = store.order.find({"id": order_id})[0]
    engine._handle_execution(order_item)

    assert 1 == len(store.execution)
    assert {
        "id": "uuid",
        "symbol": SYMBOL,
        "side": "BUY",
        "size": 1,
        "price": 10,
        "timestamp": "2022-02-22 02:22:23",
    } == store.execution.find()[0]
    assert 1 == len(store.position)
    assert {
        "symbol": SYMBOL,
        "side": "BUY",
        "size": 1,
        "price": 10,
    } == store.position.find()[0]

    assert 0 == len(store.order)


def test_handle_trigger_limit(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:23")

    store = engine._store
    order_id = engine.insert_order(SYMBOL, "BUY", 10, 1, "STOP_LIMIT", trigger=11)

    assert 1 == len(store.order.find({"trigger": 11}))

    order_item = store.order.find({"id": order_id})[0]
    engine._handle_trigger(order_item)

    assert 0 == len(store.execution)
    assert 0 == len(store.order.find({"trigger": 11}))
    assert 1 == len(store.order.find({"id": order_id}))


def test_engine_handle_trigger_market(
    engine: SandboxEngine,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:23")
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )
    store = engine._store
    order_id = engine.insert_order(SYMBOL, "BUY", 10, 1, "STOP_MARKET", trigger=11)

    assert 1 == len(store.order.find({"trigger": 11}))

    order_item = store.order.find({"id": order_id})[0]
    engine._handle_trigger(order_item)

    assert 1 == len(store.execution)
    assert {
        "id": "uuid",
        "symbol": SYMBOL,
        "side": "BUY",
        "size": 1,
        "price": 10,
        "timestamp": "2022-02-22 02:22:23",
    } == store.execution.find()[0]
    assert 1 == len(store.position)
    assert {
        "symbol": SYMBOL,
        "side": "BUY",
        "size": 1,
        "price": 10,
    } == store.position.find()[0]
    assert 0 == len(store.order)
