import pandas as pd
import pytest

import pybotters_wrapper as pbw


@pytest.mark.asyncio
async def test_timebar():
    store = pbw.create_store("binanceusdsm")
    items = [
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:00", utc=True),
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": 10000,
            "size": 1,
        },
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:01", utc=True),
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": 10003,
            "size": 1,
        },
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:01", utc=True),
            "symbol": "BTCUSDT",
            "side": "SELL",
            "price": 10001,
            "size": 1,
        },
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:02", utc=True),
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": 9999,
            "size": 1,
        },
    ]
    timebar = pbw.plugins.timebar(store, "BTCUSDT", seconds=1, maxlen=999)

    for item in items:
        timebar._on_watch(None, "insert", None, item)

    assert (999, 8) == timebar.df.shape
    assert (2, 8) == timebar.df.dropna().shape
    assert {
        "timestamp": pd.to_datetime("2021-01-01 00:00:00", utc=True),
        "open": 10000,
        "high": 10000,
        "low": 10000,
        "close": 10000,
        "size": 1,
        "buy_size": 1,
        "sell_size": 0,
    } == timebar.df.dropna().iloc[0].to_dict()
    assert {
        "timestamp": pd.to_datetime("2021-01-01 00:00:01", utc=True),
        "open": 10003,
        "high": 10003,
        "low": 10001,
        "close": 10001,
        "size": 2,
        "buy_size": 1,
        "sell_size": 1,
    } == timebar.df.dropna().iloc[1].to_dict()
    assert {
        "timestamp": pd.to_datetime("2021-01-01 00:00:02", utc=True),
        "open": 9999,
        "high": 9999,
        "low": 9999,
        "close": 9999,
        "size": 1,
        "buy_size": 1,
        "sell_size": 0,
    } == timebar.cur_bar


@pytest.mark.asyncio
async def test_no_update_with_different_symbol():
    store = pbw.create_store("binanceusdsm")
    items = [
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:00", utc=True),
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": 10000,
            "size": 1,
        },
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:01", utc=True),
            "symbol": "ETHUSDT",
            "side": "BUY",
            "price": 10003,
            "size": 1,
        },
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:01", utc=True),
            "symbol": "BTCUSDT",
            "side": "SELL",
            "price": 10001,
            "size": 1,
        },
        {
            "timestamp": pd.to_datetime("2021-01-01 00:00:02", utc=True),
            "symbol": "BTCUSDT",
            "side": "BUY",
            "price": 9999,
            "size": 1,
        },
    ]
    timebar = pbw.plugins.timebar(store, "BTCUSDT", seconds=1, maxlen=999)

    for item in items:
        timebar._on_watch(None, "insert", None, item)

    assert (999, 8) == timebar.df.shape
    assert (2, 8) == timebar.df.dropna().shape
    assert {
        "timestamp": pd.to_datetime("2021-01-01 00:00:00", utc=True),
        "open": 10000,
        "high": 10000,
        "low": 10000,
        "close": 10000,
        "size": 1,
        "buy_size": 1,
        "sell_size": 0,
    } == timebar.df.dropna().iloc[0].to_dict()
    assert {
        "timestamp": pd.to_datetime("2021-01-01 00:00:01", utc=True),
        "open": 10001,
        "high": 10001,
        "low": 10001,
        "close": 10001,
        "size": 1,
        "buy_size": 0,
        "sell_size": 1,
    } == timebar.df.dropna().iloc[1].to_dict()
    assert {
        "timestamp": pd.to_datetime("2021-01-01 00:00:02", utc=True),
        "open": 9999,
        "high": 9999,
        "low": 9999,
        "close": 9999,
        "size": 1,
        "buy_size": 1,
        "sell_size": 0,
    } == timebar.cur_bar
