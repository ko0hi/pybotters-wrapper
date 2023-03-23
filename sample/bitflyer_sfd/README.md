雑なbitflyer sfdぼっと。


以下の環境変数を設定。
```
PYBOTTERS_APIS=YOUR_APIS_JSON_PATH
```


```bash
# 数量: 0.1
# 売り指値：5.1%
# 買い指値：4.9%
# 指値更新幅：0.05%
python main.py --size 0.01 --sell_spread 0.051 --buy_spread 0.49 --cancel_gap 0.0005
```