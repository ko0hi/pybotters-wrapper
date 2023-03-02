from __future__ import annotations

import asyncio
import csv
import io
import os
from datetime import datetime

from ...core import DataStoreWrapper
from .._base import Plugin
from ..market.bar import BarStreamDataFrame
from ._base import DataStoreWaitWriter, DataStoreWatchWriter, WriterMixin

from ..mixins import CSVWriterMixin


class _CSVWriter:
    def __init__(
            self, path: str, per_day: bool, columns: list[str] = None,
            flush: bool = False
    ):
        self._path = path
        self._columns = columns
        self._filename = os.path.basename(self._path)
        self._filepath = os.path.dirname(self._path)
        self._per_day = per_day
        self._f: io.TextIOWrapper = None
        self._writer: csv.DictWriter = None
        self._flush = flush

    def _write(self, d: dict):
        self._writer.writerow(d)
        if self._flush:
            self._f.flush()

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
        self._f = open(filepath, "w")
        self._writer = csv.DictWriter(self._f, fieldnames=self._columns)
        if self._columns is not None:
            self._writer.writeheader()


class DataStoreWatchCSVWriter(CSVWriterMixin, DataStoreWatchWriter):
    def __init__(
            self,
            store: DataStoreWrapper,
            store_name: str,
            path: str,
            *,
            per_day: bool = False,
            columns: list[str] = None,
            flush: bool = False,
            operations: list[str] = None,
    ):
        super(DataStoreWatchCSVWriter, self).__init__(
            store, store_name, operations=operations
        )
        self.init_csv_writer(path, per_day, columns, flush)

    def _on_watch_first(self, store: "DataStore", operation: str, source: dict, data: dict):
        super()._on_watch_first(store, operation, source, data)
        if self.get_columns() is None:
            self.set_columns(self._fields)
        self.new_writer()

    async def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        await super()._on_watch(store, operation, source, data)
        # 日付が変わっていた場合writerを更新
        self.new_or_update_writer()


class DataStoreWaitCSVWriter(CSVWriterMixin, DataStoreWaitWriter):
    def __init__(
            self,
            store: DataStoreWrapper,
            store_name: str,
            path: str,
            *,
            per_day: bool = False,
            columns: list[str] = None,
            flush: bool = False,
    ):
        if columns is not None and "wrote_at" not in columns:
            columns.append("wrote_at")

        super(DataStoreWaitCSVWriter, self).__init__(store, store_name, fields=columns)
        self.init_csv_writer(path, per_day, columns, flush)

    def _on_wait_first(self):
        super()._on_wait_first()
        if self.get_columns() is None:
            self.set_columns(self._fields)
        self.new_writer()

    async def _on_wait(self):
        await super()._on_wait()
        self.new_or_update_writer()


class BarCSVWriter(Plugin, WriterMixin):
    def __init__(
            self,
            bar: BarStreamDataFrame,
            path: str,
            *,
            per_day: bool = False,
            flush: bool = False,
    ):
        super(BarCSVWriter)
        self._bar = bar
        self._writer: _CSVWriter = _CSVWriter(path, per_day, self._bar.COLUMNS, flush)
        self._queue = self._bar.register_queue()
        self._task = asyncio.create_task(self._auto_write())

    async def _auto_write(self):
        while True:
            df = await self._queue.get()
            self._writer._init_or_update_writer()
            self._writer._write(df.iloc[-1].to_dict())
