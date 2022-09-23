from pybotters_wrapper.bitget import BitgetDataStoreWrapper
from pybotters_wrapper.plugins import TimeBarStreamDataFrame

import pandas as pd


def _transform_for_bar(d: dict, op: str, **kwargs) -> dict:
    d["price"] = float(d["px"])
    d["timestamp"] = pd.to_datetime(d["ts"], utc=True)
    d["volume"] = d["sz"]
    d["side"] = d["side"].upper()
    return d


def timebar(
    store: BitgetDataStoreWrapper,
    seconds,
    maxlen=9999,
    df=None,
    callback=None,
    message_delay=2,
):
    bar = TimeBarStreamDataFrame(
        store.store.trade,
        seconds,
        maxlen,
        df,
        callback,
        message_delay
    )
    bar._transform = _transform_for_bar
    return bar