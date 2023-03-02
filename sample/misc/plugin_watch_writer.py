import asyncio

import pybotters_wrapper as pbw


class CustomDataStoreWatchWriter(pbw.plugins.writer.DataStoreWatchWriter):
    def write(self, data: dict):
        print(data)

    def _transform_data(self, data: dict):
        return {"original_price": data["price"], "doubled_price": data["price"] * 2}


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

        await store.subscribe("trades", symbol=conf["symbol"]).connect(client)

        writer = CustomDataStoreWatchWriter(store, "trades", fields=["price"])

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
