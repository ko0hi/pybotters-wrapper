import asyncio
import time
from collections import defaultdict

import numpy as np
import pybotters_wrapper as pbw


def create_binning_book(store: pbw.core.OrderbookStore, pips, n=100):
    asks, bids = store.sorted().values()

    def _binnize(items):
        rtn = defaultdict(float)
        for i in items:
            price = i["price"]
            size = i["size"]
            rounded_i = int(price / pips) * pips
            rtn[rounded_i] += size
            if len(rtn) == n:
                break
        return rtn

    return _binnize(asks), _binnize(bids)


async def main():
    exchange = "binanceusdsm"
    configs = {
        "binanceusdsm": {
            "symbol": "BTCUSDT",
            "min": 0,
            "max": 200000,
            "pips": 20,
            "initialize": [("orderbook", {"symbol": "BTCUSDT"})],
        },
        "bitflyer": {
            "symbol": "FX_BTC_JPY",
            "min": 1000000,
            "max": 5000000,
            "pips": 1000,
        },
        "bybitusdt": {"symbol": "BTCUSDT", "min": 0, "max": 40000, "pips": 10},
    }

    async with pbw.create_client() as client:
        conf = configs[exchange]
        store = pbw.create_store(exchange)

        # DataStoreに挿入する前に初期化する必要がある
        binning_book = pbw.plugins.binningbook(
            store,
            min_bin=conf["min"],
            max_bin=conf["max"],
            pips=conf["pips"],
            precision=10,
        )

        if "initialize" in conf:
            await store.initialize(conf["initialize"], client)
        await store.subscribe(["orderbook"], symbol=conf["symbol"]).connect(client)

        while True:
            await store.orderbook.wait()

            s = time.time()
            binned_asks1, binned_bids1 = binning_book.asks(), binning_book.bids()
            elapsed1 = time.time() - s

            s = time.time()
            binned_asks2, binned_bids2 = create_binning_book(
                store.orderbook, conf["pips"]
            )
            elapsed2 = time.time() - s

            print(f"{elapsed1:.7f} vs. {elapsed2:.7f}")

            for p, s in zip(*binned_asks1):
                assert np.isclose(binned_asks2[p], s), f"{p}: {binned_asks2[p]} vs. {s}"

            for p, s in zip(*binned_bids1):
                assert np.isclose(binned_bids2[p], s), f"{p}: {binned_bids2[p]} vs. {s}"


if __name__ == "__main__":
    asyncio.run(main())
