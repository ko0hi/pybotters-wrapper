import asyncio
import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "btc_jpy"

    async with pybotters.Client() as client:
        channels = pbw.bitbank.bitbankWebsocketChannels()
        subscribes = (
            channels.ticker(symbol).trades(symbol).orderbook(symbol).get()
        )
        for endpoint, send in subscribes.items():
            await client.ws_connect(
                endpoint, send_str=send, hdlr_str=lambda msg, ws: print(msg)
            )

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
