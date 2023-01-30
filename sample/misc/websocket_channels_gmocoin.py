import asyncio

import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "BTC_JPY"

    async with pybotters.Client() as client:
        channels = pbw.gmocoin.GMOWebsocketChannels()
        subscribes = (
            channels.ticker(symbol)
            .trades(symbol)
            .orderbooks(symbol)
            .execution_events()
            .execution_events()
            .order_events()
            .position_events()
            .position_summary_events()
            .get()
        )

        resp = await client.post("https://api.coin.z.com/private/v1/ws-auth")
        data = await resp.json()
        store = pybotters.GMOCoinDataStore()

        for endpoint, send in subscribes.items():
            if "private" in endpoint:
                endpoint += f"/{data['data']}"
            await client.ws_connect(
                endpoint,
                send_json=send,
                hdlr_json=lambda msg, ws: print(msg),
            )

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
