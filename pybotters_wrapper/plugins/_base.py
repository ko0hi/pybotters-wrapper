from typing import Generic, TypeVar

import asyncio

from pybotters.store import DataStore, StoreChange


T = TypeVar('T', bound=DataStore)


class WatchPlugin(Generic[T]):
    def __init__(self, store: T):
        self._store = store
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        with self._store.watch() as stream:
            async for msg in stream:
                self._update(msg)

    def update(self, d: dict, op: str, **kwargs):
        raise NotImplementedError

    def _update(self, item: 'StoreChange'):
        # inplaceで変えないようにcopyする
        d = self._transform({**item.data}, item.operation)
        return self.update(d, item.operation)

    def _transform(self, d: dict, op: str) -> dict:
        pass

    def cancel(self):
        return self._task.cancel()

    @property
    def store(self) -> T:
        return self._store

    @property
    def task(self):
        return self._task
