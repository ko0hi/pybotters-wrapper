from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pybotters.store import DataStore, Item

import asyncio
import loguru
import numpy as np
import pybotters

from pybotters.ws import Auth


async def kucoin(ws: aiohttp.ClientWebSocketResponse):
    while not ws.closed:
        print("H")
        await ws.send_str(f'{{"id": "{uuid.uuid4()}", "type": "ping"}}')
        await asyncio.sleep(5)

Auth.kucoin = kucoin

from argparse import ArgumentParser
from loguru import logger
from functools import partial

import pybotters_wrapper as pbw


class Status:
    def __init__(
        self,
        store: pbw.common.DataStoreWrapper,
        bar: pbw.plugins.bar.BarStreamDataFrame,
        bar_period: int = 5,
        position_adjust: float = 1.5,
        default_market_amount: float = 1.0,
        market_amount_weight: float = 1,
    ):
        self._store = store
        self._bar = bar
        self._bar_context = bar_period
        self._position_adjust = position_adjust
        self._default_market_amount = default_market_amount
        self._market_amount_weight = market_amount_weight
        self._asks = None
        self._bids = None

        asyncio.create_task(self._auto_update_board())

    async def _auto_update_board(self):
        """板情報の自動更新タスク"""
        while True:
            await self._store.orderbook.wait()
            self._asks, self._bids = self._store.orderbook.sorted().values()

    def get_limit_price(self, side: str, d: int = 1):
        """注文サイズの累積量が``t``を超えたところに``d``だけ離して指値をだす。
        :param str side: ask or bid
        :param int d: 参照注文からのマージン
        :return: 指値
        """
        items = self._get_items(side)
        market_amount = self._get_market_amount(side)
        cum_size, price = items[0]["size"], items[0]["price"]
        for i in items:
            if cum_size >= market_amount:
                return int(price + d if side == "SELL" else price - d)
            price = i["price"]
            cum_size += i["size"]
        # 最後までthresholdを満たさなかった場合、一番後ろの注文と同じ額
        return int(items[-1]["price"])

    def positions(self, side: str):
        """保有ポジションリスト。
        :param str side: BUY or SELL
        :return: ポジションのlist
        """
        positions = self._store.position.find({"side": side})
        return positions

    def position_size(self, side):
        """保有ポジションサイズ。
        :param str side: BUY or SELL
        :return: ポジションサイズ
        """
        positions = self.positions(side)
        return positions[0]["size"] if len(positions) else 0

    def ok_entry(self):
        """エントリー条件ロジック。何かエントリー条件を定めたい場合はここを書く。

        :return:
        """
        return True

    def _get_items(self, side):
        return self._asks if side == "SELL" else self._bids

    def _get_market_amount(self, side):
        if side == "SELL":
            market_amount = self._bar.buy_size[-self._bar_context :].mean()
        else:
            market_amount = self._bar.sell_size[-self._bar_context :].mean()

        if np.isnan(market_amount):
            market_amount = self._default_market_amount

        market_amount *= self._get_weight()

        position = self._store.position.find()
        if len(position):
            if position[0]["side"] != side:
                market_amount /= self._position_adjust
            else:
                market_amount *= self._position_adjust
        return market_amount

    def _get_weight(self):
        return self._market_amount_weight

    @property
    def best_ask(self):
        return int(self._asks[0]["price"])

    @property
    def best_bid(self):
        return int(self._bids[0]["price"])

    @property
    def spread(self):
        return (self.best_ask - self.best_bid) / self.best_bid

    def is_ready(self):
        return self._asks is not None and self._bids is not None

    def summary(self):
        return {
            "sell_price": self.get_limit_price("SELL"),
            "buy_price": self.get_limit_price("BUY"),
            "best_ask": self.best_ask,
            "best_bid": self.best_bid,
            "sell_t": self._get_market_amount("SELL"),
            "buy_t": self._get_market_amount("BUY"),
        }


async def market_making(
    api: pbw.common.API,
    store: pbw.common.DataStoreWrapper,
    status: Status,
    symbol: str,
    margin: float,
    size: float,
):
    async def _oneside_loop(side: str, size: float):
        # 約定監視をスケジューリング
        execution_watcher = pbw.plugins.execution_watcher(store)

        # 最初のエントリー
        price = status.get_limit_price(side)
        resp_order = await api.limit_order(symbol, side, price, size)

        # 注文IDを約定監視にセット
        execution_watcher.set(resp_order.id)

        while not execution_watcher.done():
            # 1秒間隔で指値更新チェック
            await asyncio.sleep(5)

            new_price = status.get_limit_price(side)

            # 指値位置が`m`以上離れていたら更新
            if abs(new_price - price) > margin:
                resp_cancel = await api.cancel_order(symbol, execution_watcher.order_id)
                if resp_cancel.status == 200:
                    # 約定監視をリスケジューリング
                    # 古いやつを
                    execution_watcher = pbw.plugins.execution_watcher(store)
                    resp_order = await api.limit_order(symbol, side, new_price, size)
                    execution_watcher.set(resp_order.id)
                    price = new_price
                else:

                    continue

        # 約定
        execution_item = execution_watcher.result()
        logger.info(f"[{side} FINISH] {execution_item}")
        return execution_item

    while True:
        if status.ok_entry():
            # 現在のポジションから端数を取得
            buy_size = status.position_size("BUY")
            sell_size = status.position_size("SELL")

            logger.info(
                f"[START] "
                f"symbol: {symbol} "
                f"buy_size: {size + sell_size} "
                f"sell_size: {size + buy_size} "
            )

            buy_result, sell_result = await asyncio.gather(
                _oneside_loop(
                    "BUY",
                    size + sell_size,
                ),
                _oneside_loop(
                    "SELL",
                    size + buy_size,
                ),
            )

            import sys
            sys.exit(1)

            logger.info(f"[FINISH] {sell_result['price'] - buy_result['price']}")
            break
        else:
            logger.info(
                f"[WAITING CHANCE] {status.best_ask} - ({status.spread:.4f}) - {status.best_bid}"
            )

            await asyncio.sleep(0.1)


import rich


async def watch_position(position):
    with position.watch() as stream:
        async for msg in stream:
            rich.print(msg)
            logger.info(f"[POSITION] {position.find()}")


async def main(args):
    # log設定を初期化
    pbw.utils.init_logger("log.txt", rotation="10MB", retention=3)

    initialize_configs = {
        "bitflyer": [],
        "kucoinfutures": ["token_private", "position"],
        "binanceusdsm": ["token_private"],
    }

    async with pbw.create_client(args.exchange, apis=args.apis) as client:
        api = pbw.create_api(args.exchange, client, verbose=True)
        store = pbw.create_store(args.exchange)
        await store.initialize(initialize_configs[args.exchange], client=client)
        await store.subscribe("default", symbol=args.symbol).connect(client)

        tbar = pbw.plugins.timebar(store, seconds=10)

        status = Status(
            store,
            tbar,
            bar_period=args.bar_period,
            position_adjust=args.position_adjust,
            default_market_amount=args.default_market_amount,
            market_amount_weight=args.market_amount_weight,
        )

        asyncio.create_task(watch_position(store.position))

        while True:
            if not status.is_ready():
                await asyncio.sleep(1)
                continue

            if args.dry_run:
                logger.info(status.summary())

            else:
                await market_making(
                    api,
                    store,
                    status,
                    args.symbol,
                    args.update_margin,
                    args.lot,
                )

            await asyncio.sleep(args.interval)


if __name__ == "__main__":

    parser = ArgumentParser(description="Simple Market Making Bot")
    parser.add_argument(
        "--apis",
        help="apiキーが入ったJSONファイル",
        default="apis.json",
    )
    parser.add_argument(
        "--exchange",
        help="取引所",
        choices=["bitflyer", "binanceusdsm", "kucoinfutures"],
        required=True,
    )
    parser.add_argument("--symbol", help="取引通貨", required=True)
    parser.add_argument("--lot", help="注文ロット", default=0.01, type=float)
    parser.add_argument("--update_margin", help="指値更新幅", default=1000, type=float)
    parser.add_argument("--bar_period", help="成行量推定に使うバーの本数", default=5, type=int)
    parser.add_argument(
        "--position_adjust", help="ポジションを持っている場合、反対方向の成行をk倍する", default=1.5, type=float
    )
    parser.add_argument(
        "--default_market_amount",
        help="デフォルトの成行推定量（Barが貯まるまでこちらを使う）",
        default=10,
        type=float,
    )
    parser.add_argument(
        "--market_amount_weight", help="成行推定量にかけるウェイト", default=1, type=float
    )
    parser.add_argument("--interval", help="マーケットメイキングサイクルの間隔", default=5, type=int)
    parser.add_argument("--dry_run", help="発注しない", action="store_true")

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt as e:
        pass
