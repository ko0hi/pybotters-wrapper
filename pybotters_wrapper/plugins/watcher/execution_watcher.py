from __future__ import annotations

import asyncio

from ...core.store import DataStoreWrapper, ExecutionItem
from .._base import DataStorePlugin


class ExecutionWatcher(DataStorePlugin):
    def __init__(self, store: "DataStoreWrapper"):
        # ExecutionDataStoreを監視
        super(ExecutionWatcher, self).__init__(store.execution)
        self._order_id = None
        self._item = None
        self._done = None
        self._event = asyncio.Event()

    def set(self, order_id: str) -> ExecutionWatcher:
        """監視対象の注文IDをセット"""
        if self._order_id is not None:
            raise RuntimeError(
                "ExecutionWatcher must not be 'reused', create a new instance instead."
            )
        self._order_id = order_id
        self._event.set()
        return self

    async def _on_watch(self, store, operation: str, source, data: ExecutionItem):
        """流れてきた約定情報が監視中の注文に関するものであるかをチェック

        ExecutionStoreを監視してるので、流れてくるdictはExecutionItem

        """
        if not self._event.is_set():
            # order_idがsetされるまで待機
            # 注文が即約定した時にsocket messageがresのresponseより早く到達するケースがあるので、
            # order_idがセットされるまでメッセージをここで待機させておく
            await self._event.wait()

        if data["id"] == self._order_id:
            self._done = True
            self._item = data

    def _on_watch_is_stop(self, store: "DataStore", operation: str, source: dict, data: dict) -> bool:
        """監視終了判定
        """
        return self._done

    def done(self) -> bool:
        return self._done

    def result(self) -> ExecutionItem:
        return self._item

    async def wait(self):
        return await self._watch_task

    @property
    def order_id(self) -> str:
        return self._order_id
