import asyncio
import pybotters_wrapper as pbw


async def main():

    async with pbw.create_client() as client:
        store = pbw.create_binanceusdsm_store()
        api = pbw.create_binanceusdsm_api(client)

        symbol = "BTCUSDT"

        # １個ずつ初期化
        # await store.initialize_position(client)
        # await store.initialize_orderbook(client, symbol=symbol)

        # 並列で初期化
        await asyncio.gather(
            store.initialize_position(client),
            store.initialize_orderbook(client, symbol=symbol)
        )

        # 1メソッドで初期化
        # await store.initialize([
        #     "position",
        #     ("orderbook", {"symbol": symbol})
        # ], client)

        # 任意のエンドポイントを初期化
        await store.initialize([
            api.get("/fapi/v1/klines?symbol=BTCUSDT&interval=1m")
        ], client)

        await asyncio.sleep(1)

        print(store.position.find())
        print(store.orderbook.find()[:5])
        print(store.store.kline.find()[:5])



if __name__ == "__main__":
    asyncio.run(main())