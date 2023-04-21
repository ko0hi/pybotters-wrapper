from __future__ import annotations

from collections import defaultdict

import numpy as np


class BinBucket:
    def __init__(self, min_key: int, max_key: int, pips: int = 1, precision: int = 10):
        self._rng = max_key - min_key
        assert self._rng % pips == 0
        self._min_key = min_key
        self._max_key = max_key
        self._pips = pips
        self._bucket_num = int(self._rng / pips)
        self._values = np.zeros(self._bucket_num)
        self._keys = np.arange(self._min_key, self._max_key, self._pips)
        self._memo = defaultdict(float)
        self._precision = precision

    def bucketize(self, value: int, pips: int = None, return_label: bool = False):
        pips = pips or self._pips
        index = int((value - self._min_key) / pips)
        # TODO: bucketの拡張
        assert 0 <= index < self._bucket_num, f"Out-of-index: {value}"
        return self._keys[index] if return_label else index

    def insert(self, key: int, value: int):
        index = self.bucketize(key)
        new_size = np.around(
            self._values[index] + value - self._memo[key], self._precision
        )
        self._values[index] = new_size
        self._memo[key] = value

    def delete(self, key: int, value: int):
        index = self.bucketize(key)
        self._values[index] = np.around(self._values[index] - value, self._precision)
        self._memo[key] = 0

    def _non_zero_indices(self):
        return self._values != 0

    def non_zeros(self):
        indices = self._non_zero_indices()
        return self._values[indices], self._keys[indices]

    def size(self):
        return self._bucket_num

    def get(self, i: int):
        try:
            return self._values[i]
        except IndexError:
            i = self.bucketize(i)
            return self._values[i]

    def keys(self):
        return self._keys

    def values(self):
        return self._values

    def reset(self):
        self._values = np.zeros(self._bucket_num)
        self._memo = defaultdict(float)

    @property
    def pips(self):
        return self._pips
