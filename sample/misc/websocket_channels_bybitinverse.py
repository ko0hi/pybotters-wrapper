import asyncio
import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "BTCUSD"

    async with pybotters.Client() as client:
        channels = pbw.bybit.BybitInverseWebsocketChannels()
        subscribes = (
            channels.ticker(symbol)
            .trades(symbol)
            .orderbook(symbol)
            .kline_v2(symbol)
            .liquidation()
            .insurance()
            .order()
            .position()
            .execution()
            .wallet()
            .stop_order()
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
