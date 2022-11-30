import asyncio

import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "BTC-USDT"

    async with pybotters.Client() as client:
        channels = pbw.kucoin.KuCoinSpotWebsocketChannels()
        subscribes = (
            channels.market_ticker(symbol)
            .market_match()
            .spot_market_level2depth50(symbol)
            .spot_market_trade_orders()
            .get()
        )

        store = pbw.create_store("kucoinspot")
        await store.initialize(["token"], client)

        for endpoint, send in subscribes.items():
            await client.ws_connect(
                store.endpoint, send_json=send, hdlr_json=lambda msg, ws: print(msg)
            )

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
