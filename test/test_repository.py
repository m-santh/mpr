from datetime import date
from pathlib import Path

from isoweek import Week
from pytest import fixture

from mpr.report import CutoutReport
from mpr.repository import Repository

week = Week.withdate(date(2019, 8, 20))


@fixture
def repository(tmp_path: Path):
    repository = Repository(tmp_path, CutoutReport.LM_PK602)

    repository.save(week, {
        CutoutReport.Section.CUTOUT: [{
            'report_date': '08/20/2018',
            'pork_carcass': '67.18',
            'pork_loin': '75.51',
            'pork_butt': '89.55',
            'pork_picnic': '41.82',
            'pork_rib': '113.95',
            'pork_ham': '57.52',
            'pork_belly': '77.77'
        }],
        CutoutReport.Section.VOLUME: [{
            'report_date': '08/20/2018',
            'temp_cuts_total_load': '334.74',
            'temp_process_total_load': '39.61'
        }]
    })

    return repository


async def test_get_full_report(repository: Repository):
    report = await repository.get(week)

    cutout = report[CutoutReport.Section.CUTOUT]
    assert len(cutout) == 1

    volume = report[CutoutReport.Section.VOLUME]
    assert len(volume) == 1


async def test_get_report_section(repository: Repository):
    cutout = await repository.get(week, CutoutReport.Section.CUTOUT)
    assert len(cutout) == 1
