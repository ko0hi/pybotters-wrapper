import asyncio

import pybotters_wrapper as pbw


async def main(exchange="bitflyer"):
    # 取引所個別の設定
    configs = {
        "binancespot": {"symbol": "BTCUSDT", "size": 0.001},
        "binanceusdsm": {
            "symbol": "BTCUSDT",
            "size": 0.001,
        },
        "bitflyer": {
            "symbol": "FX_BTC_JPY",
            "size": 0.01,
        },
        "bybitusdt": {"symbol": "BTCUSDT", "size": 0.001},
        "bybitinverse": {"symbol": "BTCUSD", "size": 1},
        "gmocoin": {"symbol": "BTC_JPY", "size": 0.01},
        "kucoinspot": {"symbol": "BTC-USDT", "size": 0.001},
        "kucoinfutures": {
            "symbol": "XBTUSDTM",
            "size": 1.1,
        },
    }

    assert exchange in configs

    # 取引所独立のロジック
    async with pbw.create_client() as client:
        symbol = configs[exchange]["symbol"]
        size = configs[exchange]["size"]

        api = pbw.create_api(exchange, client, verbose=True)
        store = pbw.create_store(exchange)
        if initialize_config := configs[exchange].get("initialize", None):
            await store.initialize(initialize_config, client=client)
        await store.subscribe(["ticker", "order"], symbol=symbol).connect(
            client, waits=["ticker"]
        )

        # ltpから10％下がったところに買い指値
        price = store.ticker.find()[0]["price"] * 0.9

        # 指値注文
        new_resp = await api.limit_order(symbol, "BUY", price, size)

        # 注文情報受信待機
        await asyncio.sleep(3)

        # 注文状態確認
        orders1 = store.order.find({"id": new_resp.order_id})

        # チェック
        assert len(orders1) == 1
        print(orders1)

        # 注文キャンセル
        await api.cancel_order(symbol, new_resp.order_id)

        # 注文情報受信待機
        await asyncio.sleep(5)
        orders2 = store.order.find({"id": new_resp.order_id})

        # チェック
        assert len(orders2) == 0
        print(orders2)


if __name__ == "__main__":
    asyncio.run(main())
