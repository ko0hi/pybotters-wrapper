# Higetori Bot

```bash

python main.py \
    --api YOUR_API_KEY_JSON \
    --exchange bybitusdt \
    --symbol BTCUSDT \
    --size 0.001 \
    --side BUY \
    --limit_distance 0.002 \
    --update_distance 0.0005 \
    --update_patience_seconds 15 \
    --take_profit_distance 0.002 \
    --stop_loss_distance 0.001
```

上のコンフィグ

- 最終価格から0.2%離れたところにヒゲとり指値を出す
- 設定価格と現在の注文価格の誤差が0.05%を超えたら指値を出し直す
- 指値更新前に15秒待機
- 利確0.2%・損切0.1%をトリガーにして、成行でエグジット


複数コンフィグで複数指値を出す

```bash
python main.py \
    --api YOUR_API_KEY_JSON \
    --exchange bybitusdt \
    --symbol BTCUSDT \
    --size 0.001 \
    --config config.json
```

