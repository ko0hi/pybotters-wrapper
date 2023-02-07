from __future__ import annotations

from typing import TYPE_CHECKING

import pybotters

if TYPE_CHECKING:
    pass

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
    api: pbw.core.API,
    store: pbw.core.DataStoreWrapper,
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
        # ExecutionWatcherはsetが呼ばれるまで約定受信メッセージを待機させるので、api response
        # よりも先に約定メッセージが届いても問題ない
        execution_watcher.set(resp_order.order_id)

        while not execution_watcher.done():
            # 1秒間隔で指値更新チェック
            await asyncio.sleep(1)

            new_price = status.get_limit_price(side)

            # 指値位置が`m`以上離れていたら更新
            if abs(new_price - price) > margin:
                resp_cancel = await api.cancel_order(symbol, execution_watcher.order_id)
                if resp_cancel.is_success():
                    # 約定監視をリスケジューリング
                    # ExecutionWatcherは使い回し不可の使用になっているので新しいものを作る
                    execution_watcher = pbw.plugins.execution_watcher(store)
                    resp_order = await api.limit_order(symbol, side, new_price, size)
                    execution_watcher.set(resp_order.order_id)
                    price = new_price
                else:
                    # キャンセル失敗＝約定
                    continue

        # 約定
        execution_item = execution_watcher.result()
        logger.info(f"[{side} FINISH] {execution_item}")
        return execution_item

    # 現在のポジションから端数を取得
    buy_size = store.position.size("BUY")
    sell_size = store.position.size("SELL")

    logger.info(
        f"[START] symbol: {symbol} "
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

    # ざっくり損益計算
    pnl = (sell_result["price"] - buy_result["price"]) * size
    logger.info(f"[FINISH] {pnl}")


async def main(args):
    # logdir=`/logs/${args.exchange}/${args.symbol}/${datetime.utcnow()}`
    logdir = pbw.utils.init_logdir(args.exchange, args.symbol)
    # logファイルの設定
    pbw.utils.init_logger(f"{logdir}/log.txt", rotation="10MB", retention=3)
    # commandを保存
    pbw.utils.log_command_args(logdir, args)

    # 取引所別の`initialize`メソッドの引数
    # Note: 現状以下の理由からinitialize用の共通インターフェースは用意していない
    #
    #  1. 取引所ごとに叩くエンドポイントが異なり、また、エンドポイントが必要とするパラメーターも一致していない
    #  2. pybottersもinitializeは取引所別の実装であり、DataStoreManagerもインターフェースを持っていない
    #  3. サポートされているストアも多くはない
    #
    initialize_configs = {
        "bitflyer": [],
        "bybitusdt": [],
        "bybitinverse": [],
        "kucoinfutures": ["token_private", "position"],
        "binanceusdsm": ["token_private", ("orderbook", {"symbol": "BTCUSDT"})],
    }

    # clientの初期化：exchangeにあったbase_urlを埋めてくれる。ただし複数のエンドポイントがある場合は
    # base_urlはNoneのまま（例：GMOCoinのpublic/private endpoints）
    async with pybotters.Client(apis=args.apis) as client:
        store, api = pbw.create_store_and_api(
            args.exchange, client, sandbox=args.sandbox
        )

        # pluginの設定
        # データの取りこぼしが起こりうるため、pluginの設定はstore.initialize・store.connectの
        # 前に行う必要がある。

        # watch_csvwriterは,watchメソッドでストアの更新を監視し、挿入（i.e., _insert メソッド
        # が呼ばれる）があるたびに指定カラムの値（デフォルトは全カラム）を書き出す。約定履歴などデータを
        # 順次書き出していきたい時に使う。
        execution_writer = pbw.plugins.watch_csvwriter(
            store, "execution", f"{logdir}/execution.csv"
        )

        # wait_csvwriterはwaitメソッドでストアの更新を監視し、更新があるたびに指定カラムの値（デフォ
        # ルトは全カラム）を１アイテム１行で書き出す。注文やポジションなど定期的なスナップショットを保存
        # したい時に使う。
        order_writer = pbw.plugins.wait_csvwriter(
            store,
            "order",
            f"{logdir}/order.csv",
        )

        # 約定履歴からtimebarを作成するプラグイン
        tbar = pbw.plugins.timebar(store, seconds=args.bar_seconds)

        # 状態管理クラスの初期化
        status = Status(
            store,
            tbar,
            bar_num=args.bar_num,
            position_adjust=args.position_adjust,
            market_amount_default=args.market_amount_default,
            market_amount_weight=args.market_amount_weight,
        )

        pnl = pbw.plugins.pnl(store, args.symbol)

        # ストアの初期化
        await store.initialize(initialize_configs[args.exchange], client=client)

        # websocket接続
        # "default"とするとNormalizedStore（"ticker",  "trades", "orderbook", "order",
        # "execution", "position"）に対応するチャンネルを全て購読する
        # `auto_reconnect=True`で切断された場合に再度同じチャンネルを購読し直す
        await store.subscribe("all", symbol=args.symbol).connect(
            client, auto_reconnect=True
        )

        # メインループ
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

                    logger.info(pnl.status())

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
        choices=[
            "bitflyer",
            "binanceusdsm",
            "kucoinfutures",
            "bybitusdt",
            "bybitinverse",
        ],
        required=True,
    )
    parser.add_argument("--symbol", help="取引通貨", required=True)
    parser.add_argument("--lot", help="注文ロット", default=0.01, type=float)
    parser.add_argument("--update_margin", help="指値更新幅", default=1000, type=float)
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
    parser.add_argument("--sandbox", help="sandbox環境での実行", action="store_true")

    args = parser.parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
