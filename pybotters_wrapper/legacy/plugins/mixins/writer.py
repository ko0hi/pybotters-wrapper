import csv
import io
import os
from datetime import datetime

from .helper import generate_attribute_checker


class WriterMixin:
    def write(self, *args, **kwargs):
        raise NotImplementedError


class CSVWriterMixin(WriterMixin):
    __path: str
    __columns: list[str]
    __filename: str
    __filepath: str
    __per_day: bool
    __flush: bool
    __f: io.TextIOWrapper
    __writer: csv.DictWriter

    __checker = generate_attribute_checker("init_csv_writer",
                                           "_CSVWriterMixin__f")

    def __del__(self):
        if self.__f:
            self.__f.close()

    def init_csv_writer(
            self, path: str, per_day: bool, columns: list[str] = None,
            flush: bool = False
    ):
        self.__path = path
        self.__columns = columns
        self.__filename = os.path.basename(self.__path)
        self.__filepath = os.path.dirname(self.__path)
        self.__per_day = per_day
        self.__flush = flush
        self.__f: io.TextIOWrapper = None
        self.__writer: csv.DictWriter = None

    @__checker
    def write(self, d: dict):
        self.__writer.writerow(d)
        if self.__flush:
            self.__f.flush()

    @__checker
    def get_columns(self) -> list[str]:
        return self.__columns

    @__checker
    def set_columns(self, columns: list[str]):
        self.__columns = columns

    @__checker
    def get_filepath(self):
        if self.__per_day:
            day = datetime.utcnow().strftime("%Y-%m-%d")
            return os.path.join(self.__filepath, f"{day}-{self.__filename}")
        else:
            return self.__path

    @__checker
    def new_or_update_writer(self):
        filepath = self.get_filepath()

        if self.__writer is None:
            self.new_writer(filepath)

        elif filepath != self.__f.name:
            self.__f.close()
            self.new_writer(filepath)

    @__checker
    def new_writer(self, filepath: str = None):
        filepath = filepath or self.get_filepath()
        assert self.__columns is not None, "Missing columns"
        self.__f = open(filepath, "w", newline="")
        self.__writer = csv.DictWriter(self.__f, fieldnames=self.__columns)
        self.__writer.writeheader()
