import asyncio
import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "FX_BTC_JPY"

    async with pybotters.Client() as client:
        channels = pbw.bitflyer.bitFlyerWebsocketChannels()
        subscribes = (
            channels.lightning_board(symbol)
            .lightning_board_snapshot(symbol)
            .lightning_executions(symbol)
            .lightning_ticker(symbol)
            .child_order_events()
            .parent_order_events()
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
