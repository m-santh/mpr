from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import Iterator
from typing import TypeVar

from tables import Atom
from tables import Table
from tables.tableextension import Row

T = TypeVar('T', bound=Model)


class Model(ABC):
    @staticmethod
    @property
    @abstractmethod
    def table() -> Table:
        raise NotImplementedError

    @staticmethod
    @property
    @abstractmethod
    def schema() -> Dict[str, Atom]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_row(cls, row: Row) -> T:
        raise NotImplementedError

    @classmethod
    def get(cls) -> Iterator[T]:
        return map(cls.from_row, cls.table.iterrows())

    @classmethod
    def query(cls, condition: str, params: Dict) -> Iterator[T]:
        return map(cls.from_row, cls.table.where(condition, params))

    @classmethod
    def insert(cls, records: Iterator[T]):
        for record in records:
            record.append()

        cls.commit()

    @classmethod
    def commit(cls):
        cls.table.flush()

    @abstractmethod
    def append(self):
        raise NotImplementedError