from __future__ import annotations

from datetime import datetime

from ...core import DataStoreWrapper
from .._base import Plugin
from ..mixins import WaitStoreMixin, WatchStoreMixin, WriterMixin


class DataStoreWatchWriter(WatchStoreMixin, WriterMixin, Plugin):
    """単一のデータストアのwatchで流れてくるアイテムを書き出すプラグイン"""

    def __init__(
        self,
        store: "DataStoreWrapper",
        store_name: str,
        *,
        fields: list[str] = None,
        operations: list[str] = None,
    ):
        self._operations = operations or ("insert",)
        self._fields = fields
        self.init_watch_store(getattr(store, store_name))

    def write(self, data: dict):
        raise NotImplementedError

    def _on_watch_first(self, store: "DataStore", operation: str, source: dict, data: dict):
        # カラムの指定がなければアイテムの全ての要素をカラムに設定
        if self._fields is None:
            self._fields = list(data.keys())

    async def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        if operation in self._operations:
            self.write(self._transform_data(data))

    def _transform_data(self, data: dict) -> dict:
        return {k: data[k] for k in self._fields}


class DataStoreWaitWriter(WaitStoreMixin, WriterMixin, Plugin):
    """単一のデータストアのwait時にアイテムをcsvに書き出すプラグイン"""

    def __init__(
        self,
        store: "DataStoreWrapper",
        store_name: str,
        *,
        fields: list[str] = None,
    ):
        self._fields = fields
        self.init_wait_store(getattr(store, store_name))

    def write(self, data: dict):
        raise NotImplementedError

    def _on_wait_first(self):
        if self._fields is None:
            items = self.wait_store.find()
            if len(items):
                self._fields = list(items[0].keys())
                # 書き出し時刻カラムを追加する
                self._fields = ["wrote_at"] + self._fields

    async def _on_wait(self):
        # 書き出し時刻
        wrote_at = datetime.utcnow()
        for d in self.wait_store.find():
            transformed = self._transform_item({**d})
            transformed = {"wrote_at": wrote_at, **transformed}
            self.write(transformed)

    def _transform_item(self, data: dict):
        return {k: data[k] for k in self._fields if k != "wrote_at"}
