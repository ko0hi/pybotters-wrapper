import unittest

import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.mark.asyncio
async def test_initialize(testcase: unittest.TestCase, client: pybotters.Client):
    store = pbw.create_binancespot_store()
    symbol = "BTCUSDT"
    await store.initialize(
        [
            ("orderbook", {"symbol": symbol}),
            client.get(
                "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m",
                auth=None,
            ),
        ],
        client,
    )

    if len(store.orderbook) == 0:
        await store.orderbook.wait()
    testcase.assertNotEqual(0, len(store.orderbook))
    testcase.assertNotEqual(0, len(store.store.kline))


@pytest.mark.asyncio
async def test_initialize_by_conf(
    testcase: unittest.TestCase, client: pybotters.Client
):
    store = pbw.create_binancespot_store()
    symbol = "BTCUSDT"
    await store.initialize_orderbook(client, symbol=symbol)
    if len(store.orderbook) == 0:
        await store.orderbook.wait()
    testcase.assertNotEqual(0, len(store.orderbook))


@pytest.mark.asyncio
async def test_initialize_missing_parameter(
    testcase: unittest.TestCase, client: pybotters.Client
):
    store = pbw.create_binancespot_store()
    with pytest.raises(RuntimeError):
        await store.initialize_orderbook(client)


@pytest.mark.asyncio
async def test_initialize_null_conf(
    testcase: unittest.TestCase, client: pybotters.Client
):
    store = pbw.create_binancespot_store()
    await store.initialize_ticker(client)  # ログを吐き出してスルー
    testcase.assertEqual(0, len(store.ticker))
