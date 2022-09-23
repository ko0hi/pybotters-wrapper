import pandas as pd

from pybotters_wrapper.phemex import PhemexDataStoreWrapper
from pybotters_wrapper.plugins import TimeBarStreamDataFrame


def _transform_for_bar(d: dict, op: str):
    d["timestamp"] = pd.to_datetime(d["timestamp"], utc=True, unit="ns")
    d["volume"] = float(d["size"])
    d["side"] = d["side"].upper()
    return d


def timebar(
    store: PhemexDataStoreWrapper,
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
