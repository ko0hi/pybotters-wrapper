import asyncio

import pybotters_wrapper as pbw


class CustomDataStoreWaitWriter(pbw.plugins.writer.DataStoreWaitWriter):
    def write(self, data: dict):
        print(data)

    def _transform_item(self, data: dict):
        return {k + "_custom": v for (k, v) in data.items()}


async def main():
    exchange = "binanceusdsm"
    configs = {
        "binanceusdsm": {"symbol": "BTCUSDT"},
        "bitflyer": {"symbol": "FX_BTC_JPY"},
        "bybitusdt": {"symbol": "BTCUSDT"},
    }

    async with pbw.create_client() as client:
        conf = configs[exchange]
        store = pbw.create_store(exchange)

        await store.subscribe("ticker", symbol=conf["symbol"]).connect(client)

        CustomDataStoreWaitWriter(store, "ticker")

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
