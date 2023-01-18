from __future__ import annotations

import asyncio
from typing import Callable

from loguru import logger
from pybotters.store import DataStore, StoreChange


def _is_aw(fn: Callable) -> bool:
    return asyncio.iscoroutinefunction(fn)


@logger.catch
async def _run_hook(is_aw: bool, fn: Callable, *args) -> any:
    if is_aw:
        return await fn(*args)
    else:
        return fn(*args)


class Plugin:
    def __init__(self):
        self._queues: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._queues.append(q)
        return q

    def register_queue(self) -> asyncio.Queue:
        # TODO: duplicated. use subscribe instead.
        q = asyncio.Queue()
        self._queues.append(q)
        return q

    def put(self, item: any):
        for q in self._queues:
            q.put_nowait(item)


class DataStorePlugin(Plugin):
    """単一のDataStoreを用いるプラグイン"""

    def __init__(self, store: DataStore):
        super(DataStorePlugin, self).__init__()
        self._store = store
        self._wait_task = asyncio.create_task(self._run_wait_task())
        self._watch_task = asyncio.create_task(self._run_watch_task())

    def __del__(self):
        # インスタンス破棄時に監視タスクをキャンセルする
        self.stop()

    async def _run_wait_task(self):
        """wait監視"""
        is_aw_on_before = _is_aw(self._on_wait_before)
        is_aw_on_wait = _is_aw(self._on_wait)
        is_aw_on_after = _is_aw(self._on_wait_after)
        is_aw_on_is_stop = _is_aw(self._on_wait_is_stop)
        while True:
            await self._store.wait()
            await _run_hook(is_aw_on_before, self._on_wait_before)
            await _run_hook(is_aw_on_wait, self._on_wait)
            await _run_hook(is_aw_on_after, self._on_wait_after)
            is_stop = await _run_hook(is_aw_on_is_stop, self._on_wait_is_stop)
            if is_stop:
                break

    async def _run_watch_task(self):
        """watch監視"""
        is_aw_on_before = _is_aw(self._on_watch_before)
        is_aw_on_transform = _is_aw(self._on_watch_transform)
        is_aw_on_watch = _is_aw(self._on_watch)
        is_aw_on_after = _is_aw(self._on_watch_after)
        is_aw_on_is_stop = _is_aw(self._on_watch_is_stop)
        with self._store.watch() as stream:
            async for change in stream:
                await _run_hook(is_aw_on_before, self._on_watch_before, change)

                # watchはアイテム変換用のhookがある
                transformed = await _run_hook(
                    is_aw_on_transform,
                    self._on_watch_transform,
                    change.store,
                    change.operation,
                    change.source,
                    change.data,
                )

                await _run_hook(
                    is_aw_on_watch,
                    self._on_watch,
                    change.store,
                    change.operation,
                    change.source,
                    transformed,
                )

                await _run_hook(
                    is_aw_on_after,
                    self._on_watch_after,
                    change.store,
                    change.operation,
                    change.source,
                    transformed,
                )

                is_stop = await _run_hook(
                    is_aw_on_is_stop,
                    self._on_watch_is_stop,
                    change.store,
                    change.operation,
                    change.source,
                    transformed,
                )

                if is_stop:
                    break

    def _on_wait(self):
        ...

    def _on_wait_before(self):
        ...

    def _on_wait_after(self):
        ...

    def _on_wait_is_stop(self) -> bool:
        return False

    def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        ...

    def _on_watch_before(self, change: "StoreChange"):
        ...

    def _on_watch_transform(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> dict:
        return data

    def _on_watch_is_stop(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> bool:
        return False

    def _on_watch_after(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ):
        ...

    def stop(self):
        self._wait_task.cancel()
        self._watch_task.cancel()


class MultipleDataStoresPlugin(Plugin):
    """複数のDataStoreを用いるプラグイン"""

    def __init__(self, *stores: DataStore):
        super(MultipleDataStoresPlugin, self).__init__()
        self._stores = stores
        self._wait_queue = asyncio.Queue()
        self._watch_queue = asyncio.Queue()
        self._wait_task = asyncio.create_task(self._run_wait_task())
        self._watch_task = asyncio.create_task(self._run_watch_task())
        self._wait_tasks = None
        self._watch_tasks = None

    def __del__(self):
        self.stop()

    async def _run_wait_task_one(self, store: "DataStore"):
        while True:
            await store.wait()
            self._wait_queue.put_nowait(store)

    async def _run_watch_task_one(self, store: "DataStore"):
        with store.watch() as stream:
            async for change in stream:
                self._watch_queue.put_nowait(change)

    async def _run_wait_task(self):
        # 使用するDataStoreのwaitをそれぞれ監視してキューで結果を取得する
        self._wait_tasks = [
            asyncio.create_task(self._run_wait_task_one(s)) for s in self._stores
        ]
        is_aw_on_before = _is_aw(self._on_wait_before)
        is_aw_on_wait = _is_aw(self._on_wait)
        is_aw_on_after = _is_aw(self._on_wait_after)
        is_aw_on_is_stop = _is_aw(self._on_wait_is_stop)
        while True:
            store = await self._wait_queue.get()
            await _run_hook(is_aw_on_before, self._on_wait_before)
            await _run_hook(is_aw_on_wait, self._on_wait, store)
            await _run_hook(is_aw_on_after, self._on_wait_after, store)
            is_stop = await _run_hook(is_aw_on_is_stop, self._on_wait_is_stop, store)
            if is_stop:
                break

    async def _run_watch_task(self):
        self._watch_tasks = [
            asyncio.create_task(self._run_watch_task_one(s)) for s in self._stores
        ]
        is_aw_on_before = _is_aw(self._on_watch_before)
        is_aw_on_transform = _is_aw(self._on_watch_transform)
        is_aw_on_watch = _is_aw(self._on_watch)
        is_aw_on_after = _is_aw(self._on_watch_after)
        is_aw_on_is_stop = _is_aw(self._on_watch_is_stop)
        while True:
            change = await self._watch_queue.get()
            await _run_hook(is_aw_on_before, self._on_watch_before, change)

            transformed = await _run_hook(
                is_aw_on_transform,
                self._on_watch_transform,
                change.store,
                change.operation,
                change.source,
                change.data,
            )

            await _run_hook(
                is_aw_on_watch,
                self._on_watch,
                change.store,
                change.operation,
                change.source,
                transformed,
            )

            await _run_hook(
                is_aw_on_after,
                self._on_watch_after,
                change.store,
                change.operation,
                change.source,
                transformed,
            )

            is_stop = await _run_hook(
                is_aw_on_is_stop,
                self._on_watch_is_stop,
                change.store,
                change.operation,
                change.source,
                transformed,
            )

            if is_stop:
                break

    def _on_wait(self, store: "DataStore"):
        ...

    def _on_wait_before(self):
        ...

    def _on_wait_after(self, store: "DataStore"):
        ...

    def _on_wait_is_stop(self, store: "DataStore") -> bool:
        return False

    def _on_watch(self, store: "DataStore", operation: str, source: dict, data: dict):
        ...

    def _on_watch_before(self, change: "StoreChange"):
        ...

    def _on_watch_transform(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ) -> dict:
        return data

    def _on_watch_is_stop(
        self, store: "DataStore", operation: str, source, data: dict
    ) -> bool:
        return False

    def _on_watch_after(
        self, store: "DataStore", operation: str, source: dict, data: dict
    ):
        ...

    def stop(self):
        self._wait_task.cancel()
        self._watch_task.cancel()
        [t.cancel() for t in self._wait_tasks]
        [t.cancel() for t in self._watch_tasks]
