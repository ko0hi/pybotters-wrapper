import asyncio

import pybotters
import pytest

import pybotters_wrapper as pbw


@pytest.mark.asyncio
async def test_timebar(client: pybotters.Client):
    store = pbw.create_binanceusdsm_store()
    bar = pbw.plugins.timebar(store, seconds=1)
    await store.subscribe("trades", symbol="btcusdt").connect(client)
    queue = bar.subscribe()
    await queue.get()
    await queue.get()
    df = await queue.get()
    print("\n", df)


@pytest.mark.asyncio
async def test_volumebar(client: pybotters.Client):
    store = pbw.create_binanceusdsm_store()
    bar = pbw.plugins.volumebar(store, volume_unit=1)
    await store.subscribe("trades", symbol="btcusdt").connect(client)
    queue = bar.subscribe()
    await queue.get()
    await queue.get()
    df = await queue.get()
    print("\n", df)


@pytest.mark.asyncio
async def test_binningbook(client: pybotters.Client):
    store = pbw.create_binanceusdsm_store()
    book = pbw.plugins.binningbook(store, pips=10)
    await store.subscribe("orderbook", symbol="btcusdt").connect(client)
    await asyncio.sleep(1)
    print(book.asks())
    print(book.bids())


@pytest.mark.asyncio
async def test_bookticker(client: pybotters.Client):
    store = pbw.create_binanceusdsm_store()
    bookticker = pbw.plugins.bookticker(store)
    await store.subscribe(["trades", "orderbook"], symbol="btcusdt").connect(
        client
    )
    await asyncio.sleep(1)
    print(bookticker.tick)
