import unittest

import pytest
import pytest_mock

import pybotters
import pybotters_wrapper as pbw

EXCHANGE = "bitflyer"
SYMBOL = "FX_BTC_JPY"


@pytest.fixture
def engine():
    store, api = pbw.create_sandbox(EXCHANGE, pbw.create_client())
    return store._engine


@pytest.mark.asyncio
async def test_engine_create_order_item(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:22")
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "LIMIT")
    testcase.assertEqual(item["id"], "uuid")
    testcase.assertEqual(item["timestamp"], "2022-02-22 02:22:22")
    testcase.assertEqual(0, len(store.order))


@pytest.mark.asyncio
async def test_engine_create_execution_item_limit(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:23")
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "LIMIT")
    execution_item = engine._create_execution_item(order_item)

    testcase.assertDictEqual(
        {
            "id": order_item["id"],
            "symbol": order_item["symbol"],
            "side": order_item["side"],
            "price": order_item["price"],
            "size": order_item["size"],
            "timestamp": "2022-02-22 02:22:23",
        },
        execution_item,
    )


@pytest.mark.asyncio
async def test_engine_create_execution_item_market(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:23")
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=100,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "BUY", None, 1, "MARKET")
    execution_item = engine._create_execution_item(order_item)
    testcase.assertDictEqual(
        {
            "id": order_item["id"],
            "symbol": order_item["symbol"],
            "side": order_item["side"],
            "price": 100,
            "size": order_item["size"],
            "timestamp": "2022-02-22 02:22:23",
        },
        execution_item,
    )


@pytest.mark.asyncio
async def test_engine_compute_side_size_price(
    testcase: unittest.TestCase,
    client: pybotters.Client,
):
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine

    def _actual(position, execution):
        side, size, price = engine._compute_side_size_price(position, execution)
        if side is not None:
            size = float(f"{size:.3f}")
            price = float(f"{price:.3f}")
        return side, size, price

    testcase.assertEqual(
        ("BUY", 2.000, 10.000),
        _actual(
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 1.0, "price": 10.0},
        ),
        msg="BUY追加",
    )
    testcase.assertEqual(
        ("SELL", 2.000, 10.000),
        _actual(
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 1.0, "price": 10.0},
        ),
        msg="SELL追加",
    )

    testcase.assertEqual(
        ("BUY", 2.000, 7.500),
        _actual(
            {"side": "BUY", "size": 1.0, "price": 5.0},
            {"side": "BUY", "size": 1.0, "price": 10.0},
        ),
        msg="BUY追加 - different price",
    )
    testcase.assertEqual(
        ("SELL", 2.000, 7.500),
        _actual(
            {"side": "SELL", "size": 1.0, "price": 5.0},
            {"side": "SELL", "size": 1.0, "price": 10.0},
        ),
        msg="SELL追加 - different price",
    )

    testcase.assertEqual(
        ("BUY", 1.500, 10.000),
        _actual(
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 0.5, "price": 10.0},
        ),
        msg="BUY追加 - different size",
    )
    testcase.assertEqual(
        ("SELL", 1.500, 10.000),
        _actual(
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 0.5, "price": 10.0},
        ),
        msg="SELL追加 - different size",
    )

    testcase.assertEqual(
        ("BUY", 1.500, 8.333),
        _actual(
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 0.5, "price": 5.0},
        ),
        msg="BUY追加 - different size and price",
    )
    testcase.assertEqual(
        ("SELL", 1.500, 8.333),
        _actual(
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 0.5, "price": 5.0},
        ),
        msg="SELL追加 - different size and price",
    )

    testcase.assertEqual(
        ("BUY", 0.5, 10.0),
        _actual(
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 0.5, "price": 15.0},
        ),
        msg="BUYポジション減少",
    )
    testcase.assertEqual(
        ("SELL", 0.5, 10.0),
        _actual(
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 0.5, "price": 15.0},
        ),
        msg="SELLポジション減少",
    )

    testcase.assertEqual(
        (None, None, None),
        _actual(
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 1.0, "price": 15.0},
        ),
        msg="BUYポジション解消",
    )
    testcase.assertEqual(
        (None, None, None),
        _actual(
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 1.0, "price": 15.0},
        ),
        msg="SELLポジション解消",
    )

    testcase.assertEqual(
        ("SELL", 0.5, 15.0),
        _actual(
            {"side": "BUY", "size": 1.0, "price": 10.0},
            {"side": "SELL", "size": 1.5, "price": 15.0},
        ),
        msg="BUYポジション反転",
    )
    testcase.assertEqual(
        ("BUY", 0.5, 15.0),
        _actual(
            {"side": "SELL", "size": 1.0, "price": 10.0},
            {"side": "BUY", "size": 1.5, "price": 15.0},
        ),
        msg="SELLポジション反転",
    )


@pytest.mark.asyncio
async def test_engine_create_position_item_buy_from_no_position(
    testcase: unittest.TestCase,
    client: pybotters.Client,
):
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "LIMIT")
    execution_item = engine._create_execution_item(order_item)
    position_item = engine._create_position_item(execution_item)
    testcase.assertDictEqual(
        {
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 10,
            "size": 1.0,
        },
        position_item,
    )


@pytest.mark.asyncio
async def test_engine_create_position_item_sell_from_no_position(
    testcase: unittest.TestCase,
    client: pybotters.Client,
):
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "SELL", 10, 1, "LIMIT")
    execution_item = engine._create_execution_item(order_item)
    position_item = engine._create_position_item(execution_item)
    testcase.assertDictEqual(
        {
            "symbol": SYMBOL,
            "side": "SELL",
            "price": 10,
            "size": 1.0,
        },
        position_item,
    )


@pytest.mark.asyncio
async def test_engine_create_position_item_buy_from_buy_position(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):

    mock_store = pbw.core.PositionStore()
    mock_store._insert([{"symbol": SYMBOL, "side": "BUY", "price": 10, "size": 1.0}])
    mocker.patch(
        "pybotters_wrapper.sandbox.store.SandboxDataStoreWrapper.position",
        return_value=mock_store,
        new_callable=mocker.PropertyMock,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "BUY", 10, 1, "LIMIT")
    execution_item = engine._create_execution_item(order_item)
    position_item = engine._create_position_item(execution_item)
    testcase.assertDictEqual(
        {
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 10,
            "size": 2.0,
        },
        position_item,
    )


@pytest.mark.asyncio
async def test_engine_create_position_item_sell_from_sell_position(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):

    mock_store = pbw.core.PositionStore()
    mock_store._insert([{"symbol": SYMBOL, "side": "SELL", "price": 10, "size": 1.0}])
    mocker.patch(
        "pybotters_wrapper.sandbox.store.SandboxDataStoreWrapper.position",
        return_value=mock_store,
        new_callable=mocker.PropertyMock,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "SELL", 10, 1, "LIMIT")
    execution_item = engine._create_execution_item(order_item)
    position_item = engine._create_position_item(execution_item)
    testcase.assertDictEqual(
        {
            "symbol": SYMBOL,
            "side": "SELL",
            "price": 10,
            "size": 2.0,
        },
        position_item,
    )


@pytest.mark.asyncio
async def test_engine_create_position_item_sell_from_buy_position(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):

    mock_store = pbw.core.PositionStore()
    mock_store._insert([{"symbol": SYMBOL, "side": "BUY", "price": 10, "size": 1.0}])
    mocker.patch(
        "pybotters_wrapper.sandbox.store.SandboxDataStoreWrapper.position",
        return_value=mock_store,
        new_callable=mocker.PropertyMock,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "SELL", 10, 2, "LIMIT")
    execution_item = engine._create_execution_item(order_item)
    position_item = engine._create_position_item(execution_item)
    testcase.assertDictEqual(
        {
            "symbol": SYMBOL,
            "side": "SELL",
            "price": 10,
            "size": 1,
        },
        position_item,
    )


@pytest.mark.asyncio
async def test_engine_create_position_item_buy_from_sell_position(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mock_store = pbw.core.PositionStore()
    mock_store._insert([{"symbol": SYMBOL, "side": "SELL", "price": 10, "size": 1.0}])
    mocker.patch(
        "pybotters_wrapper.sandbox.store.SandboxDataStoreWrapper.position",
        return_value=mock_store,
        new_callable=mocker.PropertyMock,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = engine._create_order_item(SYMBOL, "BUY", 10, 2, "LIMIT")
    execution_item = engine._create_execution_item(order_item)
    position_item = engine._create_position_item(execution_item)
    testcase.assertDictEqual(
        {
            "symbol": SYMBOL,
            "side": "BUY",
            "price": 10,
            "size": 1,
        },
        position_item,
    )


@pytest.mark.asyncio
async def test_engine_insert_limit_order(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    id = engine.insert_order(SYMBOL, "BUY", 10, 1, "LIMIT")
    testcase.assertEqual("uuid", id)
    testcase.assertEqual(
        1,
        len(
            store.order.find(
                {
                    "id": "uuid",
                    "symbol": SYMBOL,
                    "side": "BUY",
                    "price": 10,
                    "size": 1,
                    "type": "LIMIT",
                }
            )
        ),
    )


@pytest.mark.asyncio
async def test_engine_delete_order(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    id = engine.insert_order(SYMBOL, "BUY", 10, 1, "LIMIT")
    testcase.assertEqual(1, len(store.order.find({"id": id})))
    engine.delete_order(SYMBOL, id)
    testcase.assertEqual(0, len(store.order.find({"id": id})))


@pytest.mark.asyncio
async def test_engine_is_executed_buy(
    testcase: unittest.TestCase, client: pybotters.Client
):
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item = {"symbol": "a", "price": 10, "side": "BUY"}
    testcase.assertTrue(engine._is_executed(order_item, {"symbol": "a", "price": 9}))
    testcase.assertTrue(engine._is_executed(order_item, {"symbol": "a", "price": 10}))
    testcase.assertFalse(engine._is_executed(order_item, {"symbol": "a", "price": 11}))
    testcase.assertFalse(engine._is_executed(order_item, {"symbol": "b", "price": 9}))


@pytest.mark.asyncio
async def test_engine_is_executed_sell(
    testcase: unittest.TestCase, client: pybotters.Client
):
    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_item_sell = {"symbol": "a", "price": 10, "side": "SELL"}
    testcase.assertFalse(
        engine._is_executed(order_item_sell, {"symbol": "a", "price": 9})
    )
    testcase.assertTrue(
        engine._is_executed(order_item_sell, {"symbol": "a", "price": 10})
    )
    testcase.assertTrue(
        engine._is_executed(order_item_sell, {"symbol": "a", "price": 11})
    )
    testcase.assertFalse(
        engine._is_executed(order_item_sell, {"symbol": "b", "price": 11})
    )


@pytest.mark.asyncio
async def test_engine_handle_execution(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch("pandas.Timestamp.utcnow", return_value="2022-02-22 02:22:23")

    store, api = pbw.create_sandbox(EXCHANGE, client)
    engine = store._engine
    order_id = engine.insert_order(SYMBOL, "BUY", 10, 1, "LIMIT")

    testcase.assertEqual(1, len(store.order))

    order_item = store.order.find({"id": order_id})[0]
    engine._handle_execution(order_item)

    testcase.assertEqual(1, len(store.execution))
    testcase.assertDictEqual(
        {
            "id": "uuid",
            "symbol": SYMBOL,
            "side": "BUY",
            "size": 1,
            "price": 10,
            "timestamp": "2022-02-22 02:22:23",
        },
        store.execution.find()[0],
    )
    testcase.assertEqual(1, len(store.position))
    testcase.assertDictEqual(
        {
            "symbol": SYMBOL,
            "side": "BUY",
            "size": 1,
            "price": 10,
        },
        store.position.find()[0],
    )
    testcase.assertEqual(0, len(store.order))


@pytest.mark.asyncio
async def test_api_limit_order(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    store, api = pbw.create_sandbox(EXCHANGE, client)
    order_resp = await api.limit_order(SYMBOL, "BUY", 10, 1)
    testcase.assertEqual("uuid", order_resp.order_id)
    testcase.assertEqual(200, order_resp.status)
    testcase.assertEqual(1, len(store.order.find({"id": order_resp.order_id})))


@pytest.mark.asyncio
async def test_api_market_order(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    order_resp = await api.market_order(SYMBOL, "BUY", 10, 1)
    testcase.assertEqual("uuid", order_resp.order_id)
    testcase.assertEqual(200, order_resp.status)
    testcase.assertEqual(0, len(store.order.find({"id": order_resp.order_id})))
    testcase.assertEqual(1, len(store.execution.find({"id": order_resp.order_id})))
    testcase.assertEqual(1, len(store.position.find({"side": "BUY"})))
    testcase.assertEqual(10, store.position.find()[0]["price"])


@pytest.mark.asyncio
async def test_api_cancel_order_200(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    store, api = pbw.create_sandbox(EXCHANGE, client)
    order_resp = await api.limit_order(SYMBOL, "BUY", 10, 1)
    cancel_resp = await api.cancel_order(SYMBOL, order_resp.order_id)
    testcase.assertEqual("uuid", cancel_resp.order_id)
    testcase.assertEqual(200, cancel_resp.status)
    testcase.assertEqual(0, len(store.order))


@pytest.mark.asyncio
async def test_api_cancel_order_500(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch("uuid.uuid4", return_value="uuid")
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    order_resp = await api.market_order(SYMBOL, "BUY", 10, 1)
    cancel_resp = await api.cancel_order(SYMBOL, order_resp.order_id)
    testcase.assertEqual("uuid", cancel_resp.order_id)
    testcase.assertEqual(500, cancel_resp.status)
    testcase.assertEqual(0, len(store.order))
    testcase.assertFalse(cancel_resp.is_success())


@pytest.mark.asyncio
async def test_store_position(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    await api.market_order(SYMBOL, "BUY", 10, 1)
    testcase.assertEqual(1, len(store.position))
    await api.market_order(SYMBOL, "SELL", 10, 1)
    testcase.assertEqual(0, len(store.position))


@pytest.mark.asyncio
async def test_store_position_with_multiple_symbols(
    testcase: unittest.TestCase,
    client: pybotters.Client,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch(
        "pybotters_wrapper.sandbox.engine.SandboxEngine._get_execution_price_for_market_order",
        return_value=10,
    )
    store, api = pbw.create_sandbox(EXCHANGE, client)
    await api.market_order("A", "BUY", 10, 1)
    testcase.assertEqual(1, len(store.position))
    await api.market_order("B", "BUY", 10, 1)
    testcase.assertEqual(2, len(store.position))
    await api.market_order("A", "SELL", 10, 1)
    testcase.assertEqual(1, len(store.position))
    testcase.assertEqual("B", store.position.find()[0]["symbol"])
