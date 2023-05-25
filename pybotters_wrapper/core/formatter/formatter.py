from abc import ABCMeta, abstractmethod


class Formatter(metaclass=ABCMeta):
    @abstractmethod
    def format(self, *args, **kwargs) -> any:
        raise NotImplementedError
