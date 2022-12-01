import asyncio
import pybotters
import pybotters_wrapper as pbw


async def main():
    symbol = "FX_BTC_JPY"

    async with pybotters.Client() as client:
        endpoint = "wss://ws.lightstream.bitflyer.com/json-rpc"
        send = [
            {
                "method": "subscribe",
                "params": {"channel": f"lightning_ticker_{symbol}"},
                "id": 1,
            },
            {
                "method": "subscribe",
                "params": {"channel": f"lightning_executions_{symbol}"},
                "id": 2,
            },
            {
                "method": "subscribe",
                "params": {"channel": f"lightning_board_snapshot_{symbol}"},
                "id": 3,
            },
            {
                "method": "subscribe",
                "params": {"channel": f"lightning_board_{symbol}"},
                "id": 4,
            },
            {
                "method": "subscribe",
                "params": {"channel": "child_order_events"},
                "id": 5,
            },
        ]

        hdlr = lambda msg, ws: print(msg)

        connection = pbw.core.WebsocketConnection(endpoint, send, hdlr)
        await connection.connect(client, auto_reconnect=True)

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
