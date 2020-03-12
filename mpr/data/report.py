from datetime import date
from datetime import datetime
from datetime import timedelta

from enum import Enum
from typing import Tuple
from typing import TypeVar

from dateutil.tz import gettz

Record = TypeVar('Record', bound=Tuple)


class Section(str, Enum):
    def __str__(self):
        return self.value


class Report:
    slug: str
    description: str
    hour: int

    def __init__(self, slug: str, description: str, hour: int):
        self.slug = slug
        self.description = description
        self.hour = hour

    def __str__(self):
        return self.slug


class DailyReport(Report):
    @property
    def latest(self) -> date:
        now = datetime.now(tz=gettz('America/Chicago'))
        release = now.replace(hour=self.hour, minute=0, second=0, microsecond=0)
        return now.date() if now > release else (now - timedelta(days=1)).date()