# Simple Market Making Bot

## 使い方

```bash
python main.py \
  --api api.json \
  --exchange bitflyer \
  --symbol FX_BTC_JPY \
  --lot 0.01 \
  --bar_seconds 10 \
  --bar_num 5 \
  --market_amount_weight 3 \
  --update_margin 2000
```

成行推定量と板の厚みに応じて上下に指値を出すシンプルなマーケットメイキングボットです。

上の例だと以下の設定で動きます：

```
- 取引所・シンボル・ロットは`bitflyer`・`FX_BTC_JPY`・`0.01`
- `--bar_seconds 10`: 10秒足の
- `--bar_num 5`： 直近５本分のボリュームを成行量のベースとして
- `--market_amount_weight 3`： そこに３をかけたものを推定成行量として、板状で累積注文量が推定成行量に達するところに指値を出す。
- `--update_margin 2000`：指値の価格が2000以上離れたら指値を出し直す
```
買い・売りの両方が約定するまでを１セットとして直列に動きます（前のセットが終わるまで、次セットにはいきません）。

対応取引所は `bitflyer`・`binanceusdsm`・`kucoinfutures`です。

api.jsonは以下のフォーマットになっている必要があります。

```json
{
  "binance": [
    "xxx",
    "xxx"
  ],
  "bitflyer": [
    "xxx",
    "xxx"
  ],
  "kucoinfuture": [
    "xxx",
    "xxx",
    "xxx"
  ]
}
```


### GMOCoin

GMOは建玉別決済のため基本的に他取引所と同じ注文スクリプトで動かすことはできません。

`main_gmo.py`はGMO用に修正を入れたものです。とはいえ異なっている箇所は下記のところだけで、`close`という決済注文フラグを渡すようになっているのみです。

```python
# GMOは建玉別決済で新規と決済で注文エンドポイントが異なる。
# pybotters-wrapperではデフォルトは新規注文用の"/private/v1/order"エンドポイント、
# close=Trueフラグを与えると、一括決済用の"/private/v1/closeBulkOrder"エンドポイントを
# 叩きにいく。ここでは逆サイドの建玉を持っていれば後者を用いるようにしている。
exit_side = "BUY" if side == "SELL" else "SELL"
close = store.position.size(exit_side) > 0

...

resp_order = await api.limit_order(symbol, side, price, size, close=close)
```