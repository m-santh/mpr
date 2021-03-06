import json
from datetime import date
from io import BytesIO
from os import environ
from typing import AsyncContextManager
from typing import Iterator
from typing import Tuple
from typing import TypeVar
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from aiohttp import ClientSession
from aiohttp import TCPConnector

from . import Record
from .report import Report

T = TypeVar('T')
ParsedElement = Tuple[str, Element]

date_format = "%m-%d-%Y"


def report_url(report: Report) -> str:
    host = environ.get('MPR_SERVER', 'https://mpr.datamart.ams.usda.gov')
    return f'{host}/ws/report/v1/hogs/{report}'


def date_filter(start: date, end: date) -> str:
    return json.dumps({
        'fieldName': 'Report date',
        'operatorType': 'BETWEEN',
        'values': [
            start.strftime(date_format),
            end.strftime(date_format)
        ]
    })


def request_url(report: Report, start: date, end: date) -> str:
    return f'{report_url(report)}?filter={{"filters":[{date_filter(start, end)}]}}'


def parse_elements(elements: Iterator[ParsedElement], min_depth=1, max_depth=4) -> Iterator[Record]:
    """
    Parses a USDA report by saving metadata from parent elements to a dictionary while traversing down the tree.
    When at the maximum depth, yield all collected metadata with each child element's attributes.

    Typical layout of a USDA report:
     <results exportTime>
        <report label slug>
            <record report_date reported_for_date>
                <report label>
                    <record ...attributes/>

    Usually all we care about is the report date (depth=2); the report section label (depth=3);
    and the record data attributes (depth=4).
    """
    depth = 0
    metadata: Record = dict()

    for event, element in elements:
        if event == 'start':
            if min_depth <= depth < max_depth:
                # Parsing a parent element: merge its properties into the metadata
                metadata.update(element.items())

            elif depth == max_depth:
                # Parsing a child element: generate a dict combining metadata and child attributes
                yield dict(metadata.items() | element.items())

            depth += 1

        if event == 'end':
            depth -= 1

            if depth == min_depth:
                # clear the metadata and element tree after each report section
                element.clear()
                metadata.clear()


class Client(AsyncContextManager['Client']):
    report: Report
    session: ClientSession

    def __init__(self, report: Report):
        self.report = report

    async def __aenter__(self) -> 'Client':
        self.session = ClientSession(connector=TCPConnector(limit_per_host=4))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def fetch(self, start: date, end: date) -> Iterator[Record]:
        url = request_url(self.report, start, end)

        async with self.session.get(url) as response:
            data = BytesIO(await response.read())
            elements = ElementTree.iterparse(data, events=['start', 'end'])
            return parse_elements(elements)
