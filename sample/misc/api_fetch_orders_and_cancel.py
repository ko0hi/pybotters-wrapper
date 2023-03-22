import asyncio

import pybotters_wrapper as pbw


async def main(exchange="binancecoinm"):
    # 取引所個別の設定
    configs = {
        "binancespot": {"symbol": "BTCUSDT", "size": 0.001},
        "binanceusdsm": {"symbol": "BTCUSDT", "size": 0.001},
        "binancecoinm": {"symbol": "BTCUSD_PERP", "size": 1},
        "bitflyer": {"symbol": "FX_BTC_JPY", "size": 0.01},
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
        order_resp = await api.limit_order(symbol, "BUY", price, size)

        # アクティブ注文取得
        fetch_resp_before = await api.fetch_orders(symbol)

        # チェック
        assert len(fetch_resp_before.orders) == 1
        assert fetch_resp_before.orders[0]["id"] == order_resp.order_id
        print(fetch_resp_before.orders)

        # 注文キャンセル
        await api.cancel_order(symbol, fetch_resp_before.orders[0]["id"])

        # アクティブ注文際取得
        fetch_resp_after = await api.fetch_orders(symbol)

        # チェック
        assert len(fetch_resp_after.orders) == 0
        print(fetch_resp_after.orders)


if __name__ == "__main__":
    asyncio.run(main())
