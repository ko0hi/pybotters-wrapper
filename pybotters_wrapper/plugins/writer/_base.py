from __future__ import annotations

from datetime import datetime

from ...core import DataStoreWrapper
from .._base import DataStorePlugin


class WriterMixin:
    def _write(self, *args, **kwargs):
        raise NotImplementedError


class DataStoreWatchWriter(DataStorePlugin, WriterMixin):
    """単一のデータストアのwatchで流れてくるアイテムをcsvに書き出すプラグイン"""

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
        self._operations = operations or ("insert",)

    def _write(self, d: dict):
        raise NotImplementedError

    def _on_watch_before(self, change: "StoreChange"):
        # カラムの指定がなければアイテムの全ての要素をカラムに設定
        if self._columns is None:
            self._columns = list(change.data.keys())

    def _on_watch_transform(self, store: "DataStore", operation: str, source: dict, data: dict) -> dict:
        return self._transform_item(data)

    async def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        if operation in self._operations:
            self._write(data)

    def _transform_item(self, d: dict) -> dict:
        return {k: d[k] for k in self._columns}


class DataStoreWaitWriter(DataStorePlugin, WriterMixin):
    """単一のデータストアのwait時にアイテムをcsvに書き出すプラグイン"""

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

    def _on_wait_before(self):
        if self._columns is None:
            items = self._store.find()
            if len(items):
                self._columns = list(items[0].keys())
                # 書き出し時刻カラムを追加する
                self._columns = ["wrote_at"] + self._columns

    async def _on_wait(self):
        # 書き出し時刻
        wrote_at = datetime.utcnow()
        for d in self._store.find():
            transformed = self._transform_item({**d})
            transformed = {"wrote_at": wrote_at, **transformed}
            self._write(transformed)

    def _transform_item(self, d: dict):
        return {k: d[k] for k in self._columns if k != "wrote_at"}
