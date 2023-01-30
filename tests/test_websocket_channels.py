import asyncio
import unittest

import pybotters
import pybotters_wrapper as pbw
import pytest
import pytest_mock
import pytest_asyncio


def test_subscribe(testcase: unittest.TestCase):
    symbol = "BTC_JPY"
    expected = {
        "wss://api.coin.z.com/ws/public/v1": [
            {"command": "subscribe", "channel": "ticker", "symbol": "BTC_JPY"},
            {
                "command": "subscribe",
                "channel": "trades",
                "symbol": "BTC_JPY",
                "option": "TAKER_ONLY",
            },
            {"command": "subscribe", "channel": "orderbooks", "symbol": "BTC_JPY"},
        ],
        "wss://api.coin.z.com/ws/private/v1": [
            {"command": "subscribe", "channel": "executionEvents"},
            {"command": "subscribe", "channel": "orderEvents"},
            {"command": "subscribe", "channel": "positionEvents"},
            {"command": "subscribe", "channel": "positionSummaryEvents"},
        ],
    }

    actual = (
        pbw.gmocoin.GMOWebsocketChannels()
        .subscribe("ticker", symbol=symbol)
        .subscribe("trades", symbol=symbol, option="TAKER_ONLY")
        .subscribe("orderbooks", symbol=symbol)
        .subscribe("executionEvents")
        .subscribe("orderEvents")
        .subscribe("positionEvents")
        .subscribe("positionSummaryEvents")
        .get()
    )
    testcase.assertDictEqual(expected, actual, "subscribe")


def test_binancespot(testcase: unittest.TestCase, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = {
        "wss://stream.binance.com/ws": [
            {
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@ticker",
                    "btcusdt@aggTrade",
                    "btcusdt@bookTicker",
                    "btcusdt@depth",
                    "btcusdt@kline_1m",
                    "LISTEN_KEY",
                ],
                "id": 1000000000,
            }
        ]
    }
    actual = (
        pbw.binance.BinanceSpotWebsocketChannels()
        .ticker(symbol)
        .agg_trades(symbol)
        .book_ticker(symbol)
        .depth(symbol)
        .kline(symbol, "1m")
        .order()
        .execution()
        .position()
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_binanceusdsm(testcase: unittest.TestCase, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSDT"
    expected = {
        "wss://fstream.binance.com/ws": [
            {
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@ticker",
                    "btcusdt@aggTrade",
                    "btcusdt@bookTicker",
                    "btcusdt@depth",
                    "btcusdt@kline_1m",
                    "btcusdt_perpetual@continuousKline_1m",
                    "btcusdt@forceOrder",
                    "btcusdt@markPrice",
                    "defiusdt@compositeIndex",
                    "LISTEN_KEY",
                ],
                "id": 1000000000,
            }
        ]
    }
    actual = (
        pbw.binance.BinanceUSDSMWebsocketChannels()
        .ticker(symbol)
        .agg_trades(symbol)
        .book_ticker(symbol)
        .depth(symbol)
        .kline(symbol, "1m")
        .continuous_kline(symbol, "perpetual", "1m")
        .liquidation(symbol)
        .mark_price(symbol)
        .composite_index("defiusdt")
        .order()
        .execution()
        .position()
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_binancecoinm(testcase: unittest.TestCase, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSD_PERP"
    expected = {
        "wss://dstream.binance.com/ws": [
            {
                "method": "SUBSCRIBE",
                "params": [
                    "btcusd_perp@ticker",
                    "btcusd_perp@aggTrade",
                    "btcusd_perp@bookTicker",
                    "btcusd_perp@depth",
                    "btcusd_perp@kline_1m",
                    "btcusd_perp_perpetual@continuousKline_1m",
                    "btcusd_perp@forceOrder",
                    "btcusd_perp@markPrice",
                    "btcusd@indexPrice@1s",
                    "btcusd@indexPriceKline_1m",
                    "LISTEN_KEY",
                ],
                "id": 1000000000,
            }
        ]
    }
    actual = (
        pbw.binance.BinanceCOINMWebsocketChannels()
        .ticker(symbol)
        .agg_trades(symbol)
        .book_ticker(symbol)
        .depth(symbol)
        .kline(symbol, "1m")
        .continuous_kline(symbol, "perpetual", "1m")
        .liquidation(symbol)
        .mark_price(symbol)
        .index_price("btcusd")
        .index_price_kline("btcusd", "1m")
        .mark_price(symbol)
        .order()
        .execution()
        .position()
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_bitbank(testcase: unittest.TestCase):
    symbol = "btc_jpy"
    expected = {
        "wss://stream.bitbank.cc/socket.io/?EIO=3&transport=websocket": [
            '42["join-room","ticker_btc_jpy"]',
            '42["join-room","transactions_btc_jpy"]',
            '42["join-room","depth_whole_btc_jpy"]',
        ]
    }
    actual = (
        pbw.bitbank.bitbankWebsocketChannels()
        .ticker(symbol)
        .trades(symbol)
        .orderbook(symbol)
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_bitflyer(testcase: unittest.TestCase, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "FX_BTC_JPY"
    channels = pbw.bitflyer.bitFlyerWebsocketChannels()
    expected = {
        "wss://ws.lightstream.bitflyer.com/json-rpc": [
            {
                "method": "subscribe",
                "params": {"channel": "lightning_board_FX_BTC_JPY", "id": 1000000000},
            },
            {
                "method": "subscribe",
                "params": {
                    "channel": "lightning_board_snapshot_FX_BTC_JPY",
                    "id": 1000000000,
                },
            },
            {
                "method": "subscribe",
                "params": {
                    "channel": "lightning_executions_FX_BTC_JPY",
                    "id": 1000000000,
                },
            },
            {
                "method": "subscribe",
                "params": {"channel": "lightning_ticker_FX_BTC_JPY", "id": 1000000000},
            },
            {
                "method": "subscribe",
                "params": {"channel": "child_order_events", "id": 1000000000},
            },
            {
                "method": "subscribe",
                "params": {"channel": "parent_order_events", "id": 1000000000},
            },
        ]
    }

    actual = (
        channels.lightning_board(symbol)
        .lightning_board_snapshot(symbol)
        .lightning_executions(symbol)
        .lightning_ticker(symbol)
        .child_order_events()
        .parent_order_events()
        .get()
    )
    print()
    print(expected)
    print(dict(actual))
    testcase.assertDictEqual(expected, actual)


def test_bitget(testcase: unittest.TestCase):
    # TODO: private channels
    symbol = "BTCUSDT"
    expected = {
        "wss://ws.bitget.com/mix/v1/stream": [
            {
                "op": "subscribe",
                "args": [{"channel": "ticker", "instId": "BTCUSDT", "instType": "mc"}],
            },
            {
                "op": "subscribe",
                "args": [{"channel": "trade", "instId": "BTCUSDT", "instType": "mc"}],
            },
            {
                "op": "subscribe",
                "args": [
                    {"channel": "candle1m", "instId": "BTCUSDT", "instType": "mc"}
                ],
            },
            {
                "op": "subscribe",
                "args": [{"channel": "books", "instId": "BTCUSDT", "instType": "mc"}],
            },
        ]
    }
    actual = (
        pbw.bitget.BitgetWebsocketChannels()
        .ticker(symbol)
        .trades(symbol)
        .candlesticks(symbol, "1m")
        .books(symbol)
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_bybitusdt(testcase: unittest.TestCase):
    symbol = "BTCUSDT"
    expected = {
        "wss://stream.bybit.com/realtime_public": [
            {"op": "subscribe", "args": ["instrument_info.100ms.BTCUSDT"]},
            {"op": "subscribe", "args": ["trade.BTCUSDT"]},
            {"op": "subscribe", "args": ["orderBook_200.100ms.BTCUSDT"]},
            {"op": "subscribe", "args": ["candle.1.BTCUSDT"]},
            {"op": "subscribe", "args": ["liquidation.BTCUSDT"]},
        ],
        "wss://stream.bybit.com/realtime_private": [
            {"op": "subscribe", "args": ["stop_order"]},
            {"op": "subscribe", "args": ["order"]},
            {"op": "subscribe", "args": ["position"]},
            {"op": "subscribe", "args": ["execution"]},
            {"op": "subscribe", "args": ["wallet"]},
        ],
    }
    actual = (
        pbw.bybit.BybitUSDTWebsocketChannels()
        .ticker(symbol)
        .trades(symbol)
        .orderbook(symbol)
        .candle(symbol)
        .liquidation(symbol)
        .order()
        .position()
        .execution()
        .wallet()
        .stop_order()
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_bybitinverse(testcase: unittest.TestCase):
    symbol = "BTCUSDT"
    expected = {
        "wss://stream.bybit.com/realtime": [
            {"op": "subscribe", "args": ["instrument_info.100ms.BTCUSDT"]},
            {"op": "subscribe", "args": ["trade.BTCUSDT"]},
            {"op": "subscribe", "args": ["orderBook_200.100ms.BTCUSDT"]},
            {"op": "subscribe", "args": ["klineV2.1.BTCUSDT"]},
            {"op": "subscribe", "args": ["liquidation"]},
            {"op": "subscribe", "args": ["insurance"]},
            {"op": "subscribe", "args": ["stop_order"]},
            {"op": "subscribe", "args": ["order"]},
            {"op": "subscribe", "args": ["position"]},
            {"op": "subscribe", "args": ["execution"]},
            {"op": "subscribe", "args": ["wallet"]},
        ]
    }
    actual = (
        pbw.bybit.BybitInverseWebsocketChannels()
        .ticker(symbol)
        .trades(symbol)
        .orderbook(symbol)
        .kline_v2(symbol)
        .liquidation()
        .insurance()
        .order()
        .position()
        .execution()
        .wallet()
        .stop_order()
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_coincheck(testcase: unittest.TestCase):
    symbol = "btc_jpy"
    expected = {
        "wss://ws-api.coincheck.com/": [
            {"type": "subscribe", "channel": "btc_jpy-trades"},
            {"type": "subscribe", "channel": "btc_jpy-orderbook"},
        ]
    }
    actual = (
        pbw.coincheck.CoinCheckWebsocketChannels()
        .ticker(symbol)
        .trades(symbol)
        .orderbook(symbol)
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_gmocoin(testcase: unittest.TestCase):
    symbol = "BTC_JPY"
    expected = {
        "wss://api.coin.z.com/ws/public/v1": [
            {"command": "subscribe", "channel": "ticker", "symbol": "BTC_JPY"},
            {
                "command": "subscribe",
                "channel": "trades",
                "symbol": "BTC_JPY",
                "option": "TAKER_ONLY",
            },
            {"command": "subscribe", "channel": "orderbooks", "symbol": "BTC_JPY"},
        ],
        "wss://api.coin.z.com/ws/private/v1": [
            {"command": "subscribe", "channel": "executionEvents"},
            {"command": "subscribe", "channel": "orderEvents"},
            {"command": "subscribe", "channel": "positionEvents"},
            {"command": "subscribe", "channel": "positionSummaryEvents"},
        ],
    }

    actual = (
        pbw.gmocoin.GMOWebsocketChannels()
        .ticker(symbol)
        .trades(symbol)
        .orderbooks(symbol)
        .execution_events()
        .order_events()
        .position_events()
        .position_summary_events()
        .get()
    )
    testcase.assertDictEqual(expected, actual, "alias")


def test_kucoinspot(testcase: unittest.TestCase, mocker: pytest_mock.MockerFixture):
    _id = "bdca01b1-5fea-4b56-97b9-c131dd957274"
    mocker.patch("uuid.uuid4", return_value=_id)
    symbol = "BTC-USDT"
    expected = {
        None: [
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/market/ticker:BTC-USDT",
                "response": True,
            },
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/market/match:",
                "response": True,
            },
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/spotMarket/level2Depth50:BTC-USDT",
                "response": True,
            },
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/spotMarket/tradeOrders",
                "response": True,
            },
        ]
    }
    actual = (
        pbw.kucoin.KuCoinSpotWebsocketChannels()
        .market_ticker(symbol)
        .market_match()
        .spot_market_level2depth50(symbol)
        .spot_market_trade_orders()
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_kucoinfutures(testcase: unittest.TestCase, mocker: pytest_mock.MockerFixture):
    _id = "bdca01b1-5fea-4b56-97b9-c131dd957274"
    mocker.patch("uuid.uuid4", return_value=_id)
    symbol = "XBTUSDTM"
    expected = {
        None: [
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/contractMarket/tickerV2:XBTUSDTM",
                "response": True,
            },
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/contractMarket/execution:XBTUSDTM",
                "response": True,
            },
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/contractMarket/level2Depth50:XBTUSDTM",
                "response": True,
            },
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/contractMarket/tradeOrders",
                "response": True,
            },
            {
                "id": _id,
                "type": "subscribe",
                "topic": "/contract/position:XBTUSDTM",
                "response": True,
            },
        ]
    }

    actual = (
        pbw.kucoin.KuCoinFuturesWebsocketChannels()
        .contract_market_ticker_v2(symbol)
        .contract_market_execution(symbol)
        .contract_market_level2depth50(symbol)
        .contract_market_trade_orders()
        .contract_market_execution(symbol)
        .contract_position(symbol)
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_okx(testcase: unittest.TestCase):
    symbol = "BTC-USDT"
    expected = {
        "wss://ws.okx.com:8443/ws/v5/public": [
            {"op": "subscribe", "args": [{"channel": "tickers", "instId": "BTC-USDT"}]},
            {"op": "subscribe", "args": [{"channel": "trades", "instId": "BTC-USDT"}]},
            {"op": "subscribe", "args": [{"channel": "books", "instId": "BTC-USDT"}]},
        ]
    }
    actual = (
        pbw.okx.OKXWebsocketChannels()
        .tickers(symbol)
        .trades(symbol)
        .books(symbol)
        .get()
    )
    testcase.assertDictEqual(expected, actual)


def test_phemex(testcase: unittest.TestCase, mocker: pytest_mock.MockerFixture):
    mocker.patch("time.monotonic", return_value=1)
    symbol = "BTCUSD"
    expected = {
        "wss://phemex.com/ws": [
            {"id": 1000000000, "method": "tick.subscribe", "params": ["BTCUSD"]},
            {"id": 1000000000, "method": "trade.subscribe", "params": ["BTCUSD"]},
            {
                "id": 1000000000,
                "method": "orderbook.subscribe",
                "params": ["BTCUSD", True],
            },
        ]
    }
    actual = (
        pbw.phemex.PhemexWebsocketChannels()
        .tick(symbol)
        .trade(symbol)
        .orderbook(symbol)
        .get()
    )
    testcase.maxDiff = None
    testcase.assertDictEqual(expected, actual)
