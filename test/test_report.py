from datetime import date
from datetime import timedelta

from mpr.report import lm_hg201


def test_report():
    assert str(lm_hg201) == 'lm_hg201'


def test_section():
    assert str(lm_hg201.Section.BARROWS_AND_GILTS) == 'Barrows/Gilts'
    assert lm_hg201.Section.BARROWS_AND_GILTS == 'Barrows/Gilts'

    sections = {'Barrows/Gilts': 123}
    assert sections[lm_hg201.Section.BARROWS_AND_GILTS] == 123

    sections[lm_hg201.Section.BARROWS_AND_GILTS] = 456
    assert sections['Barrows/Gilts'] == 456


def test_release():
    assert lm_hg201.released(date(2019, 1, 1)) is True
    assert lm_hg201.released(date.today() + timedelta(days=1)) is False
