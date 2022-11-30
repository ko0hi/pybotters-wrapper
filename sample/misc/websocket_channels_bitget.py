import asyncio
import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "BTCUSDT"

    async with pybotters.Client() as client:
        channels = pbw.bitget.BitgetWebsocketChannels()
        # チェインパターンでかけます
        # subscribesはdict[list, list[dict]]で、endpointと購読チャンネルのリストが入っています
        subscribes = (
            channels.ticker(symbol)
            .trades(symbol)
            .candlesticks(symbol, "1m")
            .books(symbol)
            .get()
        )

        for endpoint, send in subscribes.items():
            await client.ws_connect(
                endpoint, send_json=send, hdlr_json=lambda msg, ws: print(msg)
            )

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
