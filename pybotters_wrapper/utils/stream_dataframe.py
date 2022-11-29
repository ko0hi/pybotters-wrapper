from __future__ import annotations

import pandas as pd


class StreamDataFrame:
    def __init__(self, maxlen, columns, df=None, callback=None, dtypes=None):
        self._df = pd.DataFrame({c: [None] * maxlen for c in columns})
        self._maxlen = maxlen

        if df is not None:
            self.init(df)

        if dtypes is not None:
            self._df = self._df.astype(dtypes)

        self._ = {}
        if callback is None:
            self._callback = []
        else:
            self._callback = callback
        assert isinstance(self._callback, list)

        if df is not None:
            self.__apply_callback()

    def __repr__(self):
        return self._df.__repr__()

    def __getitem__(self, *args):
        return self._df.__getitem__(*args)

    def __len__(self):
        return self._df.__len__()

    def init(self, df):
        if df.shape[0] < self._df.shape[0]:
            self._df.iloc[-df.shape[0] :] = df
        else:
            self._df = df
        self.__prune()

    def append(self, d: dict):
        self._df = self._df.shift(-1)
        self._df.iloc[-1] = [d[c] for c in self._df.columns]
        self.__apply_callback()

    def concat(self, df, overwrite_by_index=True):

        if overwrite_by_index:
            lhs = self._df[~self._df.index.isin(df.index)]
        else:
            lhs = self._df

        self._df = pd.concat([lhs, df], axis=0)
        self.__prune()
        self.__apply_callback()

    def __prune(self):
        if self._df.shape[0] > self._maxlen:
            self._df = self._df.iloc[-self._maxlen :]

    def __apply_callback(self):
        for cb in self._callback:
            self._.update(cb(self.df))

    @property
    def df(self):
        return self._df

    @property
    def columns(self):
        return self._df.columns

    @property
    def loc(self):
        return self._df.loc

    @property
    def iloc(self):
        return self._df.iloc
