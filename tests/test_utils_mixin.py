import unittest

from pybotters_wrapper.utils import mixins


def test_fetch_binancespot_precisions(testcase: unittest.TestCase):
    m = mixins.BinanceSpotMixin()
    # lazy fetch
    testcase.assertNotIn(m.exchange, m._PRICE_PRECISIONS)
    testcase.assertNotIn(m.exchange, m._SIZE_PRECISIONS)

    # 初回呼び出し時にfetchされる
    testcase.assertEqual("20000.12", m.format_price("BTCUSDT", 20000.1234))
    # str(round(value, precision))なので四捨五入
    testcase.assertEqual("0.12346", m.format_size("BTCUSDT", 0.123456789))

    testcase.assertIn(m.exchange, m._PRICE_PRECISIONS)
    testcase.assertIn(m.exchange, m._SIZE_PRECISIONS)


def test_fetch_binanceusdsm_precisions(testcase: unittest.TestCase):
    m = mixins.BinanceUSDSMMixin()
    testcase.assertNotIn(m.exchange, m._PRICE_PRECISIONS)
    testcase.assertNotIn(m.exchange, m._SIZE_PRECISIONS)
    testcase.assertEqual("20000.1", m.format_price("BTCUSDT", 20000.12))
    testcase.assertEqual("0.123", m.format_size("BTCUSDT", 0.123456789))


def test_fetch_binancecoinm_precisions(testcase: unittest.TestCase):
    m = mixins.BinanceCOINMMixin()
    testcase.assertNotIn(m.exchange, m._PRICE_PRECISIONS)
    testcase.assertNotIn(m.exchange, m._SIZE_PRECISIONS)
    testcase.assertEqual("20000.1", m.format_price("BTCUSD_PERP", 20000.12))
    testcase.assertEqual("1", m.format_size("BTCUSD_PERP", 1.23456))
