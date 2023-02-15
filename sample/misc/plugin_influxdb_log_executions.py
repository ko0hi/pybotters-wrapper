import asyncio

import pybotters_wrapper as pbw


async def main():
    async with pbw.create_client() as client:
        symbol = "FX_BTC_JPY"
        store, api = pbw.create_store_and_api("bitflyer", client, sandbox=True)
        await store.subscribe("public", symbol=symbol).connect(
            client, waits=["orderbook"]
        )

        # localhost:8086でアクセスできる状態になっている必要あり。
        # https://github.com/ko0hi/pybotters-wrapper-containers を起動している想定
        # bucketはなければ自動で作られる
        bucket_name = "influxdb_sample"
        influx = pbw.plugins.influxdb(
            "pbw",
            "pbw",
            bucket_name,
        )

        # 約定履歴を記録
        # 以下のflux queryと合わせることで損益グラフを出力できる（bucket_name・measurementの変更が必要）
        # https://github.com/ko0hi/pybotters-wrapper-containers/blob/main/flux/pnl_from_trade_history.flux
        asyncio.create_task(
            influx.watch_and_write_executions(
                store, measurement="bf_sandbox_executions"
            )
        )

        await api.market_order(symbol, "BUY", 0.01)
        await asyncio.sleep(1)
        await api.market_order(symbol, "SELL", 0.01)

        await asyncio.sleep(3)

        tables = (
            influx.client(sync=True)
            .query_api()
            .query(f'from(bucket: "{bucket_name}") ' f"|> range(start: 0) ")
        )

        for t in tables:
            for r in t:
                print(r.values)


if __name__ == "__main__":
    asyncio.run(main())
