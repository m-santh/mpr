from typing import Optional
from tables import Node
from tables import Group

from mpr.data import db
from mpr.data.db.model.purchase import Purchase


def create() -> Group:
    group = db.connection.create_group(
        where='/mpr',
        name='lm_hg203',
        title='Daily Direct Hog - Afternoon')

    barrows_gilts_table = db.connection.create_table(
        where=group,
        name='barrows_gilts',
        schema=Purchase.schema)

    barrows_gilts_table.cols.date.create_csindex()

    return group


def get(table: Optional[str] = None) -> Node:
    group = db.connection.get_node('/mpr', 'lm_hg203') if '/mpr/lm_hg203' in db.connection else create()
    return group if table is None else group[table]


class barrows_gilts(Purchase):
    table = get('barrows_gilts')