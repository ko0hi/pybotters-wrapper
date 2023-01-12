import asyncio
import random

import pybotters_wrapper as pbw


async def main():
    # 3秒に一回適当に成行する
    # テストネット以外では使用しないこと
    exchange = "binanceusdsm_test"
    symbol = "BTCUSDT"

    async with pbw.create_client() as client:
        api = pbw.create_api(exchange, client, verbose=True)
        store = pbw.create_store(exchange)
        await store.subscribe("all", symbol=symbol).connect(client)

        pnl = pbw.plugins.pnl(store, symbol)

        while True:
            side = random.choice(["BUY", "SELL"])
            await api.market_order(symbol, side, 0.1)
            print("PNL status", pnl.status())
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
