import asyncio
from argparse import ArgumentParser

import pandas_ta  # noqa
import pybotters_wrapper as pbw


def get_feature(df, length=14, th=20):
    """rsi計算用関数"""
    rsi = df.ta.rsi(length=length).values[-1]
    if rsi > (100 - th):
        return -1, rsi
    elif rsi < th:
        return 1, rsi
    else:
        return 0, rsi


async def main(args):
    # loggerの設定
    logdir = pbw.utils.init_logdir(
        args.exchange,
        args.symbol,
        f"bar-{args.bar_seconds}_rsi-{args.rsi_th}-{args.rsi_length}",
    )
    logger = pbw.utils.init_logger(f"{logdir}/log.txt")

    async with pbw.create_client(apis=args.api) as client:
        # ストアの設定
        store = pbw.create_store(args.exchange)

        # APIの設定 (verbose=Trueでリクエストごとにログ出力する）
        api = pbw.create_api(args.exchange, client, verbose=True)

        # timebarの設定
        tbar = pbw.plugins.timebar(store, seconds=args.bar_seconds)
        # 更新のたびに最新のDataFrameを取得するためのqueueを発行
        df_queue = tbar.subscribe()
        # 約定履歴とBarの書き出しを設定
        (
            pbw.plugins.watch_csvwriter(
                store, "execution", f"{logdir}/execution.csv", per_day=True, flush=True
            ),
            pbw.plugins.bar_csvwriter(
                tbar, f"{logdir}/bar.csv", per_day=True, flush=True
            ),
        )

        await store.subscribe("all", symbol=args.symbol).connect(
            client, auto_reconnect=True, waits=["trades"]
        )

        while True:
            # barの更新があるまで待機
            df = await df_queue.get()

            # rsiを計算
            trend, rsi = get_feature(df, args.rsi_length, args.rsi_th)

            logger.info(f"rsi={rsi} trend={trend} position={store.position.summary()}")
            if trend == 1:
                if store.position.size("BUY") == 0:
                    # long entry (short玉を持っていれば決済)
                    size = args.size + store.position.size("SELL")
                    resp = await api.market_order(args.symbol, "BUY", size)
                    logger.info(f"entry buy: {resp.order_id}")
            elif trend == -1:
                if store.position.size("SELL") == 0:
                    # short entry (long玉を持っていれば決済）
                    size = args.size + store.position.size("BUY")
                    resp = await api.market_order(args.symbol, "SELL", size)
                    logger.info(f"entry sell: {resp.order_id}")


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--api", required=True)
    parser.add_argument("--exchange", default="bitflyer")
    parser.add_argument("--symbol", default="FX_BTC_JPY")
    parser.add_argument("--size", default=0.01, type=float)
    parser.add_argument("--bar_seconds", default=5, type=int)
    parser.add_argument("--rsi_th", default=30, type=float)
    parser.add_argument("--rsi_length", default=14, type=int)
    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
