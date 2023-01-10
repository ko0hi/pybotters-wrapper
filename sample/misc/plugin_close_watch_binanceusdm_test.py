import asyncio
from argparse import ArgumentParser
import pybotters_wrapper as pbw
from pybotters_wrapper.binance.plugins.binanceusdsm_test import CloseWatcher


# 約定するギリギリの価格に注文をopen. 1か2をテストできる。
# 1. 約定を確認 status: OPEN -> FILLED  (その後market orderでpositionを解消)
# 2. 取引ページからキャンセル status: OPEN -> CANCEL

async def get_price(store):
    while True:
        await store.orderbook.wait()
        asks, bids = store.orderbook.sorted().values()
        if len(asks) != 0:
            break
    return asks[0]['price']


async def main(args):
    # logger
    logdir = pbw.utils.init_logdir(args.exchange, args.symbol)
    pbw.utils.init_logger(f"{logdir}/log.txt", rotation="10MB", retention=3)
    pbw.utils.log_command_args(logdir, args)

    async with pbw.create_client(apis=args.api) as client:
        api = pbw.create_api(args.exchange, client, verbose=True)
        store = pbw.create_store(args.exchange)

        # ストアの初期化
        await store.initialize([], client=client)
        # wsでsubscribe開始
        await store.subscribe(["order", "orderbook"], symbol=args.symbol).connect(client, auto_reconnect=True)
        # close監視をスケジューリング
        close_watcher = CloseWatcher(store)
        # ギリギリ約定しない買い注文をエントリー
        price = await get_price(store) - 1
        side = 'BUY'
        size = args.lot
        resp_order = await api.limit_order(args.symbol, side, price, size)
        close_watcher.set(resp_order.order_id)
        # await api.cancel_order(args.symbol, resp_order.order_id)
        while not close_watcher.done():
            await asyncio.sleep(1)
            print(close_watcher.status)
        print(close_watcher.status)
        print(close_watcher.result())

        if close_watcher.status == 'FILLED':
            await asyncio.sleep(5)
            print('EXIT order')
            side = 'SELL'
            await api.market_order(args.symbol, side, size)


if __name__ == "__main__":
    parser = ArgumentParser(description="Simple Market Making Bot")
    parser.add_argument("--api", help="apiキーが入ったJSONファイル", default="apis.json", )
    parser.add_argument("--exchange", default="binanceusdsm_test",
        choices=["binanceusdsm_test", "binancecoinm_test", "binanceusdsm", "binancecoinm", "bitflyer", "bybitinverse",
                 "bybitusdt", "kucoinfutures"])
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--lot", help="注文ロット", default=0.01, type=float)

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
