import asyncio

import pybotters_wrapper as pbw


def open_double_cb(df):
    return {"close2": df.open.values[-1] * 2}


async def main():
    exchange = "binancecoinm"
    configs = {
        "binanceusdsm": {"symbol": "BTCUSDT"},
        "binancecoinm": {"symbol": "BTCUSD_PERP"}
    }

    async with pbw.create_client() as client:
        conf = configs[exchange]
        store = pbw.create_store(exchange)

        tbar = pbw.plugins.timebar(
            store, conf["symbol"], seconds=1, callback=[open_double_cb]
        )
        queue = tbar.subscribe()

        await store.subscribe("trades", symbol=conf["symbol"]).connect(client)

        while True:
            df = await queue.get()
            print("latest bars:", df.tail())
            print("callback:", tbar._)


if __name__ == "__main__":
    asyncio.run(main())
