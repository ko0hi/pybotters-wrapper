# pybotters-wrapper

![test](https://github.com/ko0hi/pybotters-wrapper/actions/workflows/test.yml/badge.svg)

A high-level api collection for pybotters

## Requires

python 3.11 or higher

## Install

```bash
pip install git+https://github.com/ko0hi/pybotters-wrapper
```

## Usage

Coming soon ...

## Features

- DataStore周りの取引所間差分吸収
- 注文APIの取引所間差分吸収
- プラグインによる拡張性の提供

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
