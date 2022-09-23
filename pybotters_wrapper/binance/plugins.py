import pandas as pd

from pybotters_wrapper.binance import BinanceDataStoreWrapper
from pybotters_wrapper.plugins import TimeBarStreamDataFrame


def timebar(
    store: BinanceDataStoreWrapper,
    seconds,
    maxlen=9999,
    df=None,
    callback=None,
    message_delay=2,
):
    class _BinanceTimeBarStreamDataFrame(TimeBarStreamDataFrame):
        def _transform(self, d: dict, op: str) -> dict:
            d["price"] = float(d["p"])
            d["volume"] = float(d["q"])
            d["side"] = "SELL" if d["m"] else "BUY"
            d["timestamp"] = pd.to_datetime(d["T"], unit="ms", utc=True)
            return d

    return _BinanceTimeBarStreamDataFrame(
        store.store.trade, seconds, maxlen, df, callback, message_delay
    )
