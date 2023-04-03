from abc import ABCMeta


class ExchangeProperty(metaclass=ABCMeta):
    @property
    def base_url(self) -> str:
        raise NotImplementedError

    @property
    def exchange(self) -> str:
        raise NotImplementedError
