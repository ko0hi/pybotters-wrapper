import csv
import io
import os
from datetime import datetime

from ._base import DataStoreWatchWriter, DataStoreWaitWriter
from ...common import DataStoreWrapper


class _CSVWriter:
    def __init__(self, path: str, per_day: bool, columns: list[str] = None):
        self._path = path
        self._columns = columns
        self._filename = os.path.basename(self._path)
        self._filepath = os.path.dirname(self._path)
        self._per_day = per_day
        self._f: io.TextIOWrapper = None
        self._writer: csv.DictWriter = None

    def _write(self, d: dict):
        self._writer.writerow(d)

    def set_columns(self, columns: list[str]):
        self._columns = columns

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
        if self._columns is None:
            raise RuntimeError(f"`_columns` has not been initialized yet.")
        self._f = open(filepath, "w")
        self._writer = csv.DictWriter(self._f, fieldnames=self._columns)
        self._writer.writeheader()


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
        self._writer: _CSVWriter = _CSVWriter(path, per_day)

    def on_watch_before(self, change: "StoreChange"):
        super().on_watch_before(change)
        if self._writer._columns is None:
            self._writer.set_columns(self._columns)
        self._writer._init_or_update_writer()

    def _write(self, d: dict):
        self._writer._write(d)


class DataStoreWaitCSVWriter(DataStoreWaitWriter):
    def __init__(
        self,
        store: DataStoreWrapper,
        store_name: str,
        path: str,
        *,
        per_day: bool = False,
        columns: list[str] = None,
    ):
        super(DataStoreWaitCSVWriter, self).__init__(store, store_name, columns=columns)
        self._writer: _CSVWriter = _CSVWriter(path, per_day)

    def on_wait_before(self):
        super().on_wait_before()
        if self._writer._columns is None:
            self._writer.set_columns(self._columns)
        self._writer._init_or_update_writer()

    def _write(self, d: dict):
        self._writer._write(d)
