import asyncio

import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "BTCUSDT"

    async with pybotters.Client() as client:
        channels = pbw.bybit.BybitUSDTWebsocketChannels()
        subscribes = (
            channels
            # .ticker(symbol)
            # .trades(symbol)
            # .orderbook(symbol)
            # .candle(symbol)
            # .liquidation(symbol)
            .order()
            .position()
            # .execution()
            # .wallet()
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
