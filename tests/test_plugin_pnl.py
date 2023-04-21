import unittest

import pandas as pd
import pybotters_wrapper as pbw
import pytest

@pytest.fixture
def testcase():
    return unittest.TestCase()


@pytest.mark.asyncio
async def test_pnl_wo_fee(testcase: unittest.TestCase):
    store = pbw.create_store("binanceusdsm")
    pnl = pbw.plugins.pnl(store, "BTCUSDT")

    pnl._update_pnl("BUY", 18000, 0.1, pd.Timestamp('2050-01-01 00:00:00', tz="UTC"))
    pnl._update_pnl("SELL", 19000, 0.2, pd.Timestamp('2050-01-01 00:01:00', tz="UTC"))
    testcase.assertEqual(100, pnl.pnl)

    pnl._update_pnl("BUY", 20000, 0.1, pd.Timestamp('2050-01-01 00:02:00', tz="UTC"))
    testcase.assertEqual(0, pnl.pnl)

    pnl.stop()


@pytest.mark.asyncio
async def test_pnl_w_fee(testcase: unittest.TestCase):
    store = pbw.create_store("binanceusdsm")
    pnl = pbw.plugins.pnl(store, "BTCUSDT", fee=0.001)

    pnl._update_pnl("BUY", 18000, 0.1, pd.Timestamp('2050-01-01 00:00:00', tz="UTC"))
    pnl._update_pnl("SELL", 19000, 0.2, pd.Timestamp('2050-01-01 00:01:00', tz="UTC"))
    testcase.assertEqual(
        100 - (18000 * 0.1 * 0.001 + 19000 * 0.2 * 0.001), pnl.pnl
    )

    pnl._update_pnl("BUY", 20000, 0.1, pd.Timestamp('2050-01-01 00:00:00', tz="UTC"))
    testcase.assertEqual(
        -(18000 * 0.1 * 0.001 + 19000 * 0.2 * 0.001 + 20000 * 0.1 * 0.001),
        pnl.pnl,
    )

    pnl.stop()

@pytest.mark.asyncio
async def test_realized_and_unrealized_pnl(testcase: unittest.TestCase):
    store = pbw.create_store("binanceusdsm")
    pnl = pbw.plugins.pnl(store, "BTCUSDT", fee=0.0)

    # ポジションなし
    testcase.assertEqual(0, pnl._unrealized_pnl)

    # ポジション積み増し
    pnl._update_pnl("BUY", 18000, 0.1, pd.Timestamp('2050-01-01 00:00:00', tz="UTC"))
    testcase.assertEqual(0, pnl._unrealized_pnl)

    # 未実現損益更新
    pnl._update_unrealized_pnl(20000, pd.Timestamp('2050-01-01 00:00:01', tz="UTC"))
    status = pnl.status()
    testcase.assertEqual(0, status["realized_pnl"])
    testcase.assertAlmostEqual((20000 - 18000) * 0.1, status["unrealized_pnl"], 10)

    # ポジション反転
    pnl._update_pnl("SELL", 21000, 0.3, pd.Timestamp('2050-01-01 00:01:00', tz="UTC"))
    status = pnl.status()
    testcase.assertAlmostEqual((21000 - 18000) * 0.1, status["realized_pnl"], 10)
    testcase.assertEqual(0, status["unrealized_pnl"])

    # ポジション一部決済
    pnl._update_pnl("BUY", 22000, 0.1, pd.Timestamp('2050-01-01 00:02:00', tz="UTC"))
    status = pnl.status()
    testcase.assertAlmostEqual((21000 - 18000) * 0.1 + (22000 - 21000) * (-0.1), status["realized_pnl"], 10)
    testcase.assertAlmostEqual((22000 - 21000) * (-0.1), status["unrealized_pnl"], 10)

    # ポジションなし
    pnl._update_pnl("BUY", 20000, 0.1, pd.Timestamp('2050-01-01 00:03:00', tz="UTC"))
    status = pnl.status()
    testcase.assertEqual(status["pnl"], status["realized_pnl"])
    testcase.assertEqual(0, status["unrealized_pnl"])