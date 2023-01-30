import asyncio

import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "XBTUSDTM"

    async with pybotters.Client() as client:
        channels = pbw.kucoin.KuCoinFuturesWebsocketChannels()
        subscribes = (
            channels.contract_market_ticker_v2(symbol)
            .contract_market_execution(symbol)
            .contract_market_level2depth50(symbol)
            .contract_market_trade_orders()
            .contract_position(symbol)
            .get()
        )

        store = pbw.create_store("kucoinfutures")
        await store.initialize(["token"], client)

        for endpoint, send in subscribes.items():
            await client.ws_connect(
                store.endpoint, send_json=send, hdlr_json=lambda msg, ws: print(msg)
            )

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
