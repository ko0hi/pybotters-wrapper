import pybotters
import pytest
import tempfile
import asyncio

import pybotters_wrapper as pbw


@pytest.mark.asyncio
async def test_data_store_csv_writer(client: pybotters.Client):
    store = pbw.create_binanceusdsm_store()
    with tempfile.NamedTemporaryFile("w") as f:
        writer = pbw.plugins.watch_csvwriter(
            store,
            store_name="trades",
            path=f.name + ".csv",
            flush=True,
            columns=["timestamp", "price"],
        )
        await store.subscribe("trades", symbol="btcusdt").connect(client)
        await asyncio.sleep(3)
        with open(f.name + ".csv") as fr:
            print("\n", fr.read())


@pytest.mark.asyncio
async def test_data_store_wait_csv_writer(client: pybotters.Client):
    store = pbw.create_binanceusdsm_store()
    with tempfile.NamedTemporaryFile("w") as f:
        writer = pbw.plugins.wait_csvwriter(
            store,
            store_name="trades",
            path=f.name + ".csv",
            flush=True,
            columns=["timestamp", "price"],
        )
        await store.subscribe("trades", symbol="btcusdt").connect(client)
        await asyncio.sleep(3)
        with open(f.name + ".csv") as fr:
            print("\n", fr.read())
