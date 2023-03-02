import unittest

import pytest

import pybotters_wrapper as pbw


@pytest.mark.asyncio
async def test_pnl_wo_fee(testcase: unittest.TestCase):
    store = pbw.create_binanceusdsm_store()
    pnl = pbw.plugins.pnl(store, "BTCUSDT")
    pnl._update_status("BUY", 18000, 0.1)
    pnl._update_status("SELL", 19000, 0.2)
    testcase.assertEqual(100, pnl.pnl)
    pnl._update_status("BUY", 20000, 0.1)
    testcase.assertEqual(0, pnl.pnl)


@pytest.mark.asyncio
async def test_pnl_w_fee(testcase: unittest.TestCase):
    store = pbw.create_binanceusdsm_store()
    pnl = pbw.plugins.pnl(store, "BTCUSDT", fee=0.001)
    pnl._update_status("BUY", 18000, 0.1)
    pnl._update_status("SELL", 19000, 0.2)
    testcase.assertEqual(
        100 - (18000 * 0.1 * 0.001 + 19000 * 0.2 * 0.001), pnl.pnl
    )
    pnl._update_status("BUY", 20000, 0.1)
    testcase.assertEqual(
        -(18000 * 0.1 * 0.001 + 19000 * 0.2 * 0.001 + 20000 * 0.1 * 0.001),
        pnl.pnl,
    )
