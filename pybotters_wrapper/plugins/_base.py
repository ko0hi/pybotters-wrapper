from __future__ import annotations

import asyncio

from loguru import logger
from pybotters.store import DataStore, StoreChange


def _is_aw(fn):
    return asyncio.iscoroutinefunction(fn)


@logger.catch
async def _run_hook(is_aw: bool, fn, *args):
    if is_aw:
        return await fn(*args)
    else:
        return fn(*args)


class Plugin:
    def __init__(self):
        self._queues = []

    def register_queue(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._queues.append(q)
        return q


class DataStorePlugin(Plugin):
    def __init__(self, store: DataStore):
        super(DataStorePlugin, self).__init__()
        self._store = store
        self._wait_task = asyncio.create_task(self._run_wait_task())
        self._watch_task = asyncio.create_task(self._run_watch_task())

    def __del__(self):
        self.stop()

    async def _run_wait_task(self):
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
        is_aw_on_before = _is_aw(self._on_watch_before)
        is_aw_on_transform = _is_aw(self._on_watch_transform)
        is_aw_on_watch = _is_aw(self._on_watch)
        is_aw_on_after = _is_aw(self._on_watch_after)
        is_aw_on_is_stop = _is_aw(self._on_watch_is_stop)
        with self._store.watch() as stream:
            async for change in stream:
                await _run_hook(is_aw_on_before, self._on_watch_before, change)

                transformed = await _run_hook(
                    is_aw_on_transform,
                    self._on_watch_transform,
                    {**change.data},
                    change.operation,
                )

                await _run_hook(
                    is_aw_on_watch, self._on_watch, transformed, change.operation
                )

                await _run_hook(
                    is_aw_on_after, self._on_watch_after, transformed, change.operation
                )

                is_stop = await _run_hook(
                    is_aw_on_is_stop,
                    self._on_watch_is_stop,
                    transformed,
                    change.operation,
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

    def _on_watch(self, d: dict, op: str):
        ...

    def _on_watch_before(self, change: "StoreChange"):
        ...

    def _on_watch_transform(self, d: dict, op: str) -> dict:
        return d

    def _on_watch_is_stop(self, d: dict, op: str) -> bool:
        return False

    def _on_watch_after(self, d: dict, op: str):
        ...

    def stop(self):
        self._wait_task.cancel()
        self._watch_task.cancel()


class MultipleDataStoresPlugin(Plugin):
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
                self._watch_queue.put_nowait((store, change))

    async def _run_wait_task(self):
        self._wait_tasks = [
            asyncio.create_task(self._run_wait_task_one(s)) for s in self._stores
        ]
        is_aw_on_before = _is_aw(self._on_wait_before)
        is_aw_on_wait = _is_aw(self._on_wait)
        is_aw_on_after = _is_aw(self._on_wait_after)
        is_aw_on_is_stop = _is_aw(self._on_wait_is_stop)
        while True:
            await _run_hook(is_aw_on_before, self._on_wait_before)
            store = await self._wait_queue.get()
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
            store, change = await self._watch_queue.get()
            await _run_hook(is_aw_on_before, self._on_watch_before, change, store)

            transformed = await _run_hook(
                is_aw_on_transform,
                self._on_watch_transform,
                {**change.data},
                change.operation,
                store,
            )

            await _run_hook(
                is_aw_on_watch, self._on_watch, transformed, change.operation, store
            )

            await _run_hook(
                is_aw_on_after,
                self._on_watch_after,
                transformed,
                change.operation,
                store,
            )

            is_stop = await _run_hook(
                is_aw_on_is_stop,
                self._on_watch_is_stop,
                transformed,
                change.operation,
                store,
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

    def _on_watch(self, d: dict, op: str, store: "DataStore"):
        ...

    def _on_watch_before(
            self,
            change: "StoreChange",
            store: "DataStore",
    ):
        ...

    def _on_watch_transform(self, d: dict, op: str, store: "DataStore") -> dict:
        return d

    def _on_watch_is_stop(self, d: dict, op: str, store: "DataStore") -> bool:
        return False

    def _on_watch_after(self, d: dict, op: str, store: "DataStore"):
        ...

    def stop(self):
        self._wait_task.cancel()
        self._watch_task.cancel()
        [t.cancel() for t in self._wait_tasks]
        [t.cancel() for t in self._watch_tasks]
