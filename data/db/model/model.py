from abc import ABC, abstractmethod
from datetime import date
from typing import Tuple, List, Dict, Iterator

import numpy as np
from tables import Table, Atom
from tables.tableextension import Row

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
  def get(cls) -> 'Iterator[Model]':
    return map(cls.from_row, cls.table.iterrows())

  @classmethod
  def query(cls, condition: str, params: Dict) -> 'Iterator[Model]':
    return map(cls.from_row, cls.table.where(condition, params))

  @classmethod
  def insert(cls, records: 'Iterator[Model]'):
    table = cls.table

    for record in records:
      record.append()

    table.flush()

  @classmethod
  @abstractmethod
  def from_row(cls, row: Row) -> 'Model':
    raise NotImplementedError

  @abstractmethod
  def append(self):
    raise NotImplementedError

  @classmethod
  def commit(cls):
    cls.table.flush()

class Observation(Model):
  @classmethod
  def get(cls) -> 'Iterator[Observation]':
    return map(cls.from_row, cls.table.itersorted())

  @classmethod
  def get_date(cls, observation_date: date) -> 'Iterator[Observation]':
    return super(Observation, cls).query("""date == observation_date""", {
      'observation_date': observation_date
    })

  @classmethod
  def get_range(cls, start: date, end = date.today()) -> 'Iterator[Observation]':
    return super(Observation, cls).query("""(start <= date) & (date <= end)""", {
      'start': start.toordinal(),
      'end': end.toordinal()
    })

  @classmethod
  def get_recent(cls, days: int) -> 'Iterator[Observation]':
    today = date.today()
    start = np.busday_offset(today, -days).astype('O')

    return cls.get_range(start, today)

  @classmethod
  def get_year(cls, year: int) -> 'Iterator[Observation]':
    return cls.get_range(date(year, 1, 1), date(year, 12, 31))

  @classmethod
  def first(cls) -> 'Observation':
    cls.table[cls.table.colindexes['date'][0]]

  @classmethod
  def last(cls) -> 'Observation':
    cls.table[cls.table.colindexes['date'][-1]]

  @classmethod
  def dates(cls) -> Iterator[date]:
    return map(date.fromordinal, set(cls.table.cols.date[:]))

  @classmethod
  def extent(cls) -> Tuple[date, date]:
    table = cls.table
    date_column = table.cols.date
    date_index = table.colindexes['date']

    first = date.fromordinal(date_column[date_index[0]])
    last = datea.fromordinal(date_column[date_index[-1]])

    return (first, last)
