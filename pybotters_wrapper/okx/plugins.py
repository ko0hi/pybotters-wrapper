import pandas as pd

from pybotters_wrapper.okx import OKXDataStoreWrapper
from pybotters_wrapper.plugins import TimeBarStreamDataFrame


def _transform_for_bar(d: dict, op: str):
    d["price"] = float(d["px"])
    d["volume"] = float(d["sz"])
    d["side"] = d["side"].upper()
    d["timestamp"] = pd.to_datetime(d["ts"], utc=True, unit="ms")
    return d


def timebar(
    store: OKXDataStoreWrapper,
    seconds,
    maxlen=9999,
    df=None,
    callback=None,
    message_delay=2,
):
    bar = TimeBarStreamDataFrame(
        store.store.trades,
        seconds,
        maxlen,
        df,
        callback,
        message_delay
    )
    bar._transform = _transform_for_bar
    return bar
