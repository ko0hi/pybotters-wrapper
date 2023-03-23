import asyncio

import pandas as pd
import pybotters
import pybotters_wrapper as pbw


async def main():
    async with pybotters.Client() as client:
        store = pbw.create_bitflyer_store()
        await store.subscribe("public", symbol="FX_BTC_JPY").subscribe(
            "public", symbol="BTC_JPY"
        ).connect(client=client, waits=["trades", "orderbook"])

        while True:
            data = {}
            for s in ["BTC_JPY", "FX_BTC_JPY"]:
                tick = store.ticker.find({"symbol": s})
                asks, bids = store.orderbook.sorted({"symbol": s}).values()
                last = store.trades.find({"symbol": s})

                data[s] = {
                    "ask": asks[0]["price"] if len(asks) else None,
                    "ask_size": asks[0]["size"] if len(asks) else None,
                    "bid": bids[0]["price"] if len(bids) else None,
                    "bid_size": bids[0]["size"] if len(bids) else None,
                    "tick": tick[0]["price"] if len(tick) else None,
                    "ltp_side": last[0]["side"] if len(last) else None,
                    "ltp_price": last[0]["price"] if len(last) else None,
                    "ltp_size": last[0]["size"] if len(last) else None,
                }

            df = pd.DataFrame(data).T
            df["spread"] = (
                df.loc["FX_BTC_JPY"].ltp_price - df.loc["BTC_JPY"].ltp_price
            ) / df.loc["BTC_JPY"].ltp_price

            print("\033c", end="")
            print(df.to_markdown())

            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
