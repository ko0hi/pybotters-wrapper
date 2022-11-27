class ExchangeMixin:
    _NAME = None

    @property
    def exchange(self) -> str:
        if self._NAME is None:
            raise RuntimeError("_EXCHANGE_NAME has not been set")
        return self._NAME
