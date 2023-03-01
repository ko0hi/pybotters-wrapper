import asyncio
import random

import pybotters_wrapper as pbw


async def main():
    exchange = "binanceusdsm"
    symbol = "BTCUSDT"

    async with pbw.create_client() as client:
        store, api = pbw.create_store_and_api(exchange, symbol, sandbox=True)
        await store.subscribe("public", symbol=symbol).connect(
            client, waits=["orderbook"]
        )
        pnl = pbw.plugins.pnl(store, symbol)
        while True:
            side = random.choice(["BUY", "SELL"])
            await api.market_order(symbol, side, 0.1)
            print("PNL status", pnl.status())
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
