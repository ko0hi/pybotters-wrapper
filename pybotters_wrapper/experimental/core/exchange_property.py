from abc import ABCMeta


class ExchangeProperty(metaclass=ABCMeta):
    @property
    def exchange(self) -> str:
        raise NotImplementedError
