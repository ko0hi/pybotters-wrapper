from pybotters_wrapper.plugins import DataStorePlugin


class ExecutionWatcher(DataStorePlugin):
    def __init__(self, store: 'DataStoreManagerWrapper'):
        super(ExecutionWatcher, self).__init__(store.execution)
        self._order_id = None
        self._item = None
        self._done = None

    async def _run_wait_task(self):
        ...

    async def _run_watch_task(self):
        with self._store.watch() as stream:
            async for change in stream:
                if change.data["id"] == self._order_id:
                    self._done = True
                    self._item = change.data
                    break

    def set_order_id(self, order_id: str):
        self._order_id = order_id

    def _on_watch(self, change: 'StoreChange'):
        if change.data["id"] == self._order_id:
            self._done = True
            self._item = change.data
            self.stop()

    def done(self):
        return self._done

    def result(self):
        return self._item

    async def wait(self):
        return await self._watch_task

    @property
    def order_id(self):
        return self._order_id

