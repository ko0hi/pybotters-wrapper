from __future__ import annotations

import asyncio

from pybotters_wrapper.plugins import DataStorePlugin


class ExecutionWatcher(DataStorePlugin):
    def __init__(self, store: "DataStoreManagerWrapper"):
        super(ExecutionWatcher, self).__init__(store.execution)
        self._order_id = None
        self._item = None
        self._done = None
        self._event = asyncio.Event()

    def set(self, order_id: str) -> ExecutionWatcher:
        if self._order_id is not None:
            raise RuntimeError(
                f"ExecutionWatcher must not be 'reused', create a new instance instead."
            )
        self._order_id = order_id
        self._event.set()
        return self

    async def on_watch(self, d: dict, op: str):
        if not self._event.is_set():
            # order_idがsetされるまで待機
            # 注文が即約定した時にsocket messageがresのresponseより早く到達するケースがあるので、
            # order_idがセットされるまでメッセージをここで待機させておく
            await self._event.wait()

        if d["id"] == self._order_id:
            self._done = True
            self._item = d

    def on_watch_is_stop(self, d: dict, op: str) -> bool:
        return self._done

    def done(self):
        return self._done

    def result(self):
        return self._item

    async def wait(self):
        return await self._watch_task

    @property
    def order_id(self):
        return self._order_id
