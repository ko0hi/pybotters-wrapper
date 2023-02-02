import asyncio

import pybotters_wrapper as pbw


async def main(exchange="binancespot"):
    # 取引所個別の設定
    configs = {
        "binancespot": {"symbol": "BTCUSDT", "size": 0.001},
        "binanceusdsm": {"symbol": "BTCUSDT", "size": 0.001},
        "binancecoinm": {"symbol": "BTCUSD_PERP", "size": 1},
        "gmocoin": {"symbol": "BTC_JPY", "size": 0.01},
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

        # ltpから10％上がったところをトリガーにして逆指値
        trigger = store.ticker.find()[0]["price"] * 1.1

        # 指値注文
        if exchange == "binancespot":
            try:
                new_resp = await api.stop_market_order(symbol, "BUY", size, trigger)
            except RuntimeError as e:
                print(e)
                return
        else:
            new_resp = await api.stop_market_order(symbol, "BUY", size, trigger)

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
