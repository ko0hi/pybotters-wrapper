from __future__ import annotations

import asyncio
from argparse import ArgumentParser

import numpy as np
import pybotters_wrapper as pbw
from loguru import logger


class Status:
    def __init__(
        self,
        store: pbw.core.DataStoreWrapper,
        bar: pbw.plugins.bar.BarStreamDataFrame,
        bar_num: int = 5,
        position_adjust: float = 1.5,
        market_amount_default: float = 1.0,
        market_amount_weight: float = 1,
    ):
        self._store = store
        self._bar = bar
        self._bar_num = bar_num
        self._position_adjust = position_adjust
        self._market_amount_default = market_amount_default
        self._market_amount_weight = market_amount_weight
        self._asks = None
        self._bids = None

        asyncio.create_task(self._auto_update_board())

    async def _auto_update_board(self):
        while True:
            await self._store.orderbook.wait()
            self._asks, self._bids = self._store.orderbook.sorted().values()

    def get_limit_price(self, side: str, d: int = 1):
        """注文サイズの累積量が推定成行量を超えたところに``d``だけ離して指値をだす。"""
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

    def ok_entry(self):
        """エントリー条件ロジック。何かエントリー条件を定めたい場合はここを書く。"""
        return True

    def _get_items(self, side):
        return self._asks if side == "SELL" else self._bids

    def _get_market_amount(self, side):
        # 直近N本文のバーにおける平均ボリュームを基本成行量とする
        if side == "SELL":
            market_amount = self._bar.buy_size[-self._bar_num :].mean()

        else:
            market_amount = self._bar.sell_size[-self._bar_num :].mean()

        # N本分のバーが埋まりきってない場合はデフォルト値
        if np.isnan(market_amount):
            market_amount = self._market_amount_default

        # weightをかける
        market_amount *= self._get_weight()

        # ポジション保有時に成行推定量を調整する
        # 同サイドの注文（追玉）には多めに見積り、逆サイドの注文（決済）には少なめに見積ることで
        # 簡易的な在庫調整
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
    api: pbw.gmocoin.GMOCoinAPI,
    store: pbw.gmocoin.GMOCoinDataStoreWrapper,
    status: Status,
    symbol: str,
    margin: float,
    size: float,
):
    async def _oneside_loop(side: str, size: float):

        # GMOは建玉別決済で新規と決済で注文エンドポイントが異なる。
        # pybotters-wrapperではデフォルトは新規注文用の"/private/v1/order"エンドポイント、
        # close=Trueフラグを与えると、一括決済用の"/private/v1/closeBulkOrder"エンドポイントを
        # 叩きにいく。ここでは逆サイドの建玉を持っていれば後者を用いるようにしている。
        exit_side = "BUY" if side == "SELL" else "SELL"
        close = store.position.size(exit_side) > 0

        execution_watcher = pbw.plugins.execution_watcher(store)

        price = status.get_limit_price(side)
        resp_order = await api.limit_order(symbol, side, price, size, close=close)

        execution_watcher.set(resp_order.order_id)

        while not execution_watcher.done():
            await asyncio.sleep(1)

            new_price = status.get_limit_price(side)

            if abs(new_price - price) > margin:
                resp_cancel = await api.cancel_order(symbol, execution_watcher.order_id)
                if resp_cancel.is_success():
                    execution_watcher = pbw.plugins.execution_watcher(store)
                    resp_order = await api.limit_order(
                        symbol, side, new_price, size, close=close
                    )
                    execution_watcher.set(resp_order.order_id)
                    price = new_price
                else:
                    continue

        execution_item = execution_watcher.result()
        logger.info(f"[{side} FINISH] {execution_item}")
        return execution_item

    buy_size = store.position.size("BUY")
    sell_size = store.position.size("SELL")

    logger.info(
        f"[START] symbol: {symbol} "
        f"buy_size: {size + sell_size} "
        f"sell_size: {size + buy_size} "
    )

    buy_result, sell_result = await asyncio.gather(
        _oneside_loop("BUY", size),
        _oneside_loop("SELL", size),
    )

    pnl = (sell_result["price"] - buy_result["price"]) * size
    logger.info(f"[FINISH] {pnl}")


async def main(args):
    logdir = pbw.utils.init_logdir("gmocoin", args.symbol)
    pbw.utils.init_logger(f"{logdir}/log.txt", rotation="10MB", retention=3)
    pbw.utils.log_command_args(logdir, args)

    async with pbw.create_client(apis=args.api) as client:
        api = pbw.create_gmocoin_api(client, verbose=True)
        store = pbw.create_gmocoin_store()
        await store.initialize([("position", {"symbol": args.symbol})], client)

        await store.subscribe("all", symbol=args.symbol).connect(
            client, auto_reconnect=True
        )

        pbw.plugins.watch_csvwriter(store, "execution", f"{logdir}/execution.csv")
        pbw.plugins.wait_csvwriter(store, "order", f"{logdir}/order.csv")

        tbar = pbw.plugins.timebar(store, seconds=args.bar_seconds)

        status = Status(
            store,
            tbar,
            bar_num=args.bar_num,
            position_adjust=args.position_adjust,
            market_amount_default=args.market_amount_default,
            market_amount_weight=args.market_amount_weight,
        )

        while True:
            if not status.is_ready():
                logger.info("status has not been ready ...")
                await asyncio.sleep(1)
                continue

            if args.dry_run:
                logger.info(status.summary())

            else:
                if status.ok_entry():
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
    parser.add_argument("--api", help="apiキーが入ったJSONファイル", required=True)
    parser.add_argument("--symbol", help="取引通貨", default="BTC_JPY", choices=["BTC_JPY"])
    parser.add_argument("--lot", help="注文ロット", default=0.01, type=float)
    parser.add_argument("--update_margin", help="指値更新幅", default=2000, type=float)
    parser.add_argument("--bar_seconds", help="バーの秒足", default=10, type=int)
    parser.add_argument("--bar_num", help="成行量推定に使うバーの本数", default=5, type=int)
    parser.add_argument(
        "--position_adjust",
        help="ポジション保有時、ポジションと同サイドの成行推定量をk倍・反対方向の成行を1/k倍する",
        default=1.5,
        type=float,
    )
    parser.add_argument(
        "--market_amount_default",
        help="デフォルトの成行推定量（Barが貯まるまでこちらを使う）",
        default=1,
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
    except KeyboardInterrupt:
        pass
