# Breakout bot

```bash
python main.py \
  --api YOUR_API_KEY_JSON \
  --exchange bitflyer \
  --symbol FX_BTC_JPY  \
  --size 0.01 \
  --bar_seconds 5 \
  --trigger_period 10 \
  --take_profit 0.005 \
  --stop_loss 0.005
```

- ５秒足直近10分のhigh/lowの最大・最小価格をトリガーに設定
- エントリー価格+0.5%で利確
- エントリー価格-0.5%で損切
