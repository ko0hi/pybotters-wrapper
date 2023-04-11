import pybotters
import pytest
import asyncio

import pybotters_wrapper as pbw


@pytest.mark.asyncio
async def test_watcher_execution(client: pybotters.Client):
    store, api = pbw.create_binanceusdsm_store_and_api(client, sandbox=True)
    symbol = "btcusdt"
    await store.subscribe("public", symbol=symbol).connect(client)
    await asyncio.sleep(1)
    watcher = pbw.plugins.execution_watcher(store)
    await asyncio.sleep(1)
    resp = await api.market_order(symbol, "BUY", 0.001)
    watcher.set(resp.order_id)
    await watcher.wait()
    print(watcher.result())
