import csv
import io
import os
from datetime import datetime
from pybotters.store import DataStore, Item
from pybotters_wrapper.common import DataStoreWrapper
from ._base import DataStorePlugin


class WriterMixin:
    def _write(self, *args, **kwargs):
        raise NotImplementedError


class DataStoreWatchWriter(DataStorePlugin, WriterMixin):
    def __init__(
        self,
        store: "DataStore",
        store_name: str,
        *,
        columns: list[str] = None,
        operations: list[str] = None,
    ):
        super(DataStoreWatchWriter, self).__init__(getattr(store, store_name))
        self._columns = columns
        self._operations = operations or ["insert"]

    def _write(self, d: dict):
        raise NotImplementedError

    def on_watch_before(self, change: "StoreChange"):
        if self._columns is None:
            self._columns = list(change.data.keys())

    def on_watch_transform(self, d: dict, op: str) -> dict:
        return {k: d[k] for k in self._columns}

    async def on_watch(self, d: dict, op: str):
        if op in self._operations:
            self._write(d)


class DataStoreWatchCSVWriter(DataStoreWatchWriter):
    def __init__(
        self,
        store: DataStoreWrapper,
        store_name: str,
        path: str,
        *,
        per_day: bool = False,
        columns: list[str] = None,
        operations: list[str] = None,
    ):
        super(DataStoreWatchCSVWriter, self).__init__(
            store, store_name, columns=columns, operations=operations
        )
        self._path = path
        self._filename = os.path.basename(self._path)
        self._filepath = os.path.dirname(self._path)
        self._per_day = per_day
        self._f: io.TextIOWrapper = None
        self._writer: csv.DictWriter = None

    def on_watch_before(self, change: "StoreChange"):
        super().on_watch_before(change)
        self._init_or_update_writer()

    def _write(self, item: dict):
        self._writer.writerow(item)

    def _get_filepath(self):
        if self._per_day:
            day = datetime.utcnow().strftime("%Y-%m-%d")
            return os.path.join(self._filepath, f"{day}-{self._filename}")
        else:
            return self._path

    def _init_or_update_writer(self):
        filepath = self._get_filepath()

        if self._writer is None:
            self._init_writer(filepath)

        elif filepath != self._f.name:
            self._f.close()
            self._init_writer(filepath)

    def _init_writer(self, filepath: str):
        self._f = open(filepath, "w")
        self._writer = csv.DictWriter(self._f, fieldnames=self._columns)
        self._writer.writeheader()
