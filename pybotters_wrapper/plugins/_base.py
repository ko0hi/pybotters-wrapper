from typing import Generic, NamedTuple, TypeVar

import asyncio

from pybotters.store import Item, DataStore, StoreChange



class DataStorePlugin:
    def __init__(self, store: DataStore):
        self._store = store
        self._wait_task = asyncio.create_task(self._run_wait_task())
        self._watch_task = asyncio.create_task(self._run_watch_task())

    async def _run_wait_task(self):
        while True:
            await self._store.wait()

    async def _run_watch_task(self):
        with self._store.watch() as stream:
            async for change in stream:
                self._on_watch(change)

    def on_wait(self):
        ...

    def _on_watch(self, change: StoreChange):
        transformed_data = self.on_watch_transform({**change.data}, change.operation)
        self.on_watch(transformed_data, change.operation)

    def on_watch(self, d: dict, op: str):
        ...

    def on_watch_transform(self, d: dict, op: str) -> dict:
        return d


class MultipleDataStoresPlugin:
    def __init__(self, *stores: DataStore):
        self._stores = stores
        self._wait_queue = asyncio.Queue()
        self._watch_queue = asyncio.Queue()
        self._wait_task = asyncio.create_task(self._run_wait_task())
        self._watch_task = asyncio.create_task(self._run_watch_task())

    async def _run_wait_task_one(self, store: 'DataStore'):
        while True:
            await store.wait()
            self._wait_queue.put_nowait(store)

    async def _run_watch_task_one(self, store: 'DataStore'):
        with store.watch() as stream:
            async for change in stream:
                self._watch_queue.put_nowait((store, change))

    async def _run_wait_task(self):
        [asyncio.create_task(self._run_wait_task_one(s)) for s in self._stores]
        while True:
            store = await self._wait_queue.get()
            self.on_wait(store)

    async def _run_watch_task(self):
        [asyncio.create_task(self._run_watch_task_one(s)) for s in self._stores]
        while True:
            store, change = await self._watch_queue.get()
            self._on_watch(store, change)

    def on_wait(self, store: 'DataStore'):
        ...

    def _on_watch(self, store, change: StoreChange):
        transformed_data = self.on_watch_transform(
            store, {**change.data}, change.operation
        )
        self.on_watch(store, transformed_data, change.operation)

    def on_watch(self, store: 'DataStore', d: dict, op: str):
        ...

    def on_watch_transform(self, store: 'DataStore', d: dict, op: str) -> dict:
        return d

