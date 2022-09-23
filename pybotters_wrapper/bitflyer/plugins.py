import pandas as pd

import pybotters
from pybotters.models.bitflyer import Board
from pybotters.store import StoreChange

from pybotters_wrapper.bitflyer import BitflyerDataStoreWrapper
from pybotters_wrapper.plugins import TimeBarStreamDataFrame, Book



def timebar(
    store: BitflyerDataStoreWrapper,
    seconds,
    maxlen=9999,
    df=None,
    callback=None,
    message_delay=2,
):
    class _BitflyerTimebarStreamDataFrame(TimeBarStreamDataFrame):
        def _transform(self, d: dict, op: str, **kwargs) -> dict:
            d["timestamp"] = pd.to_datetime(d["exec_date"]).floor("10ms")
            d["volume"] = d["size"]
            return d

    return _BitflyerTimebarStreamDataFrame(
        store.store.executions, seconds, maxlen, df, callback, message_delay
    )


def book(
    symbol: str,
    store: BitflyerDataStoreWrapper,
    min_key: int = 0,
    max_key: int = 10000000,
    pips: int = 1,
    precision: int = 10,
):
    class _BitflyerBook(Book[Board]):
        async def initialize(self, client: pybotters.Client, **kwargs):
            await self.store.wait()
            for i in self.store.find():
                self._update(StoreChange("insert", i))

        def _transform(self, d: dict, op: str) -> dict:
            d["mid"] = self.store.mid_price[symbol]
            d["side"] = "ask" if d["side"] == "SELL" else "bid"
            return d

    return _BitflyerBook(store.board, min_key, max_key, pips, precision)

