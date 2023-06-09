# pybotters-wrapper

[別ブランチ](https://github.com/ko0hi/pybotters-wrapper/tree/feature/class-architecture)でリファクタ中。

A high-level api collection for pybotters

## Requires

python 3.10 or higher

## Install

```bash
pip install git+https://github.com/ko0hi/pybotters-wrapper
```

## Usage

複数取引所対応の秒速足スイングBOT

```python
import asyncio
from argparse import ArgumentParser

import pandas_ta
import pybotters_wrapper as pbw


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
        await store.subscribe("all", symbol=args.symbol).connect(
            client, auto_reconnect=True, waits=["trades"]
        )

        # 注文APIの設定
        api = pbw.create_api(args.exchange, client, verbose=True)

        # timebarの設定
        tbar = pbw.plugins.timebar(store, seconds=args.bar_seconds)

        # timebar更新のたびに最新のDataFrameを取得するためのqueueを発行
        df_queue = tbar.register_queue()

        # 約定履歴とBarの書き出しを設定
        (
            pbw.plugins.watch_csvwriter(
                store, "execution", f"{logdir}/execution.csv", per_day=True, flush=True
            ),
            pbw.plugins.bar_csvwriter(
                tbar, f"{logdir}/bar.csv", per_day=True, flush=True
            ),
        )

        while True:
            # barの更新があるまで待機
            df = await df_queue.get()

            # rsiの計算
            rsi = df.ta.rsi(length=length).values[-1]
            if rsi > (100 - th):
                trend = -1
            elif rsi < th:
                trend = 1
            else:
                trend = 0

            # 注文
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
    parser.add_argument(
        "--exchange",
        default="bitflyer",
        choices=["binanceusdsm", "binancecoinm", "bitflyer", "bybitinverse", "bybitusdt", "kucoinfutures"]
    )
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

```

## Features

- DataStore周りの取引所間差分吸収
- 注文APIの取引所間差分吸収
- プラグインによる拡張性の提供

### 対応状況

| Exchange            | DataStoreWrapper | Ticker | Trades | Orderbook | Execution | Order | Position | API  |  Plugin  |  
|:--------------------|:----------------:|:------:|:------:|:---------:|:---------:|:-----:|:--------:|:----:|:--------:|
| `binancespot`       |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ❌     |  ✅   |    ✅     | 
| `binanceusdsm`      |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     | 
| `binancecoinm`      |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     | 
| `binanceusdsm_test` |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     | 
| `binancecoinm_test` |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     | 
| `bitbank`           |        ✅         |   ✅    |   ✅    |     ✅     |     ❌     |   ❌   |    ❌     |  ✅   |    ✅     | 
| `bitflyer`          |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     | 
| `bitget`            |        ✅         |   ✅    |   ✅    |     ✅     |    WIP    |  WIP  |   WIP    | WIP  |    ✅     |
| `bybitusdt`         |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     |
| `bybitinverse`      |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     |
| `coincheck`         |        ✅         |   ✅    |   ✅    |     ✅     |     ❌     |   ❌   |    ❌     | WIP  |    ✅     | 
| `gmocoin`           |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     | 🔺^1 |    ✅     |
| `kucoinspot`        |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ❌     |  ✅   |    ✅     | 
| `kucoinfutures`     |        ✅         |   ✅    |   ✅    |     ✅     |     ✅     |   ✅   |    ✅     |  ✅   |    ✅     | 
| `okx`               |        ✅         |   ✅    |   ✅    |     ✅     |    WIP    |  WIP  |   WIP    | WIP  |    ✅     |
| `phemex`            |        ✅         |   ✅    |   ✅    |     ✅     |    WIP    |  WIP  |   WIP    | WIP  |    ✅     |

^1: 建玉別決済のため決済用の独自パラメータあり
