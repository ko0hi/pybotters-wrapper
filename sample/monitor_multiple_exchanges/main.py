import asyncio

import pandas as pd
import pybotters
import pybotters_wrapper as pbw


async def main():
    configs = {
        # "binancespot": {
        #     "symbol": "BTCUSDT",
        #     "initialize": [("orderbook", {"symbol": "BTCUSDT"})],
        # },
        # "binanceusdsm": {
        #     "symbol": "BTCUSDT",
        #     "initialize": [("orderbook", {"symbol": "BTCUSDT"})],
        # },
        # "binancecoinm": {
        #     "symbol": "BTCUSD_PERP",
        #     "initialize": [("orderbook", {"symbol": "BTCUSD_PERP"})],
        # },
        # "bitbank": {"symbol": "btc_jpy"},
        # "bitflyer": {"symbol": "FX_BTC_JPY"},
        # "bitget": {"symbol": "BTCUSDT"},
        # "bybitusdt": {"symbol": "BTCUSDT"},
        # "bybitinverse": {"symbol": "BTCUSD"},
        # "coincheck": {"symbol": "btc_jpy"},
        # "kucoinspot": {"symbol": "BTC-USDT", "initialize": ["token_public"]},
        # "kucoinfutures": {"symbol": "XBTUSDTM", "initialize": ["token_public"]},
        # "okx": {"symbol": "BTC-USDT"},
        "gmocoin": {"symbol": "BTC_JPY"},
        # "phemex": {"symbol": "BTCUSD"},
    }

    usd_jpy = 142
    jp_exchanges = {"bitbank", "bitflyer", "gmocoin", "coincheck"}

    async with pybotters.Client() as client:
        # ストアの初期化
        stores = {}
        for exchange, conf in configs.items():
            store = pbw.create_store(exchange)


            if "initialize" in conf:
                await store.initialize(conf["initialize"], client)

            await store.subscribe("public", symbol=conf["symbol"]).connect(
                client,
                auto_reconnect=True,
            )
            stores[exchange] = store

        while True:
            data = {}
            for exchange, store in stores.items():
                tick = store.ticker.find()
                asks, bids = store.orderbook.sorted().values()
                last = store.trades.find()

                mul = usd_jpy if exchange not in jp_exchanges else 1

                data[exchange] = {
                    "ask": asks[0]["price"] * mul if len(asks) else None,
                    "ask_size": asks[0]["size"] if len(asks) else None,
                    "bid": bids[0]["price"] * mul if len(bids) else None,
                    "bid_size": bids[0]["size"] if len(bids) else None,
                    "tick": tick[0]["price"] * mul if len(tick) else None,
                    "ltp_side": last[-1]["side"] if len(last) else None,
                    "ltp_price": last[-1]["price"] * mul if len(last) else None,
                    "ltp_size": last[-1]["size"] if len(last) else None,
                }

            print("\033c", end="")
            print(pd.DataFrame(data).to_markdown())

            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
