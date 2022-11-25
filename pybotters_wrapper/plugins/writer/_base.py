from __future__ import annotations

from datetime import datetime

from .._base import DataStorePlugin
from ...common import DataStoreWrapper


class WriterMixin:
    def _write(self, *args, **kwargs):
        raise NotImplementedError


class DataStoreWatchWriter(DataStorePlugin, WriterMixin):
    def __init__(
            self,
            store: "DataStoreWrapper",
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

    def _transform_item(self, d: dict):
        return {k: d[k] for k in self._columns}

    def _on_watch_before(self, change: "StoreChange"):
        if self._columns is None:
            self._columns = list(change.data.keys())

    def _on_watch_transform(self, d: dict, op: str) -> dict:
        return self._transform_item(d)

    async def _on_watch(self, d: dict, op: str):
        if op in self._operations:
            self._write(d)


class DataStoreWaitWriter(DataStorePlugin, WriterMixin):
    def __init__(
            self,
            store: "DataStoreWrapper",
            store_name: str,
            *,
            columns: list[str] = None,
    ):
        super(DataStoreWaitWriter, self).__init__(getattr(store, store_name))
        self._columns = columns

    def _write(self, d: dict):
        raise NotImplementedError

    def _transform_item(self, d: dict):
        return {k: d[k] for k in self._columns if k != "wrote_at"}

    def _on_wait_before(self):
        if self._columns is None:
            items = self._store.find()
            if len(items):
                self._columns = list(items[0].keys())
                self._columns = ["wrote_at"] + self._columns

    async def _on_wait(self):
        wrote_at = datetime.utcnow()
        for d in self._store.find():
            transformed = self._transform_item({**d})
            transformed = {"wrote_at": wrote_at, **transformed}
            self._write(transformed)
