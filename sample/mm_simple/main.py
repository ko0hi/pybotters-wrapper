from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pybotters.store import DataStore, Item

import asyncio
import loguru
import numpy as np
import pybotters

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
        default_t: float = 1.0,
    ):
        self._store = store
        self._bar = bar
        self._bar_context = bar_period
        self._position_adjust = position_adjust
        self._default_t = default_t
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
        t = self._get_t(side)
        cum_size, price = items[0]["size"], items[0]["price"]
        for i in items:
            if cum_size >= t:
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

    def _get_t(self, side, default=10):
        if side == "SELL":
            t = self._bar.buy_size[-self._bar_context :].mean()
        else:
            t = self._bar.sell_size[-self._bar_context :].mean()

        if np.isnan(t):
            t = self._default_t

        position = self._store.position.find()
        if len(position):
            if position["side"] != side:
                t /= self._position_adjust
            else:
                t *= self._position_adjust
        return t

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


async def market_making(
    api: pbw.common.API,
    store: pbw.common.DataStoreWrapper,
    status: Status,
    symbol: str,
    m: float,
    size: float,
):
    async def _oneside_loop(side: str, size: float):
        # 約定監視をスケジューリング
        execution_watcher = pbw.plugins.execution_watcher(store)

        # 最初のエントリー
        price = status.get_limit_price(side)
        resp_order = await api.limit_order(symbol, side, size, price)
        logger.info(f"[{side} ENTRY] {resp_order}")

        # 注文IDを約定監視にセット
        execution_watcher.set_order_id(resp_order.order_id)

        while not execution_watcher.done():
            await asyncio.sleep(1)

            new_price = status.get_limit_price(side)

            # 指値位置が`m`以上離れていたら更新
            if abs(new_price - price) > m:
                resp_cancel = await api.cancel_order(execution_watcher.order_id)
                if resp_cancel.is_success:
                    logger.info(f"[{side} CANCELED] {execution_watcher.order_id}")
                    resp_order = await api.limit_order(symbol, side, size, new_price)
                    execution_watcher.set_order_id(resp_order.order_id)
                    price = new_price
                    logger.info(f"[{side} UPDATE] {resp_order}")
                else:
                    logger.info(
                        f"[{side} CANCEL FAILED] {resp_cancel} (should be executed)"
                    )
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
                f"[START]\n"
                f"\tsymbol: {symbol}\n"
                f"\tbuy_size: {size + sell_size}\n"
                f"\tsell_size: {size + buy_size}"
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

            logger.info(f"[FINISH] {sell_result['price'] - buy_result['price']}")
            break
        else:
            logger.info(
                f"[WAITING CHANCE] {status.best_ask} - ({status.spread:.4f}) - {status.best_bid}"
            )

            await asyncio.sleep(0.1)


async def main(args):
    # log設定を初期化
    pbw.utils.init_logger("log.txt", rotation="10MB", retention=3)

    async with pybotters.Client(
        apis=args.api_key_json, base_url=pbw.get_base_url(args.exchange)
    ) as client:
        api = pbw.create_api(args.exchange, client)

        store = pbw.create_store(args.exchange)
        store.subscribe("default", symbol=args.symbol)
        await store.connect(client)

        pbw.plugins.execution_watcher(store)
        pbw.plugins.execution_watcher(store)

        tbar = pbw.plugins.timebar(store, seconds=10)

        status = Status(
            store,
            tbar,
            bar_period=args.bar_period,
            position_adjust=args.position_adjust,
            default_t=args.default_t
        )

        while True:
            if not status.is_ready():
                await asyncio.sleep(1)
                continue

            await market_making(
                api,
                store,
                status,
                args.symbol,
                args.m,
                args.lot,
            )

            await asyncio.sleep(args.interval)




if __name__ == "__main__":

    parser = ArgumentParser(description="pybotters x asyncio x magito MM")
    parser.add_argument(
        "--api_key_json",
        help="apiキーが入ったJSONファイル",
        default="apis.json",
    )
    parser.add_argument("--exchange", default="ftx")
    parser.add_argument("--symbol", default="BTC-PERP", help="取引通貨")
    parser.add_argument("--lot", default=0.0001, type=float, help="注文サイズ")
    parser.add_argument("--m", default=5, type=float, help="指値更新幅")
    parser.add_argument("--bar_period", default=10, type=int, help="成行量推定に使うバーの本数")
    parser.add_argument(
        "--position_adjust", default=1.5, type=float, help="ポジションを持っている場合、反対方向の成行をk倍する"
    )
    parser.add_argument("--default_t", default=1, type=float, help="デフォルトの成行推定量")
    parser.add_argument("--interval", default=5, type=int, help="マーケットメイキングサイクルの間隔")

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt as e:
        pass
