import asyncio
from argparse import ArgumentParser
from functools import partial

import pybotters
import pybotters_wrapper as pbw
from loguru import logger


def timebar_callback(df, period=10):
    return {
        "u_trigger": df["high"].values[-period:].max(),
        "l_trigger": df["low"].values[-period:].min(),
    }


async def run(
    api: pbw.core.API,
    store: pbw.core.DataStoreWrapper,
    symbol: str,
    side: str,
    size: str,
    take_profit_pct: float,
    stop_loss_pct: float,
):
    # エントリー注文
    watcher = pbw.plugins.execution_watcher(store)
    resp = await api.market_order(symbol, side, size)
    watcher.set(resp.order_id)
    await watcher.wait()
    exec_item = watcher.result()

    # 利確価格・損切価格の設定
    if side == "BUY":
        take_profit = exec_item["price"] * (1 + take_profit_pct)
        stop_loss = exec_item["price"] * (1 - stop_loss_pct)
    else:
        take_profit = exec_item["price"] * (1 - take_profit_pct)
        stop_loss = exec_item["price"] * (1 + stop_loss_pct)

    logger.info(f"run: tp={take_profit} sl={stop_loss} item={exec_item}")

    # 最終価格を監視
    with store.trades.watch() as stream:
        async for change in stream:
            ltp = change.data["price"]
            print(
                f"\rside ltp and triggers: {side} {ltp} {take_profit} {stop_loss}",
                end="",
            )
            # トリガー確認
            if side == "BUY":
                if ltp > take_profit or ltp < stop_loss:
                    break
            else:
                if ltp < take_profit or ltp > stop_loss:
                    break

    # 決済注文
    exit_side = "BUY" if side == "SELL" else "SELL"
    await api.market_order(symbol, exit_side, size)

    logger.info("finish")

    return


async def main(args):
    # loggerの設定
    logdir = pbw.utils.init_logdir(
        args.exchange,
        args.symbol,
    )
    pbw.utils.init_logger(f"{logdir}/log.txt")

    async with pybotters.Client(apis=args.api) as client:
        # ストアの設定
        store = pbw.create_store(args.exchange)

        # APIの設定 (verbose=Trueでリクエストごとにログ出力する）
        api = pbw.create_api(args.exchange, client, verbose=True)

        # timebarの設定
        tbar = pbw.plugins.timebar(
            store,
            seconds=args.bar_seconds,
            callback=[partial(timebar_callback, period=args.trigger_period)],
        )

        # 約定履歴とBarの書き出しを設定
        (
            pbw.plugins.watch_csvwriter(
                store, "execution", f"{logdir}/execution.csv", per_day=True, flush=True
            ),
            pbw.plugins.bar_csvwriter(
                tbar, f"{logdir}/bar.csv", per_day=True, flush=True
            ),
        )

        # websocket接続
        await store.subscribe("all", symbol=args.symbol).connect(
            client, auto_reconnect=True, waits=["trades"]
        )

        run_params = {
            "api": api,
            "store": store,
            "symbol": args.symbol,
            "size": args.size,
            "take_profit_pct": args.take_profit,
            "stop_loss_pct": args.stop_loss,
        }
        with store.trades.watch() as stream:
            async for change in stream:
                ltp = change.data["price"]
                print(f"\rltp and triggers: {ltp} {tbar._}", end="")

                # 最終価格が閾値を超えたらエントリー
                if ltp >= tbar._.get("u_trigger", float("inf")):
                    side = "BUY"
                elif ltp <= tbar._.get("l_trigger", 0):
                    side = "SELL"
                else:
                    side = None

                if side:
                    await run(side=side, **run_params)

                    # 処理中配信された”古い”板情報がキューに溜まっているので全部取り出す
                    while stream._queue.qsize():
                        stream._queue.get_nowait()

                    # 次のエントリーまで指定秒数空ける
                    await asyncio.sleep(args.order_interval)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--api", required=True)
    parser.add_argument("--exchange", default="bitflyer")
    parser.add_argument("--symbol", default="FX_BTC_JPY")
    parser.add_argument("--size", default=0.01, type=float)
    parser.add_argument("--bar_seconds", default=1, type=int)
    parser.add_argument("--trigger_period", default=3, type=int)
    parser.add_argument("--take_profit", default=0.0005, type=float)
    parser.add_argument("--stop_loss", default=0.0005, type=float)
    parser.add_argument("--order_interval", default=60, type=int)
    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
