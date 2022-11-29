import asyncio
import time
import uuid
from argparse import ArgumentParser
from collections import deque

import pandas_ta
import pybotters
import pybotters_wrapper as pbw
from loguru import logger


class HigetoriBot:
    def __init__(
        self,
        api: pbw.common.API,
        store: pbw.common.DataStoreWrapper,
        symbol: str,
        side: str,
        size: float,
        limit_distance: float,
        update_distance: float,
        take_profit_distance: float,
        stop_loss_distance: float,
        update_patience_seconds: int,
        window: int,
        watcher_interval: float = 0.33,
    ):
        self._api = api
        self._store = store
        self._symbol = symbol
        self._side = side
        self._window = window
        self._size = size
        self._limit_distance = limit_distance
        self._update_distance = update_distance
        self._take_profit_distance = take_profit_distance
        self._stop_loss_distance = stop_loss_distance
        self._update_patience_seconds = update_patience_seconds
        self._watcher_interval = watcher_interval
        self._last = None
        self._window_deque = deque(maxlen=window)
        self._watch_trade_task = asyncio.create_task(self._watch_trade())

    async def _watch_trade(self):
        with self._store.trades.watch() as stream:
            async for change in stream:
                self._last = change.data
                self._window_deque.append(change.data["price"])

    async def run(self, id=None):
        id = id or uuid.uuid4()
        logger.info(f"start entry: {id}")

        limit_price = self.get_limit_price()
        watcher = pbw.plugins.execution_watcher(self._store)
        resp = await self._api.limit_order(
            self._symbol, self._side, limit_price, self._size
        )
        watcher.set(resp.order_id)

        while watcher is None or not watcher.done():
            await asyncio.sleep(self._watcher_interval)
            if self._last is None:
                continue

            order = self._store.order.get(
                {"symbol": self._symbol, "id": watcher.order_id}
            )

            logger.info(f"{id} {self._side} {watcher.order_id} {limit_price}")

            if order and self._should_update(order["price"]):
                await asyncio.sleep(self._update_patience_seconds)
                if not watcher.done():
                    logger.info("update order")
                    await self._api.cancel_order(order["symbol"], order["id"])
                    logger.info(f"[{id}] cancel order: {order}")
                    limit_price = self.get_limit_price()
                    watcher = pbw.plugins.execution_watcher(self._store)
                    resp = await self._api.limit_order(
                        self._symbol, self._side, limit_price, self._size
                    )
                    watcher.set(resp.order_id)
                    logger.info(f"[{id}] new order: {limit_price} {resp}")

        logger.info(f"start exit: {id}")
        exec_item = watcher.result()
        exit_side = "BUY" if self._side == "SELL" else "SELL"
        while True:
            await asyncio.sleep(self._watcher_interval)
            if self._should_exit(exec_item["price"]):
                await self._api.market_order(self._symbol, exit_side, exec_item["size"])
                break
        logger.info(f"finish: {id}")

    async def run_forever(self, interval=5):
        while True:
            await self.run()
            await asyncio.sleep(interval)

    def get_limit_price(self, side=None):
        side = side or self._side
        center = self.center
        if side == "BUY":
            return center * (1 - self._limit_distance)
        else:
            return center * (1 + self._limit_distance)

    def _distance_from_ltp(self, price: float) -> float:
        return price / self._last["price"] - 1

    def _should_update(self, price) -> bool:
        assert self._last is not None
        cur_distance = abs(price / self._last["price"] - 1)
        return abs(cur_distance - self._limit_distance) > self._update_distance

    def _should_exit(self, entry_price) -> bool:
        profit = abs(self._last["price"] / entry_price - 1)
        logger.error(profit)
        return profit > self._stop_loss_distance or profit > self._take_profit_distance

    @property
    def center(self):
        if self._last is None:
            return self._store.trades.find()[-1]["price"]
        else:
            return sum(self._window_deque) / len(self._window_deque)


async def main(args):
    # loggerの設定
    logdir = pbw.utils.init_logdir(
        args.exchange,
        args.symbol,
    )
    logger = pbw.utils.init_logger(f"{logdir}/log.txt")

    async with pybotters.Client(apis=args.api) as client:
        # ストアの設定
        store = pbw.create_store(args.exchange)
        await store.subscribe("all", symbol=args.symbol).connect(
            client, auto_reconnect=True, waits=["trades"]
        )

        api = pbw.create_api(args.exchange, client, verbose=True)

        # 約定履歴とBarの書き出しを設定
        writers = (
            pbw.plugins.wait_csvwriter(
                store, "order", f"{logdir}/order.csv", per_day=True, flush=True
            ),
            pbw.plugins.watch_csvwriter(
                store, "execution", f"{logdir}/execution.csv", per_day=True, flush=True
            ),
        )

        params = {
            "api": api,
            "store": store,
            "symbol": args.symbol,
            "size": args.size,
        }

        if args.config is None:

            await HigetoriBot(
                **params,
                side=args.side,
                limit_distance=args.limit_distance,
                update_distance=args.update_distance,
                take_profit_distance=args.take_profit_distance,
                stop_loss_distance=args.stop_loss_distance,
                update_patience_seconds=args.update_patience_seconds,
                window=args.window,
            ).run_forever()

        else:
            config = pbw.utils.read_json(args.config)
            tasks = [HigetoriBot(**params, **c).run_forever() for c in config]
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--api", required=True)
    parser.add_argument("--exchange", default="bybitusdt")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--size", default=0.001, type=float)
    parser.add_argument("--side", default="BUY")
    parser.add_argument("--window", help="中心価格を決める約定履歴数", default=100, type=int)
    parser.add_argument(
        "--limit_distance",
        help="中心価格からn％離れたとろに指値を配置（0~1)",
        default=0.002,
        type=float,
    )
    parser.add_argument(
        "--update_distance",
        help="注文指値価格と設定指値価格の位置（％）の差がkを超えたら指値更新（0~1）",
        default=0.0005,
        type=float,
    )
    parser.add_argument(
        "--take_profit_distance", help="利確幅（0~1）", default=0.002, type=float
    )
    parser.add_argument(
        "--stop_loss_distance", help="損切幅（0~1）", default=0.001, type=float
    )
    parser.add_argument(
        "--update_patience_seconds",
        help="注文更新フラグが立った後、一定秒数待機したのちに更新する",
        default=15,
        type=int,
    )
    parser.add_argument(
        "--config", help="コンフィグファイル（複数のコンフィグで同時に動かしたい時に使用）", default=None
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
