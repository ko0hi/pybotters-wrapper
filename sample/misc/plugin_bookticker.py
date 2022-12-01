import asyncio

import pybotters_wrapper as pbw


async def main():
    exchange = "bybitusdt"
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

        book_ticker = pbw.plugins.bookticker(store)

        if "initialize" in conf:
            await store.initialize(conf["initialize"], client)
        await store.subscribe("public", symbol=conf["symbol"]).connect(client)

        while True:
            await asyncio.sleep(1)
            print("LTP", book_ticker.price)
            print("BEST_ASK", book_ticker.best_ask, book_ticker.best_ask_size)
            print("BEST_BID", book_ticker.best_bid, book_ticker.best_bid_size)
            print("MID", book_ticker.mid)
            print("SPREAD", book_ticker.spread)
            print("ASKS", book_ticker.asks[:5])
            print("BIDS", book_ticker.bids[:5])


if __name__ == "__main__":
    asyncio.run(main())
