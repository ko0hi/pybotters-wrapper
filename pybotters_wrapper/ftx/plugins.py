import pandas as pd

from pybotters_wrapper.ftx import FTXDataStoreWrapper
from pybotters_wrapper.plugins import TimeBarStreamDataFrame


def _transform_for_bar(d: dict, op: str):
    d["volume"] = d["size"]
    d["side"] = d["side"].upper()
    d["timestamp"] = pd.to_datetime(d["time"], utc=True)
    return d


def timebar(
    store: FTXDataStoreWrapper,
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
